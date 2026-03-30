```mermaid
flowchart LR
  %% Actors
  U[User / CLI]

  %% Core
  U --> |invokes| Main[main.py \n(CLI)]
  Main --> Config[config.py \n(startup checks: ffmpeg, .env)]

  Main --> Decision{mode}
  Decision --> |spotify| SP[spotify_handler.py]
  Decision --> |youtube| YT[youtube_handler.py]

  %% Spotify flow
  SP --> SPAPI[Spotify API (spotipy) \npaginate limit=100]
  SPAPI --> TrackList[Track list \n("Artist - Title")]
  TrackList --> Downloader[downloader.py \n(ThreadPoolExecutor + tqdm)]

  %% YouTube flow
  YT --> YTExtract[yt-dlp.extract_info\n(list entries)]
  YTExtract --> EntryList[Entry list (video ids/urls)]
  EntryList --> Downloader

  %% Core download steps
  Downloader --> |for each track| YTDL[yt-dlp API]
  YTDL --> FF[ffmpeg (FFmpegExtractAudio)]
  FF --> MP3[.mp3 file]
  MP3 --> Mutagen[mutagen (ID3 tags)]
  Mutagen --> Logs[logs/downloaded.log \n(append key -> filename)]

  %% Duplicate prevention and re-use
  Downloader --> |reads| Logs
  Logs --> |skips| Downloader

  %% Outputs
  MP3 --> Downloads[downloads/ (output dir)]

  %% Utilities
  YTDL -.-> |logger| Utils[utils.YTDLPLogger]
  Main -.-> |loads| DotEnv[.env via python-dotenv]

  classDef infra fill:#f9f,stroke:#333,stroke-width:1px;
  class Config,FF,Logs,Downloads,DotEnv infra;

  %% Notes
  subgraph Notes[Notes]
    N1["- Spotify: Client Credentials auth required"]
    N2["- Spotify pagination handles playlists >100 tracks"]
    N3["- Per-track try/except prevents single failures from stopping run"]
  end

  Notes --> Main
```

Save: music-downloader/ARCHITECTURE.md — open this file in an editor that supports Mermaid or render with a Mermaid renderer to print.
