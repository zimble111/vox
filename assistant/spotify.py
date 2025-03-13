import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import subprocess
from .config import CONFIG

# Инициализация Spotipy с использованием Client Credentials
client_id = CONFIG.get("spotify_client_id")
client_secret = CONFIG.get("spotify_client_secret")

sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
    client_id=client_id,
    client_secret=client_secret
))

def search_track(query):
    """
    Ищет трек по запросу через Spotify Web API и возвращает URI первого найденного трека.
    Если трек не найден, возвращает None.
    """
    results = sp.search(q=query, type="track", limit=1)
    tracks = results.get("tracks", {}).get("items", [])
    if tracks:
        return tracks[0]["uri"]
    return None

def play_track_applescript(track_uri):
    """
    Запускает воспроизведение трека в Spotify через AppleScript.
    track_uri должен быть в формате, например, "spotify:track:6RtPijgfPKROxEzTHNRiDp".
    """
    script = f'tell application "Spotify" to play track "{track_uri}"'
    subprocess.run(["osascript", "-e", script])
