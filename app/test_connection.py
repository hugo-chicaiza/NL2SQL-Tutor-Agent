from sqlalchemy import text
from app.db.database import engine


def test_connection():
    with engine.connect() as conn:
        result = conn.execute(text("SELECT NOW();"))

        for row in result:
            print(row)


if __name__ == "__main__":
    test_connection()   