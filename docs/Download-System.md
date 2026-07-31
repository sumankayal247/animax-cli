# Download System

**Status: not yet implemented — planned for Phase 5.**

## Scope (per the project spec)

- Download queue, with parallel downloads up to `download.concurrent_downloads`.
- Retry logic (`download.retries`) and resume support (HTTP range requests
  where the source supports them).
- Progress reporting via the event bus (`core.events.types.DOWNLOAD_PROGRESS`)
  consumed by a Rich `Live` progress view in `ui/`.
- Pause/cancel per task; a persisted history (`database.download_tasks`
  table — schema already created in Phase 1, see [Database.md](Database.md)).
- Verification where the source provides a checksum/size.
- Provider-agnostic: the engine only knows about `models.download.ContentSource`
  / `DownloadTask`, produced by `DownloadPlugin`/`StreamingPlugin` — it never
  hardcodes a content source.

## Destination resolution (implemented, Phase 1)

`services.config_service.resolve_download_directory(settings, cwd)`:
if `download.directory` is set in config, use it; otherwise default to the
current working directory the CLI was launched from (e.g. running inside
`~/Anime` downloads there).

## Flow (target, Phase 5)

```
Search -> Episode Selection -> Quality Selection -> Download -> Verification
-> Complete -> prompt "Play now? (Y/N)" -> Player (player/)
```
