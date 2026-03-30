"""
Spotify playlist parsing via spotipy using Client Credentials flow.

Functions:
 - parse_playlist_id(url) -> str
 - get_spotify_tracks(playlist_url) -> list[str] ("Artist - Title")
"""
from typing import List, Optional
import re
from urllib.parse import urlparse, parse_qs

from spotipy import Spotify
from spotipy.oauth2 import SpotifyClientCredentials

from config import get_spotify_credentials


PLAYLIST_URL_RE = re.compile(r"playlist[/:]([0-9A-Za-z]+)")


def parse_playlist_id(url: str) -> Optional[str]:
    """Extract the Spotify playlist ID from a variety of URL formats."""
    # Try regex first
    m = PLAYLIST_URL_RE.search(url)
    if m:
        return m.group(1)
    # Fallback parse query param
    try:
        parsed = urlparse(url)
        qs = parse_qs(parsed.query)
        if "list" in qs:
            return qs["list"][0]
    except Exception:
        return None
    return None


def get_spotify_tracks(playlist_url: str) -> List[str]:
    """Return a list of search strings in the format "Artist - Title" for all tracks in the playlist.

    Uses Client Credentials auth and paginates with limit=100.
    Guards against null/removed tracks.
    """
    client_id, client_secret = get_spotify_credentials()
    if not client_id or not client_secret:
        raise RuntimeError(
            "Missing SPOTIPY_CLIENT_ID or SPOTIPY_CLIENT_SECRET environment variables"
        )

    auth_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
    sp = Spotify(auth_manager=auth_manager)

    playlist_id = parse_playlist_id(playlist_url)
    if not playlist_id:
        raise ValueError("Could not parse playlist ID from URL")

    results = []
    limit = 100
    offset = 0

    while True:
        page = sp.playlist_items(playlist_id, limit=limit, offset=offset)
        items = page.get("items", [])
        for item in items:
            track = item.get("track")
            if not track:
                continue
            name = track.get("name")
            artists = track.get("artists") or []
            artist_name = ", ".join(a.get("name") for a in artists if a.get("name"))
            if not name or not artist_name:
                continue
            results.append(f"{artist_name} - {name}")

        if page.get("next"):
            offset += limit
        else:
            break

    return results


def get_playlist_name(playlist_url: str) -> Optional[str]:
    """Return the playlist name/title for a Spotify playlist URL.

    Returns None if it cannot be fetched.
    """
    client_id, client_secret = get_spotify_credentials()
    if not client_id or not client_secret:
        return None

    auth_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
    sp = Spotify(auth_manager=auth_manager)

    playlist_id = parse_playlist_id(playlist_url)
    if not playlist_id:
        return None

    try:
        meta = sp.playlist(playlist_id, fields="name")
        return meta.get("name")
    except Exception:
        return None
