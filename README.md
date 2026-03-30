
# Music Downloader — Quick Manual

A small CLI that downloads Spotify or YouTube playlists as MP3 files.

Quick prerequisites
- Python 3.9+ (or system Python)
- ffmpeg on PATH (macOS: `brew install ffmpeg`)

Quick start (recommended, safe)
1. Create a virtual environment (optional but recommended):

```bash
cd /path/to/project
/opt/homebrew/bin/python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r music-downloader/requirements.txt
```

2. Add Spotify credentials (only if using `--spotify`): edit `.env` in the project root:

```
SPOTIPY_CLIENT_ID=your_client_id
SPOTIPY_CLIENT_SECRET=your_client_secret
```

3. Run the CLI

# Music Downloader — Minimal Commands

Quick: run these from the project root. Ensure `ffmpeg` is installed and dependencies are present.

1) Spotify playlist (requires `.env` with `SPOTIPY_CLIENT_ID` and `SPOTIPY_CLIENT_SECRET`):

```bash
python3 music-downloader/main.py --spotify "SPOTIFY_PLAYLIST_URL"
```

2) YouTube playlist:

```bash
python3 music-downloader/main.py --youtube "YOUTUBE_PLAYLIST_URL"
```

3) From a plain text playlist file (`Artist - Title` per line):

```bash
python3 music-downloader/downloader.py --playlist-file my_playlist.txt --output ./downloads
```

4) Single song (artist + title):

```bash
python3 music-downloader/downloader.py "Artist Name" "Song Title"
```

Notes:
- You can omit `--output`, `--quality`, and `--workers` to use defaults.
- Add `--subfolder-by-playlist` to group downloads under a playlist-named folder.
```bash

