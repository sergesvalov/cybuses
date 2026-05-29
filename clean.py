import asyncio
from database import AsyncSessionLocal
from sqlalchemy import text

async def main():
    async with AsyncSessionLocal() as session:
        result = await session.execute(text("SELECT id, description FROM directions"))
        for row in result.fetchall():
            if "Сбой загрузки" in row.description or "\ufffd" in row.description:
                print(f"Deleting direction {row.id}: {row.description}")
                await session.execute(text(f"DELETE FROM departures WHERE direction_id = {row.id}"))
                await session.execute(text(f"DELETE FROM directions WHERE id = {row.id}"))
        await session.commit()
        print("Database cleaned.")

if __name__ == "__main__":
    asyncio.run(main())
