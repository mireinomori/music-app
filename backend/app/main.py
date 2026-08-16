from __future__ import annotations

import shutil
import uuid
from pathlib import Path

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from .analyzer import _find_musescore, analyze_audio
from .musicxml import write_demo_xml

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "jobs"
DATA.mkdir(parents=True, exist_ok=True)
app = FastAPI(title="おと譜 API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health():
    return {"ok": True, "local_only": True}


@app.get("/api/capabilities")
def capabilities():
    try:
        from basic_pitch import ICASSP_2022_MODEL_PATH

        basic_pitch = Path(ICASSP_2022_MODEL_PATH).exists()
    except Exception:  # noqa: BLE001 - optional runtime probe
        basic_pitch = False
    return {
        "basic_pitch": basic_pitch,
        "musicxml": True,
        "musescore": _find_musescore() is not None,
        "ffmpeg": shutil.which("ffmpeg") is not None,
        "local_only": True,
    }


@app.post("/api/analyze")
async def analyze(file: UploadFile = File(...), mode: str = Form("auto"), quantize: str = Form("auto")):  # noqa: B008
    job_id = uuid.uuid4().hex
    job_dir = DATA / job_id
    job_dir.mkdir(parents=True)
    incoming = Path(file.filename or "audio")
    input_path = job_dir / f"input{incoming.suffix.lower()}"
    try:
        with input_path.open("wb") as target:
            shutil.copyfileobj(file.file, target)
        result = analyze_audio(input_path, job_dir, quantize)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"解析中に問題が起きました。{exc}") from exc
    return {
        "job_id": job_id,
        "status": "completed",
        "bpm": result.bpm,
        "key": result.key,
        "warning": result.warning,
        "files": {"midi": "midi", "musicxml": "musicxml", "pdf": "pdf", "pdf_available": result.pdf_path is not None},
    }


@app.get("/api/demo-score")
def demo_score():
    path = DATA / "demo" / "score.musicxml"
    write_demo_xml(path)
    return FileResponse(path, media_type="application/vnd.recordare.musicxml+xml")


@app.get("/api/jobs/{job_id}/{kind}")
def download(job_id: str, kind: str):
    names = {"midi": "melody.mid", "musicxml": "score.musicxml", "pdf": "score.pdf"}
    if kind not in names:
        raise HTTPException(status_code=404, detail="出力形式が見つかりません。")
    path = DATA / job_id / names[kind]
    if not path.exists():
        raise HTTPException(status_code=404, detail="この形式のファイルはまだ作成されていません。MuseScoreの導入が必要な場合があります。")
    return FileResponse(path, filename=path.name)
