from src.core.storage import LyricCache
from src.resolvers.base import BaseResolver
from src.providers.base import BaseScraper


class LyricPipeline:
    def __init__(
        self, cache: LyricCache, resolver: BaseResolver, provider: BaseScraper
    ):
        self.cache = cache
        self.resolver = resolver
        self.provider = provider

    def run(self, query: str) -> None:
        track_id = self.cache.get_track_id_by_term(term=query)

        if track_id is None:
            resolved_track = self.resolver.resolve(query=query)
            track_id = resolved_track.track_id

            self.cache.save_track(meta=resolved_track)
            self.cache.save_term(term=query, track_id=track_id)

        track_data = self.cache.get_track(track_id=track_id)

        if track_data is None:
            raise RuntimeError(
                f"Database integrity anomaly: track_id {track_id} doesn't exists."
            )

        lyrics = self.cache.get_lyric(
            track_id=track_id, source=self.provider.PROVIDER_TYPE
        )

        if lyrics is None:
            lyrics = self.provider.fetch(track_data)
            self.cache.save_lyric(lyrics=lyrics, track_id=track_id)

        for lyric in lyrics.lines:
            print(lyric)
