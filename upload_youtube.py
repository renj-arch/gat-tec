import sys, os, json, pickle, random
from pathlib import Path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from src.viral_seo import generate_viral_title, generate_viral_description, generate_viral_tags, generate_viral_hashtags, CHANNEL_HANDLE
from src.keywords import get_youtube_category

SCOPES = ["https://www.googleapis.com/auth/youtube"]
CLIENT_SECRET = "client_secret.json"
TOKEN_FILE = "token.pickle"
PERF_FILE = Path(__file__).parent / "performance.json"

PLAYLISTS = {
    "comparisons": {
        "name": "Tech Comparisons",
        "desc": "Honest side-by-side tech comparisons. Which one should you buy? We break it down.",
    },
}


def get_service():
    creds = None
    if Path(TOKEN_FILE).exists():
        with open(TOKEN_FILE, "rb") as f:
            creds = pickle.load(f)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_FILE, "wb") as f:
            pickle.dump(creds, f)
    return build("youtube", "v3", credentials=creds)


def get_or_create_playlist(youtube, playlist_key: str = "comparisons") -> str:
    info = PLAYLISTS.get(playlist_key, PLAYLISTS["comparisons"])
    request = youtube.playlists().list(part="snippet", mine=True, maxResults=50)
    response = request.execute()
    for item in response.get("items", []):
        if item["snippet"]["title"] == info["name"]:
            print(f"  Playlist found: {info['name']}")
            return item["id"]

    body = {
        "snippet": {
            "title": info["name"],
            "description": info["desc"],
        },
        "status": {"privacyStatus": "public"},
    }
    result = youtube.playlists().insert(part="snippet,status", body=body).execute()
    print(f"  Playlist created: {info['name']}")
    return result["id"]


def add_to_playlist(youtube, playlist_id: str, video_id: str, playlist_key: str = "comparisons"):
    info = PLAYLISTS.get(playlist_key, PLAYLISTS["comparisons"])
    body = {
        "snippet": {
            "playlistId": playlist_id,
            "resourceId": {"kind": "youtube#video", "videoId": video_id},
        }
    }
    youtube.playlistItems().insert(part="snippet", body=body).execute()
    print(f"  Added to playlist: {info['name']}")


def log_performance(video_id: str, title: str, mode: str):
    from datetime import datetime
    perf = {"videos": []}
    if PERF_FILE.exists():
        perf = json.loads(PERF_FILE.read_text())
    perf["videos"].append({
        "video_id": video_id,
        "title": title,
        "mode": mode,
        "uploaded_at": datetime.now().isoformat(),
    })
    PERF_FILE.write_text(json.dumps(perf, indent=2))


def upload(video_path: str, title: str = "", description: str = "", tags: list[str] = None,
           privacy: str = "public", playlist_key: str = "comparisons", made_for_kids: bool = False,
           mode: str = "comparisons", script_data: dict = None):
    youtube = get_service()

    if script_data and not title:
        title = generate_viral_title(mode, script_data)
    if script_data and not description:
        description = generate_viral_description(mode, script_data)
        hashtags = generate_viral_hashtags(mode)
        description += f"\n\n{hashtags}"
    if script_data and not tags:
        tags = generate_viral_tags(mode, script_data)
    if not title:
        title = "Tech Comparison #Shorts"
    if not description:
        description = f"Subscribe for more tech comparisons! {CHANNEL_HANDLE}\n#shorts"
    if not tags:
        tags = ["shorts", "comparison", "techreview"]

    cat_id = {"education": "27", "entertainment": "24", "howto": "26"}.get(get_youtube_category(mode), "22")
    body = {
        "snippet": {
            "title": title,
            "description": description,
            "tags": tags,
            "categoryId": cat_id,
        },
        "status": {
            "privacyStatus": privacy,
            "selfDeclaredMadeForKids": made_for_kids,
        },
    }

    media = MediaFileUpload(video_path, chunksize=-1, resumable=True)
    print(f"\n  Uploading: {title[:60]}...")
    print(f"   Mode: {mode.upper()} | Tags: {len(tags)}")
    request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)
    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"   {int(status.progress() * 100)}%")
    video_id = response["id"]
    print(f"  Uploaded! https://youtu.be/{video_id}")

    try:
        playlist_id = get_or_create_playlist(youtube, playlist_key)
        add_to_playlist(youtube, playlist_id, video_id, playlist_key)
    except Exception as e:
        print(f"   Playlist skipped: {e}")

    log_performance(video_id, title, mode)

    print(f"   Channel: https://youtube.com/{CHANNEL_HANDLE}")
    return video_id


if __name__ == "__main__":
    mp4s = sorted(Path("output").glob("*.mp4"), key=lambda p: p.stat().st_mtime, reverse=True)
    if not mp4s:
        print("No MP4 files in output/")
        exit(1)
    video = str(mp4s[0])
    upload(
        video_path=video,
        title="iPhone 16 vs Samsung S25 — Which Wins?",
        description="Honest tech comparison.\n#shorts #techreview",
        tags=["tech", "comparison", "shorts"],
        privacy="public",
    )
