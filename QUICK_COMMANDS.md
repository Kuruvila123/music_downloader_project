# Quick Commands

Run these from the project root. Assumes `ffmpeg` is installed and dependencies are available.

1) Spotify playlist (requires `.env` with `SPOTIPY_CLIENT_ID` and `SPOTIPY_CLIENT_SECRET`)

```bash
python3 music-downloader/main.py --spotify "SPOTIFY_PLAYLIST_URL"
```

2) YouTube playlist

```bash
python3 music-downloader/main.py --youtube "YOUTUBE_PLAYLIST_URL"
```

3) From a plain text playlist file (`Artist - Title` per line)

```bash
python3 music-downloader/downloader.py --playlist-file my_playlist.txt --output ./downloads
```

4) Single song (artist + title)

```bash
python3 music-downloader/downloader.py "Artist Name" "Song Title"
```

Notes:
- Omit `--output`, `--quality`, and `--workers` to use defaults.
- Add `--subfolder-by-playlist` to place downloads in a playlist-named subfolder.
