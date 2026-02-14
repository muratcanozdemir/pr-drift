from collections import deque
from statistics import mean, stdev
from compression.zstd import ZstdCompressor, ZstdDict


class PRDriftDetector:
    def __init__(
        self,
        window_bytes=5_000_000,
        rebuild_every=10,
        level=3,
    ):
        self.window_bytes = window_bytes
        self.rebuild_every = rebuild_every
        self.level = level

        self.history = deque()
        self.history_bytes = 0
        self.scores = []

        self._since_rebuild = 0
        self._compressor = None

    def _rebuild(self):
        corpus = b"".join(self.history)
        if not corpus:
            return
        zdict = ZstdDict(corpus, is_raw=True)
        self._compressor = ZstdCompressor(
            level=self.level,
            zstd_dict=zdict,
        )
        self._since_rebuild = 0

    def _update_history(self, diff: bytes):
        self.history.append(diff)
        self.history_bytes += len(diff)
        while self.history_bytes > self.window_bytes:
            removed = self.history.popleft()
            self.history_bytes -= len(removed)

    def score(self, diff: bytes) -> float:
        if not self._compressor or len(diff) == 0:
            return 0.0
        compressed = self._compressor.compress(
            diff,
            ZstdCompressor.FLUSH_FRAME,
        )
        return len(compressed) / len(diff)

    def observe(self, diff: bytes) -> dict:
        if self._compressor is None:
            self._rebuild()

        s = self.score(diff)
        self.scores.append(s)

        if len(self.scores) > 30:
            mu = mean(self.scores)
            sigma = stdev(self.scores)
            z = (s - mu) / sigma if sigma > 0 else 0.0
        else:
            z = 0.0

        self._update_history(diff)
        self._since_rebuild += 1
        if self._since_rebuild >= self.rebuild_every:
            self._rebuild()

        return {
            "score": s,
            "z_score": z,
            "history_mb": self.history_bytes / 1e6,
        }
