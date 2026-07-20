import os
import sqlite3
import logging
import unicodedata
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

def clean_birthdate(player_dict):
    if "birthdate" in player_dict and player_dict["birthdate"]:
        bd = player_dict["birthdate"]
        if hasattr(bd, "year"):
            player_dict["birthdate"] = str(bd.year)
        else:
            player_dict["birthdate"] = str(bd)[:4]
    return player_dict

def normalize_name(s):
    if not s:
        return ""
    s = unicodedata.normalize('NFD', s)
    s = "".join([c for c in s if not unicodedata.category(c).startswith('M')])
    s = s.lower()
    s = s.replace("'", "").replace("-", "").replace(" ", "").replace(".", "")
    return s

def levenshtein_distance(s1, s2):
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)
    if len(s2) == 0:
        return len(s1)
    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    return previous_row[-1]

@router.get("/search")
async def search_players(q: str = Query(..., min_length=2), type: str = Query("all"), age_category: str = Query("all")):
    conn, db_type = get_archive_connection()
    try:
        # Fetch all active players from database
        sql_pg = """
            SELECT p.member_id, p.name, p.gender, p.birthdate, p.club_id, p.fide_id,
                   (SELECT pr.rating FROM player_ratings pr WHERE pr.member_id = p.member_id ORDER BY pr.period DESC LIMIT 1) as latest_elo,
                   (SELECT pr.period FROM player_ratings pr WHERE pr.member_id = p.member_id ORDER BY pr.period DESC LIMIT 1) as latest_elo_period
            FROM players p
            WHERE p.license_year >= 2026
        """
        sql_lite = """
            SELECT p.member_id, p.name, p.gender, p.birthdate, p.club_id, p.fide_id,
                   (SELECT pr.rating FROM player_ratings pr WHERE pr.member_id = p.member_id ORDER BY pr.period DESC LIMIT 1) as latest_elo,
                   (SELECT pr.period FROM player_ratings pr WHERE pr.member_id = p.member_id ORDER BY pr.period DESC LIMIT 1) as latest_elo_period
            FROM players p
            WHERE p.license_year >= 2026
        """
        players = run_query(conn, db_type, sql_pg, sql_lite, ())
        
        # Clean birthdates
        for p in players:
            clean_birthdate(p)
            
        # Filter and rank in Python
        from datetime import date
        q_norm = normalize_name(q)
        results = []
        current_year = date.today().year
        
        for p in players:
            # Apply age category filter if active
            if age_category != "all":
                if not p["birthdate"]:
                    continue
                try:
                    byear = int(p["birthdate"])
                    age = current_year - byear
                    if age_category == "youth" and age > 20:
                        continue
                    elif age_category == "senior" and (age < 21 or age > 59):
                        continue
                    elif age_category == "senior_60" and age < 60:
                        continue
                except ValueError:
                    continue

            member_id_str = str(p["member_id"])
            fide_id_str = str(p["fide_id"]) if p["fide_id"] else ""
            name_full = p["name"]
            
            # Extract first and last name for fuzzy matching
            name_parts = name_full.split(",")
            last_name = normalize_name(name_parts[0])
            first_name = normalize_name(name_parts[1]) if len(name_parts) > 1 else ""
            # Names are stored "Last, First" but users search in either order,
            # so match against both concatenations.
            if first_name:
                name_variants = {last_name + first_name, first_name + last_name}
            else:
                name_variants = {last_name}

            def best_name_score(q):
                best = None
                for variant in name_variants:
                    if q in variant:
                        s = len(variant) - len(q)
                        if best is None or s < best:
                            best = s
                return best

            matched = False
            score = 999
            
            if type == "national":
                if q_norm in member_id_str:
                    matched = True
                    score = len(member_id_str) - len(q_norm)
            elif type == "fide":
                if q_norm in fide_id_str:
                    matched = True
                    score = len(fide_id_str) - len(q_norm)
            elif type == "name":
                name_score = best_name_score(q_norm)
                if name_score is not None:
                    matched = True
                    score = name_score
                elif len(q_norm) >= 3:
                    dist = min(
                        levenshtein_distance(q_norm, last_name),
                        levenshtein_distance(q_norm, first_name) if first_name else 999
                    )
                    if dist <= 2:
                        matched = True
                        score = 100 + dist
            else: # "all"
                if q_norm in member_id_str:
                    matched = True
                    score = len(member_id_str) - len(q_norm)
                elif fide_id_str and q_norm in fide_id_str:
                    matched = True
                    score = len(fide_id_str) - len(q_norm)
                elif best_name_score(q_norm) is not None:
                    matched = True
                    score = best_name_score(q_norm)
                elif len(q_norm) >= 3:
                    dist = min(
                        levenshtein_distance(q_norm, last_name),
                        levenshtein_distance(q_norm, first_name) if first_name else 999
                    )
                    if dist <= 2:
                        matched = True
                        score = 100 + dist
            
            if matched:
                results.append((score, p))
                
        # Sort first by match score, then alphabetically
        results.sort(key=lambda x: (x[0], x[1]["name"]))
        final_players = [x[1] for x in results[:50]]
        return {"success": True, "players": final_players}
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

