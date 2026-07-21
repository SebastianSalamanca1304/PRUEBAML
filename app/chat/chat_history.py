import sqlite3
from pathlib import Path
from typing import List, Dict, Any


BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "data"
CHAT_DIR = DATA_DIR / "chat_history"
DB_PATH = CHAT_DIR / "chat_history.db"

CHAT_DIR.mkdir(parents=True, exist_ok=True)


class ChatHistoryRepository:
    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = Path(db_path)
        self._init_db()

    def _get_connection(self):
        return sqlite3.connect(self.db_path)

    def _init_db(self):
        with self._get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS chat_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    message TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()

    def save_message(self, session_id: str, role: str, message: str) -> None:
        with self._get_connection() as conn:
            conn.execute("""
                INSERT INTO chat_history (session_id, role, message)
                VALUES (?, ?, ?)
            """, (session_id, role, message))
            conn.commit()

    def get_last_messages(self, session_id: str, limit: int = 6) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.execute("""
                SELECT role, message, created_at
                FROM chat_history
                WHERE session_id = ?
                ORDER BY id DESC
                LIMIT ?
            """, (session_id, limit))

            rows = cursor.fetchall()

        rows.reverse()

        return [
            {
                "role": row[0],
                "message": row[1],
                "created_at": row[2]
            }
            for row in rows
        ]

    def get_full_session(self, session_id: str) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.execute("""
                SELECT role, message, created_at
                FROM chat_history
                WHERE session_id = ?
                ORDER BY id ASC
            """, (session_id,))

            rows = cursor.fetchall()

        return [
            {
                "role": row[0],
                "message": row[1],
                "created_at": row[2]
            }
            for row in rows
        ]

    def list_sessions(self) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.execute("""
                SELECT
                    session_id,
                    COUNT(*) as total_messages,
                    MIN(created_at) as started_at,
                    MAX(created_at) as last_message_at
                FROM chat_history
                GROUP BY session_id
                ORDER BY last_message_at DESC
            """)

            rows = cursor.fetchall()

        return [
            {
                "session_id": row[0],
                "total_messages": row[1],
                "started_at": row[2],
                "last_message_at": row[3]
            }
            for row in rows
        ]

    def delete_session(self, session_id: str) -> int:
        with self._get_connection() as conn:
            cursor = conn.execute("""
                DELETE FROM chat_history
                WHERE session_id = ?
            """, (session_id,))
            conn.commit()
            return cursor.rowcount

    def count_messages(self, session_id: str | None = None) -> int:
        with self._get_connection() as conn:
            if session_id:
                cursor = conn.execute("""
                    SELECT COUNT(*)
                    FROM chat_history
                    WHERE session_id = ?
                """, (session_id,))
            else:
                cursor = conn.execute("""
                    SELECT COUNT(*)
                    FROM chat_history
                """)

            return cursor.fetchone()[0]


if __name__ == "__main__":
    repo = ChatHistoryRepository()

    test_session = "demo-session-001"

    repo.save_message(test_session, "user", "Hola, ¿qué productos ofrece el banco?")
    repo.save_message(test_session, "assistant", "El banco ofrece cuentas, tarjetas y préstamos.")
    repo.save_message(test_session, "user", "¿Y qué opciones hay para personas?")

    print("\n=== ÚLTIMOS MENSAJES ===")
    for msg in repo.get_last_messages(test_session, limit=5):
        print(msg)

    print("\n=== SESIÓN COMPLETA ===")
    for msg in repo.get_full_session(test_session):
        print(msg)

    print("\n=== LISTA DE SESIONES ===")
    for session in repo.list_sessions():
        print(session)

    print("\n=== TOTAL MENSAJES ===")
    print(repo.count_messages())