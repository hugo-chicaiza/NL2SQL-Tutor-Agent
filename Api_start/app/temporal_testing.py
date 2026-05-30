import asyncio
from app.db.database import AsyncSessionLocal
from app.services.nl2sql_service import NL2SQLService


async def main():

    async with AsyncSessionLocal() as session:

        service = NL2SQLService(session)

        question = """
        Debes listar usuarios que hayan usado instalaciones de tenis,
        mostrando en una sola columna el nombre del usuario y la instalación.
        Evita duplicados y ordena por usuario y luego instalación.
        """

        response = await service.run(question)

        print("\nSQL:\n", response.sql)
        print("\nEXPLANATION:\n", response.explanation)

        for r in (response.rows or [])[:20]:
            print(r)


if __name__ == "__main__":
    asyncio.run(main())