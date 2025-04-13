import sqlite3

db = sqlite3.connect("quiz.db")
cursor = db.cursor()

cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS users(
        chat_id INTEGER PRIMARY KEY,
        username TEXT,
        points INTEGER DEFAULT 0
    )
    """
)

cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS admins(
        chat_id INTEGER PRIMARY KEY
    )
    """
)

cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS questions(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        q TEXT,
        a1 TEXT,
        a2 TEXT,
        a3 TEXT,
        a4 TEXT,
        right_a_number INTEGER
    )
    """
)

cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS states(
        game_on INTEGER PRIMARY KEY
    )
    """
)

cursor.execute("INSERT INTO states(game_on) VALUES(0)")
db.commit()
