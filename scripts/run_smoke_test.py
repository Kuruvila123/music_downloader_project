"""Smoke test for music-downloader without network or external binaries.

This script injects lightweight fake versions of `spotipy`, `yt_dlp`, and
`mutagen`, creates a fake `ffmpeg` in PATH, and runs the `main` entry for
Spotify and YouTube flows to ensure import-time and basic runtime paths work.
"""
import os
import sys
import types
import tempfile
import stat
from pathlib import Path


def make_fake_ffmpeg(tmpdir: Path) -> None:
    ff = tmpdir / "ffmpeg"
    ff.write_text("#!/bin/sh\n# fake ffmpeg for tests\nexit 0\n")
    ff.chmod(ff.stat().st_mode | stat.S_IXUSR)


def inject_fakes():
    # spotipy
    spotipy = types.ModuleType("spotipy")
    class FakeSpotify:
        def __init__(self, *a, **k):
            pass
        def playlist_items(self, playlist_id, limit=100, offset=0):
            return {"items": [], "next": None}
    spotipy.Spotify = FakeSpotify
    spotipy.oauth2 = types.ModuleType("spotipy.oauth2")
    class FakeCreds:
        def __init__(self, *a, **k):
            pass
    spotipy.oauth2.SpotifyClientCredentials = FakeCreds
    sys.modules["spotipy"] = spotipy
    sys.modules["spotipy.oauth2"] = spotipy.oauth2

    # yt_dlp
    yt_dlp = types.ModuleType("yt_dlp")
    class FakeYDL:
        def __init__(self, opts=None):
            self.opts = opts or {}
        def __enter__(self):
            return self
        def __exit__(self, exc_type, exc, tb):
            return False
        def download(self, items):
            # Do not create files; simulate success
            return None
        def extract_info(self, url, download=False):
            return {"entries": []}
    yt_dlp.YoutubeDL = FakeYDL
    sys.modules["yt_dlp"] = yt_dlp

    # mutagen
    mutagen = types.ModuleType("mutagen")
    mutagen.easyid3 = types.ModuleType("mutagen.easyid3")
    class FakeEasyID3(dict):
        def save(self):
            return None
    mutagen.easyid3.EasyID3 = FakeEasyID3
    mutagen.mp3 = types.ModuleType("mutagen.mp3")
    class FakeMP3:
        def __init__(self, path, ID3=None):
            pass
        def add_tags(self):
            pass
    mutagen.mp3.MP3 = FakeMP3
    sys.modules["mutagen"] = mutagen
    sys.modules["mutagen.easyid3"] = mutagen.easyid3
    sys.modules["mutagen.mp3"] = mutagen.mp3


def run():
    root = Path(__file__).resolve().parents[1]
    tmp = Path(tempfile.mkdtemp(prefix="md_test_"))
    make_fake_ffmpeg(tmp)
    # Prepend tmp to PATH
    os.environ["PATH"] = str(tmp) + os.pathsep + os.environ.get("PATH", "")

    inject_fakes()

    # Ensure the package folder is on sys.path so we can import modules by name
    sys.path.insert(0, str(root))

    # Ensure env vars for Spotify flow
    os.environ.setdefault("SPOTIPY_CLIENT_ID", "FAKEID")
    os.environ.setdefault("SPOTIPY_CLIENT_SECRET", "FAKESECRET")

    # Run main Spotify flow (should not crash; will find no tracks)
    try:
        import main
        print("Running main with --spotify (expected: no tracks found)")
        try:
            main.main(["--spotify", "https://open.spotify.com/playlist/test", "--output", str(root / "downloads_test")])
        except SystemExit as e:
            print("main exited with", e)
    except Exception as e:
        print("Failed to run main for spotify:", e)
        raise

    # Run main YouTube flow (expected: no entries)
    try:
        print("Running main with --youtube (expected: no entries)")
        try:
            main.main(["--youtube", "https://www.youtube.com/playlist?list=TEST", "--output", str(root / "downloads_test")])
        except SystemExit as e:
            print("main exited with", e)
    except Exception as e:
        print("Failed to run main for youtube:", e)
        raise

    # Test downloader.search-based function
    try:
        from downloader import LogManager, download_search_track
        logs_dir = root.joinpath("logs")
        logs_dir.mkdir(parents=True, exist_ok=True)
        log_file = logs_dir.joinpath("downloaded.log")
        log_file.touch(exist_ok=True)
        lm = LogManager(log_file)
        print("Testing download_search_track (expected: file-not-found due to fake YDL)")
        success, info = download_search_track("Artist - Title", str(root / "downloads_test"), 320, lm, lm.append)
        print("download_search_track returned:", success, info)
    except Exception as e:
        print("Failed to test download_search_track:", e)
        raise

    print("Smoke test completed successfully")


if __name__ == "__main__":
    run()
