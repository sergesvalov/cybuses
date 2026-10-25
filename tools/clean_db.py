import asyncio
from database import AsyncSessionLocal
from sqlalchemy import text

async def main():
    async with AsyncSessionLocal() as session:
        # Delete dummy directions with "Сбой загрузки расписания"
        await session.execute(text("DELETE FROM departures WHERE direction_id IN (SELECT id FROM directions WHERE description LIKE '%Сбой загрузки%')"))
        await session.execute(text("DELETE FROM directions WHERE description LIKE '%Сбой загрузки%'"))
        
        # OSYPA had an error character: 
        await session.execute(text("DELETE FROM departures WHERE direction_id IN (SELECT id FROM directions WHERE description LIKE '%%')"))
        await session.execute(text("DELETE FROM directions WHERE description LIKE '%%'"))
        
        await session.commit()
        print("Database cleaned.")

if __name__ == "__main__":
    asyncio.run(main())
