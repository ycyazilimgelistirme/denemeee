import json
import time
from pathlib import Path
from yt_dlp import YoutubeDL

ID_FILE = "ids.txt"
OUTPUT_FILE = "links.json"

ydl_opts = {
    "quiet": True,
    "format": "bestaudio/best",
    "noplaylist": True,
    "skip_download": True,
    "forcejson": True,
}

# JSON yükle veya boş dict oluştur
if Path(OUTPUT_FILE).exists():
    try:
        with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError:
        data = {}
else:
    data = {}

while True:
    with open(ID_FILE, "r", encoding="utf-8") as f:
        ids = [line.strip() for line in f if line.strip()]

    total = len(ids)
    for index, video_id in enumerate(ids, start=1):
        try:
            print(f"[{index}/{total}] İşleniyor: {video_id}...")

            url = f"https://www.youtube.com/watch?v={video_id}"
            with YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)

            # Ham ses linki
            audio_url = info.get("url")
            # En yüksek çözünürlüklü kapak
            thumbnails = info.get("thumbnails", [])
            max_thumb = max(thumbnails, key=lambda t: t.get("width", 0)) if thumbnails else None
            thumb_url = max_thumb["url"] if max_thumb else None

            # Albüm bilgisi (yoksa boş string)
            album = info.get("album") or info.get("playlist") or ""

            # Meta veriler
            meta = {
                "title": info.get("title"),
                "uploader": info.get("uploader"),
                "duration": info.get("duration"),
                "audio_url": audio_url,
                "thumbnail_url": thumb_url,
                "album": album
            }

            data[video_id] = meta

            # JSON kaydet
            with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)

            print(f"[{index}/{total}] Başarılı: {video_id} -> {meta['title']} (Albüm: {album})")

        except Exception as e:
            print(f"[{index}/{total}] Hata: {video_id} -> {e}")

    print("Liste bitti, 10 saniye sonra baştan başlıyor...")
    time.sleep(10)
