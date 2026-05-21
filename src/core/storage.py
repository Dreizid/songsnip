import sqlite3
from pathlib import Path
from src.core.schema import LyricsData, TrackMetadata


PROJECT_ROOT = Path(__file__).resolve().parent


class LyricCache:
    def __init__(self, db_name: str = "lyricutils_cache.db") -> None:
        self.db_path = PROJECT_ROOT / db_name
        self._bootstrap()

    def _get_connection(self) -> sqlite3.Connection:
        """Returns an sqlite3 connection with Row factory enabled"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn

    def _bootstrap(self) -> None:
        with self._get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS term_map (
                    term_key TEXT PRIMARY KEY,
                    isrc TEXT NOT NULL
                )
            """)

            conn.execute("""
                CREATE TABLE IF NOT EXISTS tracks (
                    isrc TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    artist TEXT NOT NULL,
                    album TEXT,
                    duration INTEGER,
                    resolver_type TEXT,
                    resolver_id INTEGER
                )
            """)

            conn.execute("""
                CREATE TABLE IF NOT EXISTS lyrics (
                    isrc TEXT,
                    text TEXT NOT NULL,
                    synced_text TEXT,
                    source TEXT,
                    PRIMARY KEY (isrc, source),
                    FOREIGN KEY(isrc) REFERENCES tracks(isrc)
                )
            """)

    def save_track(self, meta: TrackMetadata) -> None:
        with self._get_connection() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO tracks 
                (isrc, title, artist, album, duration, resolver_type, resolver_id)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    meta.isrc,
                    meta.title,
                    meta.artist,
                    meta.album,
                    meta.duration,
                    meta.resolver,
                    meta.id,
                ),
            )

    def save_lyric(self, isrc: str, lyrics: LyricsData) -> None:
        with self._get_connection() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO lyrics
                (isrc, text, synced_text, source)
                VALUES (?, ?, ?, ?)
            """,
                (isrc, lyrics.text, lyrics.synced_text, lyrics.source),
            )

    def save_term(self, term: str, isrc: str) -> None:
        with self._get_connection() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO term_map
                (term_key, isrc)
                VALUES (?, ?)
            """,
                (term, isrc),
            )

    def get_isrc_by_term(self, term: str) -> str | None:
        with self._get_connection() as conn:
            row = conn.execute(
                """
                SELECT isrc FROM term_map WHERE term_key = ?
                """,
                (term,),
            ).fetchone()

            if not row:
                return None

            return row["isrc"]

    def get_track(self, isrc: str) -> TrackMetadata | None:
        with self._get_connection() as conn:
            row = conn.execute(
                """
                SELECT * FROM tracks WHERE isrc = ?
                """,
                (isrc,),
            ).fetchone()

            if not row:
                return None

            return TrackMetadata(
                isrc=row["isrc"],
                title=row["title"],
                artist=row["artist"],
                album=row["album"],
                duration=row["duration"],
                resolver=row["resolver_type"],
                id=row["resolver_id"],
            )

    def get_lyric(self, isrc: str) -> LyricsData | None:
        with self._get_connection() as conn:
            row = conn.execute(
                """
                SELECT * FROM lyrics WHERE isrc = ? LIMIT 1
                """,
                (isrc,),
            ).fetchone()

            if not row:
                return None

            return LyricsData(
                text=row["text"],
                synced_text=row["synced_text"],
                source=row["source"],
            )
