LYRIC_SCHEMA = [
    """CREATE TABLE IF NOT EXISTS tracks (
        track_id TEXT PRIMARY KEY,
        isrc TEXT,
        title TEXT NOT NULL,
        artist TEXT NOT NULL,
        album TEXT,
        duration INTEGER,
        resolver_type TEXT,
        resolver_id INTEGER
    )""",
    """CREATE TABLE IF NOT EXISTS term_map (
        term_key TEXT PRIMARY KEY,
        track_id TEXT NOT NULL,
        FOREIGN KEY(track_id) REFERENCES tracks(track_id) ON DELETE CASCADE
    )""",
    """CREATE TABLE IF NOT EXISTS lyrics (
        track_id TEXT NOT NULL,
        text TEXT NOT NULL,
        synced_text TEXT,
        source TEXT,
        PRIMARY KEY (track_id, source),
        FOREIGN KEY(track_id) REFERENCES tracks(track_id) ON DELETE CASCADE
    )""",
]
