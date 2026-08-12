import asyncio
import logging
import time
from pathlib import Path

from animax.cache.store import Cache
from animax.database.connection import connect, initialize
from animax.logging_config import configure_logging
from animax.services.plugin_service import discover_plugins


async def benchmark() -> None:
    print("--- Performance Benchmarks ---")

    # 1. Startup & Config
    t0 = time.perf_counter()
    from animax.services.config_service import load_settings

    load_settings()
    t1 = time.perf_counter()
    print(f"Config Load: {(t1 - t0) * 1000:.2f} ms")

    # 2. Plugin Discovery
    t0 = time.perf_counter()
    await discover_plugins()
    t1 = time.perf_counter()
    print(f"Plugin Discovery (First Run): {(t1 - t0) * 1000:.2f} ms")

    t0 = time.perf_counter()
    await discover_plugins()
    t1 = time.perf_counter()
    print(f"Plugin Discovery (Cached): {(t1 - t0) * 1000:.2f} ms")

    # 3. Cache
    cache = Cache("bench", max_size_bytes=100000)
    t0 = time.perf_counter()
    for i in range(100):
        cache.set(f"key{i}", "value" * 10)
    t1 = time.perf_counter()
    print(f"Cache Write (100 items): {(t1 - t0) * 1000:.2f} ms")

    t0 = time.perf_counter()
    for i in range(100):
        cache.get(f"key{i}")
    t1 = time.perf_counter()
    print(f"Cache Read (100 items): {(t1 - t0) * 1000:.2f} ms")

    # 4. Database
    await initialize(Path("bench.db"))
    t0 = time.perf_counter()
    async with connect(Path("bench.db")) as db:
        for _i in range(100):
            await db.execute(
                "INSERT INTO history_entries "
                "(media_id, title, episode, event, occurred_at) VALUES (?, ?, ?, ?, ?)",
                ("1", "Bench Title", 1.0, "PLAY", time.time()),
            )
    t1 = time.perf_counter()
    print(f"Database Insert (100 rows): {(t1 - t0) * 1000:.2f} ms")
    Path("bench.db").unlink(missing_ok=True)

    # 5. Logging
    configure_logging(debug=True)
    logger = logging.getLogger("bench")
    t0 = time.perf_counter()
    for _i in range(100):
        logger.debug("Bench log message")
    t1 = time.perf_counter()
    print(f"Logging (100 messages): {(t1 - t0) * 1000:.2f} ms")


if __name__ == "__main__":
    asyncio.run(benchmark())
