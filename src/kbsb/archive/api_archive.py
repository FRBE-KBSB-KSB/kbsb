import os
import sqlite3
import logging
import psycopg
from pathlib import Path
from fastapi import APIRouter, HTTPException, Query
from reddevil.core import get_secret, get_settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/archive", tags=["archive"])

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
            pg_config = get_secret("postgres")
            dsn = f"host={pg_config['dbhost']} port={pg_config.get('dbport', 5432)} dbname={pg_config['dbname']} user={pg_config['dbuser']} password={pg_config['dbpassword']}"
            conn = psycopg.connect(dsn)
            return conn, "postgres"
        except Exception as e:
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
    except Exception as e:
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
            SELECT p.member_id, p.name, p.gender, p.birthdate, p.nationality, p.club_id,
                   (SELECT pr.rating FROM player_ratings pr WHERE pr.member_id = p.member_id ORDER BY pr.period DESC LIMIT 1) as latest_elo
            FROM players p
            WHERE p.name ILIKE %s OR CAST(p.member_id AS TEXT) LIKE %s 
            ORDER BY p.name ASC 
            LIMIT 50
        """
        sql_lite = """
            SELECT p.member_id, p.name, p.gender, p.birthdate, p.nationality, p.club_id,
                   (SELECT pr.rating FROM player_ratings pr WHERE pr.member_id = p.member_id ORDER BY pr.period DESC LIMIT 1) as latest_elo
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
            SELECT club_id, name, abbreviation, federation 
            FROM clubs 
            WHERE name ILIKE %s OR CAST(club_id AS TEXT) LIKE %s 
            ORDER BY club_id ASC 
            LIMIT 50
        """
        sql_lite = """
            SELECT club_id, name, abbreviation, federation 
            FROM clubs 
            WHERE name LIKE ? OR CAST(club_id AS TEXT) LIKE ? 
            ORDER BY club_id ASC 
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
            SELECT p.member_id, p.name, p.gender, p.birthdate, p.nationality, p.club_id,
                   (SELECT pr.rating FROM player_ratings pr WHERE pr.member_id = p.member_id ORDER BY pr.period DESC LIMIT 1) as latest_elo
            FROM players p
            WHERE p.club_id = %s AND p.license_year >= 2026
            ORDER BY latest_elo DESC NULLS LAST, p.name ASC
        """
        sql_lite = """
            SELECT p.member_id, p.name, p.gender, p.birthdate, p.nationality, p.club_id,
                   (SELECT pr.rating FROM player_ratings pr WHERE pr.member_id = p.member_id ORDER BY pr.period DESC LIMIT 1) as latest_elo
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
        sql_pg = "SELECT member_id, name, gender, birthdate, nationality FROM players WHERE member_id = %s"
        sql_lite = "SELECT member_id, name, gender, birthdate, nationality FROM players WHERE member_id = ?"
        
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
            SELECT period, opponent_member_id, opponent_name, tournament, result, color, date 
            FROM player_games 
            WHERE member_id = %s 
            ORDER BY date DESC, period DESC, id DESC
            LIMIT 100
        """
        sql_games_lite = """
            SELECT period, opponent_member_id, opponent_name, tournament, result, color, date 
            FROM player_games 
            WHERE member_id = ? 
            ORDER BY date DESC, period DESC, id DESC
            LIMIT 100
        """
        games = run_query(conn, db_type, sql_games_pg, sql_games_lite, (member_id,))
        
        return {
            "success": True,
            "player": player,
            "ratings": ratings,
            "games": games
        }
    finally:
        conn.close()

@router.get("/player/{member_id}/games")
async def get_player_games(member_id: int, period: str = None):
    conn, db_type = get_archive_connection()
    try:
        if period:
            sql_pg = """
                SELECT period, opponent_member_id, opponent_name, tournament, result, color, date 
                FROM player_games 
                WHERE member_id = %s AND period = %s
                ORDER BY date DESC, id DESC
            """
            sql_lite = """
                SELECT period, opponent_member_id, opponent_name, tournament, result, color, date 
                FROM player_games 
                WHERE member_id = ? AND period = ?
                ORDER BY date DESC, id DESC
            """
            params = (member_id, period)
        else:
            sql_pg = """
                SELECT period, opponent_member_id, opponent_name, tournament, result, color, date 
                FROM player_games 
                WHERE member_id = %s
                ORDER BY date DESC, period DESC, id DESC
            """
            sql_lite = """
                SELECT period, opponent_member_id, opponent_name, tournament, result, color, date 
                FROM player_games 
                WHERE member_id = ?
                ORDER BY date DESC, period DESC, id DESC
            """
            params = (member_id,)
            
        games = run_query(conn, db_type, sql_pg, sql_lite, params)
        return {"success": True, "games": games}
    finally:
        conn.close()
