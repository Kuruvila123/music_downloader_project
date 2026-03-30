"""
Core download logic.

Provides functions to download tracks by searching YouTube (ytsearch1:) and to
manage duplicate logs and ID3 tagging using mutagen.
"""
from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Callable, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

from yt_dlp import YoutubeDL
from utils import YTDLPLogger
from mutagen.easyid3 import EasyID3
from mutagen.mp3 import MP3


def sanitize_filename(name: str) -> str:
    # Remove characters not allowed in filenames
    name = re.sub(r"[\\/:*?\"<>|]+", "", name)
    name = re.sub(r"\s+", " ", name).strip()
    return name


class LogManager:
    def __init__(self, log_path: Path):
        self.log_path = log_path
        self._lock = threading.Lock()
        self._seen = None

    def load(self) -> set:
        if self._seen is not None:
            return self._seen
        s = set()
        if self.log_path.exists():
            for line in self.log_path.read_text(encoding="utf-8").splitlines():
                if "->" in line:
                    key = line.split("->", 1)[0].strip()
                    s.add(key)
        self._seen = s
        return s

    def append(self, key: str, filename: str) -> None:
        with self._lock:
            with self.log_path.open("a", encoding="utf-8") as f:
                f.write(f"{key} -> {filename}\n")
            if self._seen is not None:
                self._seen.add(key)


def write_id3_tags(file_path: Path, artist: str, title: str) -> None:
    try:
        audio = MP3(file_path, ID3=EasyID3)
        try:
            tags = EasyID3(file_path)
        except Exception:
            audio.add_tags()
            tags = EasyID3(file_path)
        tags["title"] = title
        tags["artist"] = artist
        tags.save()
    except Exception:
        # Tagging failure should not crash the downloader
        return


def download_search_track(
    search_query: str,
    output_dir: str,
    quality: int,
    log_manager: LogManager,
    append_log: Callable[[str, str], None],
) -> Tuple[bool, str]:
    """Search YouTube with `ytsearch1:` and download as MP3.

    Returns (success, filename_or_error).
    """
    key = f"search:{search_query}"
    seen = log_manager.load()
    if key in seen:
        return False, "skipped"

    safe_name = sanitize_filename(search_query)
    outtmpl = os.path.join(output_dir, f"{safe_name}.%(ext)s")

    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": outtmpl,
        "quiet": True,
        "noplaylist": True,
        "default_search": "ytsearch1",
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
            ydl.download([search_query])

        # After download, assume file is {safe_name}.mp3
        filename = f"{safe_name}.mp3"

        # Attempt to split artist/title from query
        if " - " in search_query:
            artist, title = [s.strip() for s in search_query.split(" - ", 1)]
        else:
            artist, title = "", search_query

        file_path = Path(output_dir).joinpath(filename)
        if file_path.exists():
            write_id3_tags(file_path, artist, title)
            append_log(key, filename)
            return True, filename
        else:
            return False, "file-not-found"
    except Exception as exc:
        return False, str(exc)


def download_tracks_concurrent(
    queries: list,
    output_dir: str,
    quality: int,
    workers: int = 4,
    log_manager: Optional[LogManager] = None,
) -> None:
    """Download a list of search queries concurrently with a progress bar."""
    from tqdm import tqdm

    output_dir = str(Path(output_dir).resolve())
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    if log_manager is None:
        raise ValueError("A LogManager instance is required")

    seen = log_manager.load()
    tasks = []
    for q in queries:
        key = f"search:{q}"
        if key in seen:
            continue
        tasks.append(q)

    if not tasks:
        return

    lock = threading.Lock()
    with ThreadPoolExecutor(max_workers=workers) as exe:
        futures = {exe.submit(download_search_track, q, output_dir, quality, log_manager, log_manager.append): q for q in tasks}
        with tqdm(total=len(futures), desc="Downloading") as pbar:
            for fut in as_completed(futures):
                q = futures[fut]
                try:
                    success, info = fut.result()
                except Exception:
                    success, info = False, "exception"
                pbar.update(1)


def _read_playlist_file(path: str) -> list:
    """Read a simple playlist file containing lines in `Artist - Title` format.

    Ignores blank lines and lines starting with '#'. Returns a list of strings.
    """
    res = []
    p = Path(path)
    if not p.exists():
        return res
    for raw in p.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        res.append(line)
    return res


#!/usr/bin/env python3

def _cli():
    """Small CLI for single-song and playlist-file downloads.

    Usage examples:
      python3 downloader.py "Artist" "Song Title"
      python3 downloader.py --playlist-file my_playlist.txt --output ./downloads --quality 320
    """
    import argparse
    parser = argparse.ArgumentParser(description="Download single song or a simple playlist file (Artist - Title per line)")
    parser.add_argument("artist", nargs="?", help="Artist name for single-song mode")
    parser.add_argument("title", nargs="?", help="Song title for single-song mode")
    parser.add_argument("--playlist-file", help="Path to a text file with lines 'Artist - Title' to download")
    parser.add_argument("--output", default="./downloads", help="Output directory (default ./downloads)")
    parser.add_argument("--quality", choices=["128", "192", "320"], default="320", help="MP3 quality (default 320)")
    parser.add_argument("--workers", type=int, default=4, help="Number of concurrent workers for playlist file mode")
    args = parser.parse_args()

    # Ensure directories
    from config import ensure_dirs

    downloads_dir, logs_dir = ensure_dirs(args.output)
    log_file = logs_dir / "downloaded.log"
    lm = LogManager(log_file)

    quality = int(args.quality)

    # Single-song mode if both artist and title provided
    if args.artist and args.title:
        query = f"{args.artist} - {args.title}"
        success, info = download_search_track(query, str(downloads_dir), quality, lm, lm.append)
        if success:
            print(f"Downloaded: {info}")
        else:
            print(f"Failed: {info}")
        return

    # Playlist-file mode
    if args.playlist_file:
        items = _read_playlist_file(args.playlist_file)
        if not items:
            print("No songs found in playlist file.")
            return
        download_tracks_concurrent(items, str(downloads_dir), quality, workers=args.workers, log_manager=lm)
        return

    parser.print_help()


if __name__ == "__main__":
    _cli()
