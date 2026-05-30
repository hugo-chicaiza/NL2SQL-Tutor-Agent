import asyncio
from app.db.database import AsyncSessionLocal
from app.services.nl2sql_service import NL2SQLService


async def main():

    async with AsyncSessionLocal() as session:

        service = NL2SQLService(session)

        question = """
        How can you produce a list of all members who have used a tennis court? 
        Include in your output the name of the court, and the name of the member
         formatted as a single column. Ensure no duplicate data, and order by the 
         member name followed by the facility name.
        """

        response = await service.run(question)

        print("\nSQL:\n", response.sql)
        print("\nEXPLANATION:\n", response.explanation)

        for r in (response.rows or [])[:20]:
            print(r)


if __name__ == "__main__":
    asyncio.run(main())