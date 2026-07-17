import os
import sqlite3
import logging
from pathlib import Path
from fastapi import APIRouter, HTTPException, Query
from reddevil.core import get_secret
from psycopg_pool import ConnectionPool

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/national_elo_archive", tags=["national_elo_archive"])

class PooledConnectionWrapper:
    def __init__(self, conn, pool):
        self._conn = conn
        self._pool = pool
        
    def cursor(self, *args, **kwargs):
        return self._conn.cursor(*args, **kwargs)
        
    def close(self):
        if self._pool is not None:
            self._pool.putconn(self._conn)
            self._pool = None
        else:
            self._conn.close()

_pool = None

def get_pool():
    global _pool
    if _pool is not None:
        return _pool
    try:
        pg_config = get_secret("postgres")
        db_host = pg_config.get('dbhost', '')
        if db_host == "oldelo.zerotwo.cloud":
            try:
                import socket
                socket.gethostbyname(db_host)
            except Exception:
                logger.warning("DNS resolution failed for oldelo.zerotwo.cloud, falling back to IP 178.104.142.24")
                db_host = "178.104.142.24"
        
        dsn = f"host={db_host} port={pg_config.get('dbport', 5432)} dbname={pg_config['dbname']} user={pg_config['dbuser']} password={pg_config['dbpassword']}"
        _pool = ConnectionPool(dsn, min_size=1, max_size=10, open=True)
        return _pool
    except Exception as e:
        logger.exception("Failed to initialize PostgreSQL ConnectionPool")
        raise e

def get_archive_connection():
    # If KBSB_MODE is local, fallback to local SQLite database
    if os.environ.get("KBSB_MODE") == "local":
        sqlite_path = Path(__file__).resolve().parent.parent.parent.parent / "scratch" / "test_archive.db"
        if not sqlite_path.exists():
            sqlite_path = Path(r"C:\Users\AuraFlight\.gemini\antigravity\scratch\kbsb\scratch\test_archive.db")
        
        if not sqlite_path.exists():
            logger.error(f"Local SQLite database not found at {sqlite_path}")
            raise HTTPException(status_code=500, detail="Database file missing")
            
        conn = sqlite3.connect(sqlite_path)
        conn.row_factory = sqlite3.Row
        return conn, "sqlite"
    else:
        try:
            pool = get_pool()
            conn = pool.getconn()
            return PooledConnectionWrapper(conn, pool), "postgres"
        except Exception:
            logger.exception("Failed to connect to PostgreSQL")
            raise HTTPException(status_code=500, detail="Database connection failed")

def run_query(conn, db_type, sql_pg, sql_lite, params):
    cursor = conn.cursor()
    try:
        if db_type == "postgres":
            cursor.execute(sql_pg, params)
            columns = [desc[0] for desc in cursor.description]
            results = [dict(zip(columns, row)) for row in cursor.fetchall()]
        else:
            # SQLite uses ? placeholders instead of %s
            cursor.execute(sql_lite, params)
            results = [dict(row) for row in cursor.fetchall()]
        return results
    except Exception:
        logger.exception("Database query execution failed")
        raise HTTPException(status_code=500, detail="Database query error")
    finally:
        cursor.close()

