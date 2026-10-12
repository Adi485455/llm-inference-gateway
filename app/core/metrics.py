import asyncio
from collections import Counter


class GatewayMetrics:
    def __init__(self):
        self._lock = asyncio.Lock()
        self._counters = Counter()
        self._total_latency_seconds = 0.0

    async def increment(self, name: str):
        async with self._lock:
            self._counters[name] += 1

    async def record_latency(self, seconds: float):
        async with self._lock:
            self._total_latency_seconds += seconds
            self._counters["completed_requests"] += 1

    async def snapshot(self):
        async with self._lock:
            completed = self._counters["completed_requests"]

            return {
                "counters": dict(self._counters),
                "average_latency_seconds": (
                    self._total_latency_seconds / completed
                    if completed
                    else 0.0
                ),
            }


metrics = GatewayMetrics()