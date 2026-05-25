from src.cache.manager import DatabaseManager
from src.core.schema import TrackMetadata, LyricsData
from src.core.types import ProviderType


class LyricCache:
    def __init__(self, db: DatabaseManager) -> None:
        self.db = db

    def save_track(self, meta: TrackMetadata) -> None:
        with self.db.get_connection() as conn:
            conn.execute(
                """
                INSERT INTO tracks 
                (track_id, isrc, title, artist, album, duration, resolver_type, resolver_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT (track_id) DO NOTHING;
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
        with self.db.get_connection() as conn:
            conn.execute(
                """
                INSERT INTO lyrics
                (track_id, text, synced_text, source)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(track_id, source) DO NOTHING;
            """,
                (track_id, lyrics.text, lyrics.synced_text, lyrics.source),
            )

    def save_term(self, term: str, track_id: str) -> None:
        with self.db.get_connection() as conn:
            conn.execute(
                """
                INSERT INTO term_map
                (term_key, track_id)
                VALUES (?, ?)
                ON CONFLICT (term_key) DO NOTHING;
            """,
                (term, track_id),
            )

    def get_track_id_by_term(self, term: str) -> str | None:
        with self.db.get_connection() as conn:
            row = conn.execute(
                """
                SELECT track_id FROM term_map WHERE term_key = ?;
                """,
                (term,),
            ).fetchone()

            if not row:
                return None

            return row["track_id"]

    def get_track(self, track_id: str) -> TrackMetadata | None:
        with self.db.get_connection() as conn:
            row = conn.execute(
                """
                SELECT * FROM tracks WHERE track_id = ?;
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
        with self.db.get_connection() as conn:
            row = conn.execute(
                """
                SELECT * FROM lyrics WHERE track_id = ? AND source = ? LIMIT 1;
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
