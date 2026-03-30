# Music Downloader

CLI tool to download Spotify or YouTube playlists as MP3 files.

## Features
- Download songs from a Spotify playlist URL
- Download songs from a YouTube playlist URL
- Download from a text playlist file (`Artist - Title` per line)
- Download a single song from artist + title input
- Parallel downloads with configurable quality/output folder

## Requirements
- Python 3.9+
- `ffmpeg` on your PATH

Install `ffmpeg` on macOS:

```bash
brew install ffmpeg
```

## Setup
From the repository root:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

If you plan to use Spotify, create a `.env` file in this directory with:

```env
SPOTIPY_CLIENT_ID=your_client_id
SPOTIPY_CLIENT_SECRET=your_client_secret
```

## Usage
Spotify playlist:

```bash
python3 main.py --spotify "SPOTIFY_PLAYLIST_URL"
```

YouTube playlist:

```bash
python3 main.py --youtube "YOUTUBE_PLAYLIST_URL"
```

Playlist text file (`Artist - Title` per line):

```bash
python3 downloader.py --playlist-file my_playlist.txt --output ./downloads
```

Single song:

```bash
python3 downloader.py "Artist Name" "Song Title"
```

## Useful Flags
- `--output ./downloads` set output directory
- `--quality 192` set MP3 bitrate (example)
- `--workers 4` control parallel downloads
- `--subfolder-by-playlist` group output by playlist name

## Notes
- Omit optional flags to use defaults.
- Keep your Spotify credentials private and never commit `.env`.
