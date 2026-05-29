import asyncio
import sys
from alembic.config import Config
from alembic import command
from database import engine

async def check_connection():
    try:
        async with engine.connect() as conn:
            return True
    except Exception as e:
        print(f"Database not ready yet, waiting... ({type(e).__name__})")
        return False

async def wait_for_db():
    retries = 15
    while retries > 0:
        if await check_connection():
            print("Database is ready!")
            return
        retries -= 1
        await asyncio.sleep(2)
    print("Could not connect to database after retries.")
    sys.exit(1)

def run_migrations():
    print("Running Alembic migrations...")
    alembic_cfg = Config("alembic.ini")
    command.upgrade(alembic_cfg, "head")
    print("Migrations complete.")

if __name__ == "__main__":
    # Wait for DB in an isolated event loop
    asyncio.run(wait_for_db())
    # Run migrations synchronously (Alembic's env.py manages its own event loop)
    run_migrations()
