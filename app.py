import os
import re
import sys
import uuid
import glob
import logging
import subprocess
import threading
import time
import traceback
from flask import Flask, render_template, request, jsonify, send_file

from pytubefix import YouTube

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DOWNLOAD_DIR = os.path.join(BASE_DIR, "downloads")
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

FFMPEG_TIMEOUT = 300  # 초

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    stream=sys.stdout,
)
logger = logging.getLogger("ymp3")

# 진행 상태 저장
tasks = {}


def cleanup_old_files(max_age_seconds=3600):
    """1시간 이상 된 파일 및 task 레코드 삭제"""
    now = time.time()
    for f in glob.glob(os.path.join(DOWNLOAD_DIR, "*")):
        if now - os.path.getmtime(f) > max_age_seconds:
            os.remove(f)
    for tid in [t for t, v in tasks.items()
                if now - v.get("created_at", now) > max_age_seconds]:
        tasks.pop(tid, None)


def is_valid_youtube_url(url):
    pattern = r"^(https?://)?(www\.)?(youtube\.com/watch\?v=|youtu\.be/|youtube\.com/shorts/)[\w-]+"
    return re.match(pattern, url) is not None


def on_progress(stream, chunk, bytes_remaining):
    task_id = getattr(stream, "_task_id", None)
    if task_id and task_id in tasks:
        total = stream.filesize
        downloaded = total - bytes_remaining
        tasks[task_id]["progress"] = round(downloaded / total * 100, 1)


def _run_ffmpeg(audio_path, mp3_path, title, author):
    """subprocess.run + timeout 으로 hang 방지. communicate() 기반이라 파이프 데드락 없음."""
    return subprocess.run(
        [
            "ffmpeg", "-nostdin", "-i", audio_path, "-vn", "-q:a", "0",
            "-metadata", f"title={title}",
            "-metadata", f"artist={author}",
            "-y", mp3_path,
        ],
        stdin=subprocess.DEVNULL,
        capture_output=True,
        text=True,
        timeout=FFMPEG_TIMEOUT,
    )


def download_worker(task_id, url):
    audio_path = None
    try:
        logger.info("[%s] start url=%s", task_id, url)
        tasks[task_id]["status"] = "downloading"

        yt = YouTube(url, on_progress_callback=on_progress)
        title = yt.title
        tasks[task_id]["title"] = title
        logger.info("[%s] title=%s", task_id, title)

        stream = yt.streams.get_audio_only()
        if stream is None:
            raise RuntimeError("오디오 스트림을 찾을 수 없습니다.")
        stream._task_id = task_id

        audio_filename = f"{task_id}_audio"
        audio_path = stream.download(output_path=DOWNLOAD_DIR, filename=audio_filename)
        logger.info("[%s] downloaded -> %s", task_id, audio_path)

        # ffmpeg로 MP3 변환 (원본 음질 유지)
        tasks[task_id]["status"] = "converting"
        tasks[task_id]["progress"] = 100

        mp3_path = os.path.join(DOWNLOAD_DIR, f"{task_id}.mp3")
        author = yt.author or ""

        try:
            result = _run_ffmpeg(audio_path, mp3_path, title, author)
        except subprocess.TimeoutExpired:
            tasks[task_id]["status"] = "error"
            tasks[task_id]["error"] = f"MP3 변환 시간 초과({FFMPEG_TIMEOUT}s)"
            logger.error("[%s] ffmpeg timeout", task_id)
            return
        finally:
            if audio_path and os.path.exists(audio_path):
                os.remove(audio_path)

        if result.returncode == 0 and os.path.exists(mp3_path):
            tasks[task_id]["status"] = "done"
            tasks[task_id]["file"] = mp3_path
            logger.info("[%s] done", task_id)
        else:
            tasks[task_id]["status"] = "error"
            tasks[task_id]["error"] = f"MP3 변환 실패 (code={result.returncode})"
            logger.error("[%s] ffmpeg failed code=%s stderr=%s",
                         task_id, result.returncode, (result.stderr or "")[-2000:])

    except Exception as e:
        tasks[task_id]["status"] = "error"
        tasks[task_id]["error"] = str(e)
        logger.error("[%s] worker error: %s\n%s", task_id, e, traceback.format_exc())
        if audio_path and os.path.exists(audio_path):
            try:
                os.remove(audio_path)
            except OSError:
                pass


@app.route("/")
def index():
    cleanup_old_files()
    return render_template("index.html")


@app.route("/api/download", methods=["POST"])
def start_download():
    data = request.get_json()
    url = data.get("url", "").strip()

    if not url:
        return jsonify({"error": "URL을 입력해주세요."}), 400

    if not is_valid_youtube_url(url):
        return jsonify({"error": "유효한 유튜브 URL이 아닙니다."}), 400

    task_id = uuid.uuid4().hex
    tasks[task_id] = {
        "status": "queued", "progress": 0, "title": "",
        "file": None, "error": None, "created_at": time.time(),
    }

    thread = threading.Thread(target=download_worker, args=(task_id, url), daemon=True)
    thread.start()

    return jsonify({"task_id": task_id})


@app.route("/api/status/<task_id>")
def check_status(task_id):
    task = tasks.get(task_id)
    if not task:
        return jsonify({"error": "존재하지 않는 작업입니다."}), 404
    return jsonify(task)


@app.route("/api/file/<task_id>")
def download_file(task_id):
    task = tasks.get(task_id)
    if not task or task["status"] != "done":
        return jsonify({"error": "파일이 준비되지 않았습니다."}), 404

    safe_title = re.sub(r'[\\/*?:"<>|]', "", task["title"])
    return send_file(task["file"], as_attachment=True, download_name=f"{safe_title}.mp3")


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=False, port=5001)
