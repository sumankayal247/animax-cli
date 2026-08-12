"""Console and file logging setup."""

from __future__ import annotations

import json
import logging
import traceback
from datetime import datetime

from rich.logging import RichHandler

from animax.config.paths import log_dir
from animax.ui.theme import console


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        data = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "name": record.name,
            "message": record.getMessage(),
        }
        if record.exc_info:
            data["exc_info"] = self.formatException(record.exc_info)
        return json.dumps(data)


def configure_logging(*, debug: bool = False, verbose: bool = False) -> None:
    level = logging.DEBUG if debug else (logging.INFO if verbose else logging.WARNING)
    
    logs = log_dir()
    logs.mkdir(parents=True, exist_ok=True)
    
    file_handler = logging.FileHandler(logs / "animax.log", encoding="utf-8")
    file_handler.setFormatter(logging.Formatter("[%(asctime)s] %(levelname)s:%(name)s: %(message)s"))
    
    json_handler = logging.FileHandler(logs / "animax.json.log", encoding="utf-8")
    json_handler.setFormatter(JsonFormatter())
    
    rich_handler = RichHandler(console=console, rich_tracebacks=debug, show_path=debug)
    
    logging.basicConfig(
        level=level,
        handlers=[rich_handler, file_handler, json_handler],
        force=True,
    )


def log_crash(exc: Exception) -> None:
    logs = log_dir()
    logs.mkdir(parents=True, exist_ok=True)
    crash_file = logs / "crash.log"
    with crash_file.open("a", encoding="utf-8") as f:
        f.write("--- CRASH REPORT ---\n")
        f.write(f"Timestamp: {datetime.now().isoformat()}\n")
        f.write(f"Error: {type(exc).__name__}: {exc}\n\n")
        traceback.print_exception(type(exc), exc, exc.__traceback__, file=f)
        f.write("\n")
