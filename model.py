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
        self.cursor.execute("INSERT INTO admins(chat_id) VALUES(?)", [chat_id])
        self.connect.commit()

    def is_admin(self, chat_id: int) -> bool:
        self.cursor.execute("SELECT chat_id FROM admins WHERE chat_id = ?", [chat_id])
        return self.cursor.fetchone() is not None

    def change_game_state(self, state: bool) -> None:
        int_state = 1 if state else 0  # Тернарный оператор
        self.cursor.execute("UPDATE states SET game_on = ?", [int_state])
        self.connect.commit()

    def is_game_on(self) -> bool:
        self.cursor.execute("SELECT game_on FROM states")
        result = self.cursor.fetchone()
        if not result:
            return False
        return result[0] == 1

    def get_all_users_id(self) -> list[int]:
        self.cursor.execute("SELECT chat_id FROM users")
        users_id = []
        for users_id_tuple in self.cursor.fetchall():
            users_id.append(users_id_tuple[0])
        return users_id

    def create_question(
        self, q: str, a1: str, a2: str, a3: str, a4: str, correct_a_number: int
    ) -> None:
        self.cursor.execute(
            "INSERT INTO questions(q, a1, a2, a3, a4, right_a_number) VALUES(?, ?, ?, ?, ?, ?)",
            [q, a1, a2, a3, a4, correct_a_number],
        )
        self.connect.commit()

    def get_questions_amount(self) -> int:
        self.cursor.execute("SELECT id FROM questions")
        return len(self.cursor.fetchall())

    def clear_questions(self) -> None:
        self.cursor.execute("DELETE FROM questions")
        self.connect.commit()

    def get_all_questions(self) -> list[tuple]:
        self.cursor.execute("SELECT q, a1, a2, a3, a4, right_a_number FROM questions")
        return self.cursor.fetchall()

    def add_points(self, chat_id: int, points: int) -> None:
        self.cursor.execute(
            "UPDATE users SET points = ? WHERE chat_id = ?", [points, chat_id]
        )
        self.connect.commit()

    def get_all_records(self, max_records: int = 10) -> list[tuple]:
        self.cursor.execute(
            "SELECT chat_id, username, points FROM users ORDER BY points DESC LIMIT ?",
            [max_records],
        )
        return self.cursor.fetchall()

    def clear_records(self):
        self.cursor.execute("UPDATE users SET points = 0")
        self.connect.commit()
