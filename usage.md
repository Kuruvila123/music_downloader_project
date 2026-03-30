python3 music-downloader/main.py \
  --youtube "https://www.youtube.com/playlist?list=..." \
  --output ./downloads --quality 320 --workers 4 --subfolder-by-playlist


python3 music-downloader/main.py \
  --spotify "https://open.spotify.com/playlist/5zCdhPJHI9kgYsgkSBEWT0?si=ac9c96c1243a425e" \
  --output ./downloads --quality 320 --workers 4 --subfolder-by-playlist



- Using system Python:

Spotify (only required arg + defaults):
python3 main.py --spotify "SPOTIFY_PLAYLIST_URL"
YouTube:
python3 main.py --youtube "YOUTUBE_PLAYLIST_URL"


- Examples with optional flags (only include what you need)

Custom output and playlist subfolder:
main.py --spotify "URL" --subfolder-by-playlist
Lower quality and fewer workers:
main.py --youtube "URL" --quality 192 --workers 2