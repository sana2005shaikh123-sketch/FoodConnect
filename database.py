import os
import psycopg2


def get_connection():
    return psycopg2.connect(os.getenv("DATABASE_URL"))


def create_table():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS donations (
            id SERIAL PRIMARY KEY,
            hotel TEXT NOT NULL,
            food TEXT NOT NULL,
            quantity TEXT NOT NULL,
            location TEXT NOT NULL,
            contact TEXT NOT NULL
        )
    """)

    connection.commit()
    cursor.close()
    connection.close()