@router.get("/search")
async def search_players(q: str = Query(..., min_length=2)):
    conn, db_type = get_archive_connection()
    try:
        # Search by name or stamnummer
        search_pattern = f"%{q}%"
        sql_pg = """
            SELECT p.member_id, p.name, p.gender, p.birthdate, p.nationality, p.club_id, p.fide_id,
                   (SELECT pr.rating FROM player_ratings pr WHERE pr.member_id = p.member_id ORDER BY pr.period DESC LIMIT 1) as latest_elo,
                   (SELECT pr.period FROM player_ratings pr WHERE pr.member_id = p.member_id ORDER BY pr.period DESC LIMIT 1) as latest_elo_period
            FROM players p
            WHERE p.name ILIKE %s OR CAST(p.member_id AS TEXT) LIKE %s 
            ORDER BY p.name ASC 
            LIMIT 50
        """
        sql_lite = """
            SELECT p.member_id, p.name, p.gender, p.birthdate, p.nationality, p.club_id, p.fide_id,
                   (SELECT pr.rating FROM player_ratings pr WHERE pr.member_id = p.member_id ORDER BY pr.period DESC LIMIT 1) as latest_elo,
                   (SELECT pr.period FROM player_ratings pr WHERE pr.member_id = p.member_id ORDER BY pr.period DESC LIMIT 1) as latest_elo_period
            FROM players p
            WHERE p.name LIKE ? OR CAST(p.member_id AS TEXT) LIKE ? 
            ORDER BY p.name ASC 
            LIMIT 50
        """
        results = run_query(conn, db_type, sql_pg, sql_lite, (search_pattern, search_pattern))
        return {"success": True, "players": results}
    finally:
        conn.close()

@router.get("/clubs")
async def search_clubs(q: str = Query(..., min_length=2)):
    conn, db_type = get_archive_connection()
    try:
        search_pattern = f"%{q}%"
        sql_pg = """
            SELECT c.club_id, c.name, c.abbreviation, c.federation,
                   (SELECT COUNT(*) FROM players p WHERE p.club_id = c.club_id AND p.license_year >= 2026) as player_count
            FROM clubs c
            WHERE c.name ILIKE %s OR CAST(c.club_id AS TEXT) LIKE %s 
            ORDER BY c.club_id ASC 
            LIMIT 50
        """
        sql_lite = """
            SELECT c.club_id, c.name, c.abbreviation, c.federation,
                   (SELECT COUNT(*) FROM players p WHERE p.club_id = c.club_id AND p.license_year >= 2026) as player_count
            FROM clubs c
            WHERE c.name LIKE ? OR CAST(c.club_id AS TEXT) LIKE ? 
            ORDER BY c.club_id ASC 
            LIMIT 50
        """
        results = run_query(conn, db_type, sql_pg, sql_lite, (search_pattern, search_pattern))
        return {"success": True, "clubs": results}
    finally:
        conn.close()

@router.get("/club/{club_id}/players")
async def get_club_players(club_id: int):
    conn, db_type = get_archive_connection()
    try:
        sql_pg = """
            SELECT p.member_id, p.name, p.gender, p.birthdate, p.nationality, p.club_id, p.fide_id,
                   (SELECT pr.rating FROM player_ratings pr WHERE pr.member_id = p.member_id ORDER BY pr.period DESC LIMIT 1) as latest_elo,
                   (SELECT pr.period FROM player_ratings pr WHERE pr.member_id = p.member_id ORDER BY pr.period DESC LIMIT 1) as latest_elo_period
            FROM players p
            WHERE p.club_id = %s AND p.license_year >= 2026
            ORDER BY latest_elo DESC NULLS LAST, p.name ASC
        """
        sql_lite = """
            SELECT p.member_id, p.name, p.gender, p.birthdate, p.nationality, p.club_id, p.fide_id,
                   (SELECT pr.rating FROM player_ratings pr WHERE pr.member_id = p.member_id ORDER BY pr.period DESC LIMIT 1) as latest_elo,
                   (SELECT pr.period FROM player_ratings pr WHERE pr.member_id = p.member_id ORDER BY pr.period DESC LIMIT 1) as latest_elo_period
            FROM players p
            WHERE p.club_id = ? AND p.license_year >= 2026
            ORDER BY latest_elo DESC, p.name ASC
        """
        results = run_query(conn, db_type, sql_pg, sql_lite, (club_id,))
        return {"success": True, "players": results}
    finally:
        conn.close()

