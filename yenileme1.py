import json
import time
import threading
from pathlib import Path
from yt_dlp import YoutubeDL
from flask import Flask, render_template, request, redirect, url_for, jsonify

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

app = Flask(__name__)

# ----- YouTube ID işleme fonksiyonu -----
def process_ids():
    while True:
        if Path(ID_FILE).exists():
            with open(ID_FILE, "r", encoding="utf-8") as f:
                ids = [line.strip() for line in f if line.strip()]
        else:
            ids = []

        total = len(ids)
        for index, video_id in enumerate(ids, start=1):
            if video_id in data:
                continue  # Daha önce işlenmiş
            try:
                print(f"[{index}/{total}] İşleniyor: {video_id}...")
                url = f"https://www.youtube.com/watch?v={video_id}"
                with YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=False)

                audio_url = info.get("url")
                thumbnails = info.get("thumbnails", [])
                max_thumb = max(thumbnails, key=lambda t: t.get("width", 0)) if thumbnails else None
                thumb_url = max_thumb["url"] if max_thumb else None
                album = info.get("album") or info.get("playlist") or ""

                meta = {
                    "title": info.get("title"),
                    "uploader": info.get("uploader"),
                    "duration": info.get("duration"),
                    "audio_url": audio_url,
                    "thumbnail_url": thumb_url,
                    "album": album
                }

                data[video_id] = meta

                with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=4)

                print(f"[{index}/{total}] Başarılı: {video_id} -> {meta['title']}")

            except Exception as e:
                print(f"[{index}/{total}] Hata: {video_id} -> {e}")

        time.sleep(10)  # 10 saniye bekle

# Thread olarak başlat
threading.Thread(target=process_ids, daemon=True).start()


# ----- Admin Paneli -----
@app.route("/")
def index():
    return render_template("index.html", data=data)


@app.route("/add_id", methods=["POST"])
def add_id():
    new_id = request.form.get("video_id")
    if new_id and new_id not in data:
        with open(ID_FILE, "a", encoding="utf-8") as f:
            f.write(new_id + "\n")
    return redirect(url_for("index"))


@app.route("/api/data")
def api_data():
    return jsonify(data)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
