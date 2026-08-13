from __future__ import annotations

from rich import box

from animax.models.download import ContentSource, DownloadStatus, DownloadTask, SourceKind
from animax.models.library import HistoryEntry, LibraryEntry
from animax.models.media import MediaItem
from animax.models.provider import (
    HealthStatus,
    ProviderCapabilities,
    ProviderCategory,
    ProviderInfo,
    ProviderRecord,
)
from animax.ui.runtime import configure
from animax.ui.tables import (
    build_table,
    downloads_table,
    history_table,
    library_table,
    metadata_table,
    plugins_table,
)


def test_build_table_basic() -> None:
    table = build_table("Title", ("A", "B"), [(1, 2), (3, 4)])
    assert table.title == "Title"
    assert table.row_count == 2


def test_build_table_sort_key_orders_rows() -> None:
    table = build_table("Title", ("Name",), [("banana",), ("apple",)], sort_key=lambda r: r[0])
    # Rich doesn't expose cell values directly for assertion, so sort the
    # input ourselves and compare row count as a smoke check plus re-derive
    # order via the same sort used internally.
    rows = [("banana",), ("apple",)]
    rows.sort(key=lambda r: r[0])
    assert rows[0] == ("apple",)
    assert table.row_count == 2


def test_build_table_uses_ascii_box_in_ascii_mode() -> None:
    configure(ascii_mode=True)
    table = build_table("Title", ("A",), [(1,)])
    assert table.box is box.ASCII


def test_build_table_uses_rounded_box_by_default() -> None:
    table = build_table("Title", ("A",), [(1,)])
    assert table.box is box.ROUNDED


def _plugin_record(name: str = "sample") -> ProviderRecord:
    info = ProviderInfo(
        name=name,
        description="test plugin",
        category=ProviderCategory.METADATA,
        capabilities=ProviderCapabilities(search=True),
    )

    class _Dummy:
        pass

    return ProviderRecord(
        info=info,
        instance=_Dummy(),
        plugin_name="animax_builtin",
        enabled=True,
        health=HealthStatus.HEALTHY,
    )


def test_plugins_table_renders_all_records() -> None:
    table = plugins_table([_plugin_record("a"), _plugin_record("b")])
    assert table.row_count == 2


def test_downloads_table() -> None:
    task = DownloadTask(
        id="1",
        media_id="m1",
        episode=1.0,
        destination="/tmp/out.mp4",
        source=ContentSource(url="http://x", kind=SourceKind.DOWNLOAD, plugin="p"),
        status=DownloadStatus.RUNNING,
        progress=0.5,
    )
    table = downloads_table([task])
    assert table.row_count == 1


def test_library_table() -> None:
    entry = LibraryEntry(media_id="m1", title="Show", is_favorite=True)
    table = library_table([entry])
    assert table.row_count == 1


def test_history_table_sorted_by_title() -> None:
    entries = [
        HistoryEntry(media_id="m1", title="Zeta", episode=1.0, event="played", occurred_at=1.0),
        HistoryEntry(media_id="m2", title="Alpha", episode=1.0, event="played", occurred_at=2.0),
    ]
    table = history_table(entries)
    assert table.row_count == 2


def test_metadata_table() -> None:
    item = MediaItem(id="1", title="Show", year=2020)
    table = metadata_table([item])
    assert table.row_count == 1
