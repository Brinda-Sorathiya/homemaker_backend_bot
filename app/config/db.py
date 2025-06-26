import os
import asyncpg
import asyncio
import logging
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
pool = None
_db_lock = asyncio.Lock()  # prevent race condition in Vercel

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

async def connect_to_db():
    global pool
    try:
        if not DATABASE_URL:
            raise ValueError("DATABASE_URL is not set in the environment.")
        
        if pool is None:
            pool = await asyncpg.create_pool(DATABASE_URL)
            logger.info("Connected to the PostgreSQL database.")
    except (asyncpg.PostgresError, ValueError) as e:
        logger.error(f"Database connection failed: {e}")
        raise
    except Exception as e:
        logger.exception("Unexpected error during DB connection:")
        raise

async def get_conn():
    global pool
    if pool is None:
        async with _db_lock:
            if pool is None:  # double check in case other coroutine already created it
                logger.info("Lazy DB pool initialization triggered.")
                await connect_to_db()
    return pool

async def close_db_connection():
    global pool
    try:
        if pool:
            await pool.close()
            logger.info("PostgreSQL connection pool closed.")
    except Exception as e:
        logger.warning(f"Error while closing DB pool: {e}")

async def get_table_info() -> str:
    pool = await get_conn()

    query = """
    SELECT
        table_name,
        column_name,
        data_type
    FROM
        information_schema.columns
    WHERE
        table_schema = 'public'
    ORDER BY
        table_name, ordinal_position;
    """

    async with pool.acquire() as conn:
        rows = await conn.fetch(query)

    table_dict = {}
    for row in rows:
        table = row["table_name"]
        column = f"{row['column_name']} {row['data_type']}"
        if table not in table_dict:
            table_dict[table] = []
        table_dict[table].append(column)

    table_info = ""
    for table, columns in table_dict.items():
        table_info += f"{table}({', '.join(columns)})\n"

    return table_info.strip()