@router.get("/clubs/all")
async def get_all_clubs():
    conn, db_type = get_archive_connection()
    try:
        sql_pg = """
            SELECT c.club_id, c.name, c.abbreviation, c.federation,
                   (SELECT COUNT(*) FROM players p WHERE p.club_id = c.club_id AND p.license_year >= 2026) as player_count
            FROM clubs c
            ORDER BY c.club_id ASC
        """
        sql_lite = """
            SELECT c.club_id, c.name, c.abbreviation, c.federation,
                   (SELECT COUNT(*) FROM players p WHERE p.club_id = c.club_id AND p.license_year >= 2026) as player_count
            FROM clubs c
            ORDER BY c.club_id ASC
        """
        results = run_query(conn, db_type, sql_pg, sql_lite, ())
        return {"success": True, "clubs": results}
    finally:
        conn.close()

@router.get("/club/{club_id}/players")
async def get_club_players(club_id: int):
    conn, db_type = get_archive_connection()
    try:
        sql_pg = """
            SELECT p.member_id, p.name, p.gender, p.birthdate, p.club_id, p.fide_id,
                   (SELECT pr.rating FROM player_ratings pr WHERE pr.member_id = p.member_id ORDER BY pr.period DESC LIMIT 1) as latest_elo,
                   (SELECT pr.period FROM player_ratings pr WHERE pr.member_id = p.member_id ORDER BY pr.period DESC LIMIT 1) as latest_elo_period
            FROM players p
            WHERE p.club_id = %s AND p.license_year >= 2026
            ORDER BY latest_elo DESC NULLS LAST, p.name ASC
        """
        sql_lite = """
            SELECT p.member_id, p.name, p.gender, p.birthdate, p.club_id, p.fide_id,
                   (SELECT pr.rating FROM player_ratings pr WHERE pr.member_id = p.member_id ORDER BY pr.period DESC LIMIT 1) as latest_elo,
                   (SELECT pr.period FROM player_ratings pr WHERE pr.member_id = p.member_id ORDER BY pr.period DESC LIMIT 1) as latest_elo_period
            FROM players p
            WHERE p.club_id = ? AND p.license_year >= 2026
            ORDER BY latest_elo DESC, p.name ASC
        """
        results = run_query(conn, db_type, sql_pg, sql_lite, (club_id,))
        for r in results:
            clean_birthdate(r)
        return {"success": True, "players": results}
    finally:
        conn.close()

