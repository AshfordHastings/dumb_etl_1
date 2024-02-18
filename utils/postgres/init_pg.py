import sqlalchemy 
from sqlalchemy import text


engine = sqlalchemy.create_engine('postgresql://postgres:postgres@localhost:5432/postgres', echo=True)

def create_table():
    stmt = """
    CREATE TABLE IF NOT EXISTS user_info (
        id integer PRIMARY KEY,
        first_name TEXT,
        last_name TEXT,
        gender TEXT,
        address TEXT,
        post_code TEXT,
        email TEXT,
        username TEXT,
        registered_date TEXT,
        phone TEXT
        );
    """

    with engine.connect() as conn:
        conn.execute(text(stmt))

if __name__ == "__main__":
    create_table()
    print("Postgres setup completed!")

