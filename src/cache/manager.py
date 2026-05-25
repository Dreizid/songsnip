from collections.abc import Iterator
from contextlib import contextmanager
import sqlite3
from src.config.paths import CACHE_ROOT
from src.cache.schema import LYRIC_SCHEMA


class DatabaseManager:
    def __init__(self, db_name: str = "lyricutils_cache.db") -> None:
        self.db_path = CACHE_ROOT / db_name
        CACHE_ROOT.mkdir(parents=True, exist_ok=True)
        print(CACHE_ROOT)
        self._init_db()

    def _init_db(self) -> None:
        with self.get_connection() as conn:
            for statement in LYRIC_SCHEMA:
                conn.execute(statement)

    @contextmanager
    def get_connection(self) -> Iterator[sqlite3.Connection]:
        """Returns an sqlite3 connection with Row factory enabled"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        try:
            with conn:
                yield conn
        finally:
            conn.close()
