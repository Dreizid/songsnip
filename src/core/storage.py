import sqlite3
from pathlib import Path
from src.core.schema import LyricsData, TrackMetadata
from src.core.types import ProviderType


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
                CREATE TABLE IF NOT EXISTS tracks (
                    track_id TEXT PRIMARY KEY,
                    isrc TEXT,
                    title TEXT NOT NULL,
                    artist TEXT NOT NULL,
                    album TEXT,
                    duration INTEGER,
                    resolver_type TEXT,
                    resolver_id INTEGER
                )
            """)

            conn.execute("""
                CREATE TABLE IF NOT EXISTS term_map (
                    term_key TEXT PRIMARY KEY,
                    track_id TEXT NOT NULL,
                    FOREIGN KEY(track_id) REFERENCES tracks(track_id) ON DELETE CASCADE
                )
            """)

            conn.execute("""
                CREATE TABLE IF NOT EXISTS lyrics (
                    track_id TEXT NOT NULL,
                    text TEXT NOT NULL,
                    synced_text TEXT,
                    source TEXT,
                    PRIMARY KEY (track_id, source),
                    FOREIGN KEY(track_id) REFERENCES tracks(track_id) ON DELETE CASCADE
                )
            """)

    def save_track(self, meta: TrackMetadata) -> None:
        with self._get_connection() as conn:
            conn.execute(
                """
                INSERT INTO tracks 
                (track_id, isrc, title, artist, album, duration, resolver_type, resolver_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT (track_id) DO NOTHING
            """,
                (
                    meta.track_id,
                    meta.isrc,
                    meta.title,
                    meta.artist,
                    meta.album,
                    meta.duration,
                    meta.resolver,
                    meta.id,
                ),
            )

    def save_lyric(self, track_id: str, lyrics: LyricsData) -> None:
        with self._get_connection() as conn:
            conn.execute(
                """
                INSERT INTO lyrics
                (track_id, text, synced_text, source)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(track_id, source) DO NOTHING
            """,
                (track_id, lyrics.text, lyrics.synced_text, lyrics.source),
            )

    def save_term(self, term: str, track_id: str) -> None:
        with self._get_connection() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO term_map
                (term_key, track_id)
                VALUES (?, ?)
                ON CONFLICT (term_key) DO NOTHING
            """,
                (term, track_id),
            )

    def get_track_id_by_term(self, term: str) -> str | None:
        with self._get_connection() as conn:
            row = conn.execute(
                """
                SELECT track_id FROM term_map WHERE term_key = ?
                """,
                (term,),
            ).fetchone()

            if not row:
                return None

            return row["track_id"]

    def get_track(self, track_id: str) -> TrackMetadata | None:
        with self._get_connection() as conn:
            row = conn.execute(
                """
                SELECT * FROM tracks WHERE track_id = ?
                """,
                (track_id,),
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

    def get_lyric(self, track_id: str, source: ProviderType) -> LyricsData | None:
        with self._get_connection() as conn:
            row = conn.execute(
                """
                SELECT * FROM lyrics WHERE track_id = ? AND source = ? LIMIT 1
                """,
                (track_id, source),
            ).fetchone()

            if not row:
                return None

            return LyricsData(
                text=row["text"],
                synced_text=row["synced_text"],
                source=row["source"],
            )
