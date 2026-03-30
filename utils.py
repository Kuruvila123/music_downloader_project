"""
Utility helpers for the project.

Includes a minimal logger for yt-dlp that silences non-critical messages.
"""
from typing import Any


class YTDLPLogger:
    """A very small logger that matches yt-dlp expected methods.

    Use this to suppress yt-dlp warnings and info messages by passing an
    instance as the `logger` option to `YoutubeDL`.
    """
    def debug(self, msg: str) -> None:
        # Intentionally ignore debug messages
        return None

    def info(self, msg: str) -> None:
        # Intentionally ignore info messages
        return None

    def warning(self, msg: str) -> None:
        # Intentionally ignore warnings (suppresses signature-extraction warnings)
        return None

    def error(self, msg: str) -> None:
        # Print errors so real problems are visible
        try:
            print(msg)
        except Exception:
            pass