@router.get("/player/{member_id}")
async def get_player_profile(member_id: int):
    conn, db_type = get_archive_connection()
    try:
        sql_pg = """
            SELECT p.member_id, p.name, p.gender, p.birthdate, p.club_id, p.fide_id, c.name as club_name 
            FROM players p 
            LEFT JOIN clubs c ON p.club_id = c.club_id 
            WHERE p.member_id = %s
        """
        sql_lite = """
            SELECT p.member_id, p.name, p.gender, p.birthdate, p.club_id, p.fide_id, c.name as club_name 
            FROM players p 
            LEFT JOIN clubs c ON p.club_id = c.club_id 
            WHERE p.member_id = ?
        """
        
        results = run_query(conn, db_type, sql_pg, sql_lite, (member_id,))
        if not results:
            raise HTTPException(status_code=404, detail="Player not found")
            
        player = results[0]
        clean_birthdate(player)
        
        # 1. Fetch ratings history
        sql_ratings_pg = "SELECT period, rating FROM player_ratings WHERE member_id = %s ORDER BY period ASC"
        sql_ratings_lite = "SELECT period, rating FROM player_ratings WHERE member_id = ? ORDER BY period ASC"
        ratings = run_query(conn, db_type, sql_ratings_pg, sql_ratings_lite, (member_id,))
        
        # 2. Fetch full game history
        sql_games_pg = """
            SELECT pg.id, pg.period, pg.opponent_member_id, pg.opponent_name, pg.tournament, pg.result, pg.color, pg.date, pg.opponent_elo, pg.game_number, pg.k_factor, pg.expected_score,
                   (CASE WHEN p.member_id IS NOT NULL THEN 1 ELSE 0 END) as opponent_is_active
            FROM player_games pg
            LEFT JOIN players p ON pg.opponent_member_id = p.member_id
            WHERE pg.member_id = %s
            ORDER BY pg.date DESC, pg.period DESC, pg.id DESC
        """
        sql_games_lite = """
            SELECT pg.id, pg.period, pg.opponent_member_id, pg.opponent_name, pg.tournament, pg.result, pg.color, pg.date, pg.opponent_elo, pg.game_number, pg.k_factor, pg.expected_score,
                   (CASE WHEN p.member_id IS NOT NULL THEN 1 ELSE 0 END) as opponent_is_active
            FROM player_games pg
            LEFT JOIN players p ON pg.opponent_member_id = p.member_id
            WHERE pg.member_id = ?
            ORDER BY pg.date DESC, pg.period DESC, pg.id DESC
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
                SELECT pg.period, pg.opponent_member_id, pg.opponent_name, pg.tournament, pg.result, pg.color, pg.date, pg.opponent_elo,
                       (CASE WHEN p.member_id IS NOT NULL THEN 1 ELSE 0 END) as opponent_is_active
                FROM player_games pg
                LEFT JOIN players p ON pg.opponent_member_id = p.member_id
                WHERE pg.member_id = %s AND pg.period = %s
                ORDER BY pg.date DESC, pg.id DESC
            """
            sql_lite = """
                SELECT pg.period, pg.opponent_member_id, pg.opponent_name, pg.tournament, pg.result, pg.color, pg.date, pg.opponent_elo,
                       (CASE WHEN p.member_id IS NOT NULL THEN 1 ELSE 0 END) as opponent_is_active
                FROM player_games pg
                LEFT JOIN players p ON pg.opponent_member_id = p.member_id
                WHERE pg.member_id = ? AND pg.period = ?
                ORDER BY pg.date DESC, pg.id DESC
            """
            params = (member_id, period)
        else:
            sql_pg = """
                SELECT pg.period, pg.opponent_member_id, pg.opponent_name, pg.tournament, pg.result, pg.color, pg.date, pg.opponent_elo,
                       (CASE WHEN p.member_id IS NOT NULL THEN 1 ELSE 0 END) as opponent_is_active
                FROM player_games pg
                LEFT JOIN players p ON pg.opponent_member_id = p.member_id
                WHERE pg.member_id = %s
                ORDER BY pg.date DESC, pg.period DESC, pg.id DESC
            """
            sql_lite = """
                SELECT pg.period, pg.opponent_member_id, pg.opponent_name, pg.tournament, pg.result, pg.color, pg.date, pg.opponent_elo,
                       (CASE WHEN p.member_id IS NOT NULL THEN 1 ELSE 0 END) as opponent_is_active
                FROM player_games pg
                LEFT JOIN players p ON pg.opponent_member_id = p.member_id
                WHERE pg.member_id = ?
                ORDER BY pg.date DESC, pg.period DESC, pg.id DESC
            """
            params = (member_id,)
            
        games = run_query(conn, db_type, sql_pg, sql_lite, params)
        return {"success": True, "games": games}
    finally:
        conn.close()