@router.get("/player/{member_id}")
async def get_player_profile(member_id: int):
    conn, db_type = get_archive_connection()
    try:
        sql_pg = """
            SELECT p.member_id, p.name, p.gender, p.birthdate, p.nationality, p.club_id, p.fide_id, c.name as club_name 
            FROM players p 
            LEFT JOIN clubs c ON p.club_id = c.club_id 
            WHERE p.member_id = %s
        """
        sql_lite = """
            SELECT p.member_id, p.name, p.gender, p.birthdate, p.nationality, p.club_id, p.fide_id, c.name as club_name 
            FROM players p 
            LEFT JOIN clubs c ON p.club_id = c.club_id 
            WHERE p.member_id = ?
        """
        
        results = run_query(conn, db_type, sql_pg, sql_lite, (member_id,))
        if not results:
            raise HTTPException(status_code=404, detail="Player not found")
            
        player = results[0]
        
        # 1. Fetch ratings history
        sql_ratings_pg = "SELECT period, rating FROM player_ratings WHERE member_id = %s ORDER BY period ASC"
        sql_ratings_lite = "SELECT period, rating FROM player_ratings WHERE member_id = ? ORDER BY period ASC"
        ratings = run_query(conn, db_type, sql_ratings_pg, sql_ratings_lite, (member_id,))
        
        # 2. Fetch game history (limit to last 100 games for performance, full list via separate games query)
        sql_games_pg = """
            SELECT period, opponent_member_id, opponent_name, tournament, result, color, date, opponent_elo, game_number, k_factor, expected_score 
            FROM player_games 
            WHERE member_id = %s 
            ORDER BY date DESC, period DESC, id DESC
            LIMIT 100
        """
        sql_games_lite = """
            SELECT period, opponent_member_id, opponent_name, tournament, result, color, date, opponent_elo, game_number, k_factor, expected_score 
            FROM player_games 
            WHERE member_id = ? 
            ORDER BY date DESC, period DESC, id DESC
            LIMIT 100
        """
        games = run_query(conn, db_type, sql_games_pg, sql_games_lite, (member_id,))
        
        # 3. Fetch summary stats (total games and latest game date)
        sql_stats_pg = "SELECT COUNT(*) as total_games, MAX(date) as latest_game_date FROM player_games WHERE member_id = %s"
        sql_stats_lite = "SELECT COUNT(*) as total_games, MAX(date) as latest_game_date FROM player_games WHERE member_id = ?"
        stats = run_query(conn, db_type, sql_stats_pg, sql_stats_lite, (member_id,))
        
        total_games = stats[0]["total_games"] if stats else 0
        latest_game_date = stats[0]["latest_game_date"] if stats else None
        latest_game_date_str = latest_game_date.isoformat() if latest_game_date else None
        if isinstance(latest_game_date, str):
            latest_game_date_str = latest_game_date
            
        return {
            "success": True,
            "player": player,
            "ratings": ratings,
            "games": games,
            "total_games": total_games,
            "latest_game_date": latest_game_date_str
        }
    finally:
        conn.close()

@router.get("/player/{member_id}/games")
async def get_player_games(member_id: int, period: str = None):
    conn, db_type = get_archive_connection()
    try:
        if period:
            sql_pg = """
                SELECT period, opponent_member_id, opponent_name, tournament, result, color, date, opponent_elo 
                FROM player_games 
                WHERE member_id = %s AND period = %s
                ORDER BY date DESC, id DESC
            """
            sql_lite = """
                SELECT period, opponent_member_id, opponent_name, tournament, result, color, date, opponent_elo 
                FROM player_games 
                WHERE member_id = ? AND period = ?
                ORDER BY date DESC, id DESC
            """
            params = (member_id, period)
        else:
            sql_pg = """
                SELECT period, opponent_member_id, opponent_name, tournament, result, color, date, opponent_elo 
                FROM player_games 
                WHERE member_id = %s
                ORDER BY date DESC, period DESC, id DESC
            """
            sql_lite = """
                SELECT period, opponent_member_id, opponent_name, tournament, result, color, date, opponent_elo 
                FROM player_games 
                WHERE member_id = ?
                ORDER BY date DESC, period DESC, id DESC
            """
            params = (member_id,)
            
        games = run_query(conn, db_type, sql_pg, sql_lite, params)
        return {"success": True, "games": games}
    finally:
        conn.close()
