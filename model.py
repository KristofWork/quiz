import sqlite3


class DB:
    def __init__(self, db_path: str) -> None:
        self.connect = sqlite3.connect(db_path)
        self.cursor = self.connect.cursor()

    def is_user_exists(self, chat_id: int) -> bool:
        self.cursor.execute("SELECT chat_id FROM users WHERE chat_id = ?", [chat_id])
        return self.cursor.fetchone() is not None

    def create_user(self, chat_id: int, username: str) -> None:
        self.cursor.execute(
            "INSERT INTO users(chat_id, username) VALUES(?, ?)", [chat_id, username]
        )
        self.connect.commit()

    def create_admin(self, chat_id: int) -> None:
        self.cursor.execute(
            "INSERT INTO admins(chat_id) VALUES(?)", [chat_id]
        )
        self.connect.commit()

    def is_admin(self, chat_id: int) -> bool:
        self.cursor.execute("SELECT chat_id FROM admins WHERE chat_id = ?", [chat_id])
        return self.cursor.fetchone() is not None