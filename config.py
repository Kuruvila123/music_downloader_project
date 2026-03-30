"""
Configuration and environment helpers.
"""
import os
import shutil
from pathlib import Path
from typing import Optional, Tuple
from dotenv import load_dotenv


def load_env(env_path: Optional[str] = None) -> None:
    """Load environment variables from a .env file if present."""
    if env_path:
        load_dotenv(env_path)
    else:
        load_dotenv()


def get_spotify_credentials() -> Tuple[Optional[str], Optional[str]]:
    """Return SPOTIPY_CLIENT_ID and SPOTIPY_CLIENT_SECRET from env.

    Returns a tuple (client_id, client_secret). Values may be None.
    """
    # Read credentials from environment variables (recommended).
    client_id = os.getenv("SPOTIPY_CLIENT_ID")
    client_secret = os.getenv("SPOTIPY_CLIENT_SECRET")
    return client_id, client_secret


def ensure_ffmpeg_present() -> bool:
    """Check if ffmpeg is installed and available on PATH."""
    return shutil.which("ffmpeg") is not None


def ensure_dirs(base_output: str) -> Tuple[Path, Path]:
    """Ensure `downloads/` and `logs/` exist under project or custom output.

    Returns (downloads_dir, logs_dir)
    """
    base = Path(base_output)
    downloads = base.resolve()
    logs = Path(__file__).resolve().parent.joinpath("logs")
    downloads.mkdir(parents=True, exist_ok=True)
    logs.mkdir(parents=True, exist_ok=True)
    # Ensure downloaded.log exists
    (logs / "downloaded.log").touch(exist_ok=True)
    return downloads, logs
