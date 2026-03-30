import sys, types

# Create minimal fake spotipy
spotipy = types.ModuleType('spotipy')
class FakeSpotify:
    def __init__(self, *a, **k):
        pass
    def playlist_items(self, *a, **k):
        return {'items': [], 'next': None}
spotipy.Spotify = FakeSpotify
spotipy.oauth2 = types.ModuleType('spotipy.oauth2')
class FakeCreds:
    def __init__(self, *a, **k):
        pass
spotipy.oauth2.SpotifyClientCredentials = FakeCreds
sys.modules['spotipy'] = spotipy
sys.modules['spotipy.oauth2'] = spotipy.oauth2

# Create minimal fake yt_dlp
yt_dlp = types.ModuleType('yt_dlp')
class FakeYDL:
    def __init__(self, opts=None):
        pass
    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc, tb):
        return False
    def download(self, items):
        return None
    def extract_info(self, url, download=False):
        return {'entries': []}
yt_dlp.YoutubeDL = FakeYDL
sys.modules['yt_dlp'] = yt_dlp

# Create minimal fake mutagen
mutagen = types.ModuleType('mutagen')
mutagen.easyid3 = types.ModuleType('mutagen.easyid3')
class FakeEasyID3(dict):
    def save(self):
        return None
mutagen.easyid3.EasyID3 = FakeEasyID3
mutagen.mp3 = types.ModuleType('mutagen.mp3')
class FakeMP3:
    def __init__(self, path, ID3=None):
        pass
    def add_tags(self):
        pass
mutagen.mp3.MP3 = FakeMP3
sys.modules['mutagen'] = mutagen
sys.modules['mutagen.easyid3'] = mutagen.easyid3
sys.modules['mutagen.mp3'] = mutagen.mp3

# Now try importing our modules
ok = True
mods = ['config','spotify_handler','youtube_handler','downloader','main']
for m in mods:
    try:
        __import__(m)
        print('imported', m)
    except Exception as e:
        print('FAILED import', m, e)
        ok = False
if not ok:
    raise SystemExit(1)
