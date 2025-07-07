import os
import time
import json
import sys
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from dotenv import load_dotenv

load_dotenv()

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=os.getenv("SPOTIPY_CLIENT_ID"),
    client_secret=os.getenv("SPOTIPY_CLIENT_SECRET"),
    redirect_uri=os.getenv("SPOTIPY_REDIRECT_URI"),
    scope="playlist-read-private"))

def get_youtube_service():
    flow = InstalledAppFlow.from_client_secrets_file(
        "client_secret_google.json",
        scopes=["https://www.googleapis.com/auth/youtube"]
    )
    credentials = flow.run_local_server(port=8080, open_browser=True)
    return build("youtube", "v3", credentials=credentials)

youtube = get_youtube_service()

CACHE_FILE = "yt_cache.json"
PROGRESS_FILE = "progress.json"

if os.path.exists(CACHE_FILE):
    try:
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            yt_cache = json.load(f)
    except json.JSONDecodeError:
        yt_cache = {}
else:
    yt_cache = {}

if os.path.exists(PROGRESS_FILE):
    try:
        with open(PROGRESS_FILE, "r", encoding="utf-8") as f:
            progress = json.load(f)
    except json.JSONDecodeError:
        progress = {}
else:
    progress = {}

def save_cache():
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(yt_cache, f, indent=2, ensure_ascii=False)

def save_progress():
    with open(PROGRESS_FILE, "w", encoding="utf-8") as f:
        json.dump(progress, f, indent=2, ensure_ascii=False)

def search_youtube_video(query):
    if query in yt_cache:
        print(f"♻️ Cache usado para: {query}")
        return yt_cache[query]

    try:
        results = youtube.search().list(
            q=query,
            part="snippet",
            maxResults=1,
            type="video"
        ).execute()
        items = results.get("items", [])
        if not items:
            yt_cache[query] = None
        else:
            video_id = items[0]["id"]["videoId"]
            yt_cache[query] = video_id
        save_cache()
        return yt_cache[query]

    except HttpError as e:
        error_content = e.content.decode()
        print(f"❌ Error en búsqueda YouTube: {e}")

        if e.resp.status == 401:
            print("🔐 Token inválido o caducado. Cerrando script.")
            sys.exit(1)

        if e.resp.status == 403:
            if "quotaExceeded" in error_content:
                print("🚫 Se ha superado la cuota diaria de la API de YouTube. Vuelve a intentarlo mañana.")
                sys.exit(1)
            elif "userRateLimitExceeded" in error_content:
                print("⚠️ Se alcanzó el límite de peticiones por segundo. Esperando 60s...")
                time.sleep(60)
                return None

        return None

def create_youtube_playlist(title, description=""):
    playlist = youtube.playlists().insert(
        part="snippet,status",
        body={
            "snippet": {"title": title, "description": description},
            "status": {"privacyStatus": "private"}
        }
    ).execute()
    return playlist["id"]

def get_youtube_playlist_videos(playlist_id):
    videos = []
    nextPageToken = None

    while True:
        request = youtube.playlistItems().list(
            part="snippet",
            playlistId=playlist_id,
            maxResults=50,
            pageToken=nextPageToken
        )
        response = request.execute()

        for item in response.get("items", []):
            title = item["snippet"]["title"]
            videos.append(title)

        nextPageToken = response.get("nextPageToken")
        if not nextPageToken:
            break

    return videos

def add_video_to_youtube_playlist(playlist_id, video_id, retries=3):
    for attempt in range(retries):
        try:
            youtube.playlistItems().insert(
                part="snippet",
                body={
                    "snippet": {
                        "playlistId": playlist_id,
                        "resourceId": {"kind": "youtube#video", "videoId": video_id}
                    }
                }
            ).execute()
            return True
        except HttpError as e:
            print(f"Error al añadir video: {e}")
            if attempt < retries - 1:
                print("Reintentando en 5 segundos...")
                time.sleep(5)
            else:
                print("No se pudo añadir el video tras varios intentos.")
                return False

def clone_playlists():
    playlists = sp.current_user_playlists()
    for playlist in playlists["items"]:
        name = playlist["name"]

        if name in progress:
            yt_playlist_id = progress[name]["yt_playlist_id"]
            print(f"\n♻️ Continuando playlist: {name}")
        else:
            print(f"\n📀 Creando playlist: {name}")
            yt_playlist_id = create_youtube_playlist(name)
            progress[name] = {
                "yt_playlist_id": yt_playlist_id,
                "tracks_added": []
            }
            save_progress()

        # Leer canciones ya presentes en la playlist de YouTube
        yt_existing_tracks = set(get_youtube_playlist_videos(yt_playlist_id))

        tracks = sp.playlist_tracks(playlist["id"])
        while tracks:
            for item in tracks["items"]:
                track = item["track"]
                if not track:
                    continue
                title = f"{track['name']} {track['artists'][0]['name']}"

                if title in yt_existing_tracks:
                    print(f"⚠️ Saltando canción ya presente en YouTube: {title}")
                    continue

                if title in progress[name]["tracks_added"]:
                    print(f"⚠️ Saltando canción registrada: {title}")
                    continue

                print(f"🎵 Buscando: {title}")
                video_id = search_youtube_video(title)
                if video_id:
                    if add_video_to_youtube_playlist(yt_playlist_id, video_id):
                        print(f"✅ Añadido: {title}")
                        progress[name]["tracks_added"].append(title)
                        save_progress()
                    else:
                        print(f"❌ Error al añadir: {title}")
                else:
                    print(f"❌ No encontrado: {title}")
                time.sleep(1)

            # Comprobar si hay más páginas en Spotify
            if tracks.get("next"):
                tracks = sp.next(tracks)
            else:
                break

if __name__ == "__main__":
    clone_playlists()
