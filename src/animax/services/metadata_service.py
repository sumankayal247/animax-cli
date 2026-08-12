"""Metadata aggregation and normalization."""

from __future__ import annotations

import asyncio
import difflib
import re
import unicodedata

from animax.core.events import default_bus
from animax.core.events.metadata_events import (
    EpisodesCompleted,
    EpisodesRequested,
    MetadataDetailsCompleted,
    MetadataDetailsStarted,
    ProviderQueryCompleted,
    ProviderQueryStarted,
    SearchNormalized,
    SearchRanked,
    SuggestionsGenerated,
)
from animax.core.interfaces.metadata import MetadataPlugin
from animax.models.media import Episode, MediaItem, SearchResult
from animax.services.plugin_service import discover_plugins


def _normalize_string(text: str) -> str:
    """Normalize whitespace and unicode for search matching."""
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("utf-8")
    return re.sub(r"\s+", " ", text).strip().lower()


async def resolve_query(query: str, exact: bool = False) -> list[SearchResult]:
    """Search enabled metadata plugins concurrently, normalize, and rank results."""
    normalized_query = _normalize_string(query)
    await default_bus.publish(
        SearchNormalized(original_query=query, normalized_query=normalized_query)
    )

    records, _ = await discover_plugins()
    enabled = [r for r in records if r.info.category.value == "metadata"]

    async def _query_plugin(plugin: MetadataPlugin, name: str) -> list[SearchResult]:
        await default_bus.publish(ProviderQueryStarted(provider_name=name, query=query))
        results: list[SearchResult] = []
        error: str | None = None
        try:
            results = await plugin.search(query)
        except Exception as e:
            error = str(e)
        finally:
            await default_bus.publish(
                ProviderQueryCompleted(
                    provider_name=name, query=query, result_count=len(results), error=error
                )
            )
        return results

    tasks = []
    for record in enabled:
        plugin = record.plugin
        if isinstance(plugin, MetadataPlugin):
            tasks.append(_query_plugin(plugin, record.info.name))

    results_list = await asyncio.gather(*tasks)
    all_results = [r for sublist in results_list for r in sublist]

    # Normalize results: deduplicate by title, merge external_ids
    seen: dict[str, MediaItem] = {}
    for res in all_results:
        item = res.item
        key = _normalize_string(item.title)
        if key not in seen:
            seen[key] = item
        else:
            # Merge plugins and external ids
            existing = seen[key]
            merged_plugins = tuple(set(existing.source_plugins + item.source_plugins))
            merged_ids = dict(existing.external_ids)
            merged_ids.update(item.external_ids)
            seen[key] = existing.model_copy(
                update={"source_plugins": merged_plugins, "external_ids": merged_ids}
            )

    final_results = []
    for _, item in seen.items():
        score = 0.0
        norm_title = _normalize_string(item.title)
        norm_alts = [_normalize_string(alt) for alt in item.alt_titles]

        # Exact title match
        if norm_title == normalized_query:
            score += 100
        elif exact:
            # If exact is requested, maybe an alternative title matches exactly
            if normalized_query in norm_alts:
                score += 80
            else:
                continue

        # Alternative title match
        if not score and normalized_query in norm_alts:
            score += 60

        # Fuzzy and partial matching
        if not score:
            title_similarity = difflib.SequenceMatcher(None, normalized_query, norm_title).ratio()
            alt_similarities = [
                difflib.SequenceMatcher(None, normalized_query, alt).ratio() for alt in norm_alts
            ]
            best_sim = max([title_similarity] + alt_similarities) if norm_alts else title_similarity

            if best_sim > 0.8:
                score += best_sim * 50
            elif normalized_query in norm_title:
                score += 40  # Partial match
            elif exact:
                continue  # If exact match required, this is dropped

        # Metadata completeness
        if item.synopsis:
            score += 5
        if item.cover_url:
            score += 5
        if item.episode_count:
            score += 5

        # Provider priority
        if "anilist" in item.source_plugins:
            score += 10
        if "kitsu" in item.source_plugins:
            score += 5

        # Media type bonus
        if item.media_type.value in ["TV", "Movie"]:
            score += 5

        final_results.append(SearchResult(item=item, score=score))

    # Filter out 0 scores if any fuzzy logic was applied
    final_results = [r for r in final_results if r.score > 0]

    # Deterministic sorting: by score desc, then by title asc
    final_results.sort(key=lambda x: (-x.score, _normalize_string(x.item.title)))

    await default_bus.publish(SearchRanked(query=query, result_count=len(final_results)))

    # Suggestions
    if not final_results:
        suggestions = [item.title for _, item in seen.items()][:5]
        if suggestions:
            await default_bus.publish(SuggestionsGenerated(query=query, suggestions=suggestions))

    return final_results


async def get_details(item_id: str, provider: str | None = None) -> MediaItem:
    """Get rich metadata details for an item from a specific provider."""
    await default_bus.publish(MetadataDetailsStarted(item_id=item_id))

    records, _ = await discover_plugins()
    enabled = [r for r in records if r.info.category.value == "metadata"]

    target_plugin = None
    if provider:
        target_plugin = next((r.plugin for r in enabled if r.info.name == provider), None)
    else:
        # Just pick the first available metadata plugin
        target_plugin = enabled[0].plugin if enabled else None

    if not isinstance(target_plugin, MetadataPlugin):
        error = "No suitable metadata plugin found"
        await default_bus.publish(
            MetadataDetailsCompleted(item_id=item_id, success=False, error=error)
        )
        raise RuntimeError(error)

    try:
        details = await target_plugin.get_details(item_id)
        await default_bus.publish(MetadataDetailsCompleted(item_id=item_id, success=True))
        return details
    except Exception as e:
        await default_bus.publish(
            MetadataDetailsCompleted(item_id=item_id, success=False, error=str(e))
        )
        raise


async def get_episodes(item_id: str, provider: str | None = None) -> list[Episode]:
    """Get episodes for an item from a specific provider."""
    await default_bus.publish(EpisodesRequested(item_id=item_id))

    records, _ = await discover_plugins()
    enabled = [r for r in records if r.info.category.value == "metadata"]

    target_plugin = None
    if provider:
        target_plugin = next((r.plugin for r in enabled if r.info.name == provider), None)
    else:
        target_plugin = enabled[0].plugin if enabled else None

    if not isinstance(target_plugin, MetadataPlugin):
        error = "No suitable metadata plugin found"
        await default_bus.publish(
            EpisodesCompleted(item_id=item_id, episode_count=0, success=False, error=error)
        )
        raise RuntimeError(error)

    try:
        episodes = await target_plugin.get_episodes(item_id)
        await default_bus.publish(
            EpisodesCompleted(item_id=item_id, episode_count=len(episodes), success=True)
        )
        return episodes
    except Exception as e:
        await default_bus.publish(
            EpisodesCompleted(item_id=item_id, episode_count=0, success=False, error=str(e))
        )
        raise
