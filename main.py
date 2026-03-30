#!/usr/bin/env python3
"""
CLI entry point for music-downloader.

Supports downloading from Spotify playlists (searching YouTube per track)
and direct YouTube playlist downloads.
"""
import argparse
import sys
from pathlib import Path

from config import load_env, ensure_ffmpeg_present, ensure_dirs, get_spotify_credentials
from downloader import LogManager, download_tracks_concurrent, sanitize_filename
from spotify_handler import get_spotify_tracks
from youtube_handler import download_playlist
from youtube_handler import get_playlist_title
from spotify_handler import get_playlist_name


def main(argv=None):
    parser = argparse.ArgumentParser(description="Download playlist tracks as MP3s")
    parser.add_argument("--spotify", help="Spotify playlist URL")
    parser.add_argument("--youtube", help="YouTube playlist URL")
    parser.add_argument("--output", default="./downloads", help="Output directory (default: ./downloads)")
    parser.add_argument("--subfolder-by-playlist", action="store_true", help="Create a subfolder per playlist inside the output folder")
    parser.add_argument("--quality", choices=["128", "192", "320"], default="320", help="MP3 quality (default: 320)")
    parser.add_argument("--workers", type=int, default=4, help="Number of concurrent download workers (default: 4)")
    args = parser.parse_args(argv)

    # Load .env
    load_env()

    # Startup checks
    if not ensure_ffmpeg_present():
        print("ffmpeg is required but was not found on PATH. Install via 'brew install ffmpeg' or visit https://ffmpeg.org/")
        sys.exit(1)

    client_id, client_secret = get_spotify_credentials()
    if args.spotify and (not client_id or not client_secret):
        print("Spotify credentials missing. Create a .env with SPOTIPY_CLIENT_ID and SPOTIPY_CLIENT_SECRET. See README for details.")
        sys.exit(1)

    downloads_dir, logs_dir = ensure_dirs(args.output)
    log_file = logs_dir.joinpath("downloaded.log")
    log_manager = LogManager(log_file)

    quality = int(args.quality)

    if args.spotify:
        print("Parsing Spotify playlist...")
        try:
            tracks = get_spotify_tracks(args.spotify)
        except Exception as exc:
            print(f"Failed to fetch Spotify playlist: {exc}")
            sys.exit(1)
        if not tracks:
            print("No tracks found in playlist.")
            return
        out_dir = downloads_dir
        if args.subfolder_by_playlist:
            pname = get_playlist_name(args.spotify) or parse_playlist_id(args.spotify) or "playlist"
            safe = sanitize_filename(pname)
            out_dir = downloads_dir.joinpath(safe)
            out_dir.mkdir(parents=True, exist_ok=True)
        download_tracks_concurrent(tracks, str(out_dir), quality, workers=args.workers, log_manager=log_manager)

    if args.youtube:
        print("Downloading YouTube playlist...")
        out_dir = downloads_dir
        if args.subfolder_by_playlist:
            ytitle = get_playlist_title(args.youtube) or "youtube_playlist"
            safe = sanitize_filename(ytitle)
            out_dir = downloads_dir.joinpath(safe)
            out_dir.mkdir(parents=True, exist_ok=True)
        # youtube_handler will call append_log via log_manager.append
        download_playlist(args.youtube, str(out_dir), quality, log_manager.load(), log_manager.append)


if __name__ == "__main__":
    main()
