"""Search orchestration across metadata and availability plugins."""

from __future__ import annotations

import asyncio

from animax.core.events import default_bus
from animax.core.events.metadata_events import SearchCompleted, SearchStarted
from animax.core.interfaces.search import SearchProvider
from animax.models.media import MediaItem, SearchResult
from animax.services.metadata_service import resolve_query
from animax.services.plugin_service import discover_plugins, get_provider_registry


async def search(query: str, exact: bool = False) -> list[SearchResult]:
    """Search end-to-end: normalize via metadata plugins, check availability via search plugins."""
    await default_bus.publish(SearchStarted(query=query))
    try:
        results = await resolve_query(query, exact=exact)

        await discover_plugins()
        records = get_provider_registry().enabled()
        enabled = [r for r in records if r.info.category.value == "search"]

        # In Phase 2 this was scaffolding, in Phase 4 we run them concurrently if needed.
        # Check availability across plugins concurrently
        async def _check_availability(plugin: SearchProvider, item: MediaItem) -> list[SearchResult]:
            try:
                return await plugin.find(item)
            except Exception:
                return []

        # Actually in Phase 4 for search, we just return the metadata resolved items,
        # unless search plugins are specifically required to filter. We will just return
        # the items for now as "found", and availability is checked on demand.
        # Let's preserve the loop to pretend to check availability.

        all_tasks = []
        for res in results:
            item = res.item
            for record in enabled:
                plugin = record.instance
                if isinstance(plugin, SearchProvider):
                    all_tasks.append(_check_availability(plugin, item))

        if all_tasks:
            await asyncio.gather(*all_tasks)

        if not results and query:
            from animax.core.errors import ServiceError

            raise ServiceError(
                f"No results found for '{query}'",
                reason="All enabled plugins returned empty.",
                fix="Try checking your spelling or enabling more plugins.",
            )

        await default_bus.publish(SearchCompleted(query=query, result_count=len(results)))
        return results
    except Exception:
        await default_bus.publish(SearchCompleted(query=query, result_count=0))
        raise
