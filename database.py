import sqlite3


connection = sqlite3.connect("foodconnect.db")

cursor = connection.cursor()


cursor.execute("""
CREATE TABLE IF NOT EXISTS donations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    hotel TEXT NOT NULL,
    food TEXT NOT NULL,
    quantity TEXT NOT NULL,
    location TEXT NOT NULL,
    contact TEXT NOT NULL
)
""")


connection.commit()

connection.close()

print("FoodConnect database created successfully!")