"""
YouTube playlist downloading using yt-dlp Python API.

This module provides `download_playlist` which downloads each entry in a playlist
individually so we can perform per-track logging and error handling.
"""
from typing import Callable
import os
import re
from pathlib import Path

from yt_dlp import YoutubeDL
from utils import YTDLPLogger


def sanitize_filename(name: str) -> str:
    # Remove path-unfriendly characters
    return re.sub(r"[\\/:*?\"<>|]+", "", name).strip()


def download_playlist(
    playlist_url: str,
    output_dir: str,
    quality: int,
    seen_keys: set,
    append_log: Callable[[str, str], None],
) -> None:
    """Download all entries from a YouTube playlist URL.

    - `seen_keys` is a set-like containing already-downloaded identifiers (we check by entry id).
    - `append_log` is a callable that accepts (key, filename) to persist successes.
    """
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    ydl_opts_info = {"quiet": True, "skip_download": True, "no_warnings": True, "logger": YTDLPLogger()}
    with YoutubeDL(ydl_opts_info) as ydl:
        info = ydl.extract_info(playlist_url, download=False)
        entries = info.get("entries") or []

    # Prepare postprocessor and base options used for each item
    for entry in entries:
        if not entry:
            continue
        video_id = entry.get("id")
        webpage_url = entry.get("webpage_url") or entry.get("url")
        title = entry.get("title") or video_id or "unknown"
        key = f"youtube:{video_id}"
        if key in seen_keys:
            continue

        safe_title = sanitize_filename(title)
        outtmpl = os.path.join(output_dir, f"{safe_title}.%(ext)s")

        ydl_opts = {
            "format": "bestaudio/best",
            "outtmpl": outtmpl,
            "quiet": True,
            "no_warnings": True,
            "logger": YTDLPLogger(),
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": str(quality),
                }
            ],
        }

        try:
            with YoutubeDL(ydl_opts) as ydl:
                ydl.download([webpage_url])
            # The final filename should be safe_title + .mp3
            filename = f"{safe_title}.mp3"
            append_log(key, filename)
        except Exception:
            # Per-spec: don't let one failure stop the rest
            continue


def get_playlist_title(playlist_url: str) -> str | None:
    """Extract the playlist title for a YouTube playlist URL using yt-dlp."""
    ydl_opts = {"quiet": True, "skip_download": True, "no_warnings": True, "logger": YTDLPLogger()}
    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(playlist_url, download=False)
            return info.get("title")
    except Exception:
        return None
