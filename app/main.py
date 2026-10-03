from __future__ import annotations

import logging
import re
import uuid
from pathlib import Path
from typing import Annotated

from fastapi import FastAPI, File, HTTPException, Request, UploadFile
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from PIL import Image

from app.i18n import locale_from_request, t
from app.upscaler import get_upscaler

logger = logging.getLogger(__name__)

ROOT = Path(__file__).resolve().parent.parent
UPLOAD_DIR = ROOT / "data" / "uploads"
OUTPUT_DIR = ROOT / "data" / "outputs"
STATIC_DIR = Path(__file__).resolve().parent / "static"
TEMPLATE = Path(__file__).resolve().parent / "templates" / "index.html"
NOTICE_FILE = ROOT / "NOTICE"
LICENSE_FILE = ROOT / "LICENSE"

APP_VERSION = "0.1.0"
ALLOWED_EXT = {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".gif"}
JOB_ID_RE = re.compile(r"^[a-f0-9]{12}$")
MAX_UPLOAD_BYTES = 25 * 1024 * 1024
MAX_INPUT_SIDE = 4096

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR_RESOLVED = OUTPUT_DIR.resolve()

app = FastAPI(title="Anime Image Upscaler", version=APP_VERSION)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
app.mount("/outputs", StaticFiles(directory=OUTPUT_DIR), name="outputs")
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")


def _output_path_for(job_id: str) -> Path:
    path = (OUTPUT_DIR / f"{job_id}_4x.png").resolve()
    if not path.is_relative_to(OUTPUT_DIR_RESOLVED):
        raise HTTPException(status_code=400, detail="invalid path")
    return path


@app.get("/", response_class=HTMLResponse)
async def index() -> HTMLResponse:
    return HTMLResponse(TEMPLATE.read_text(encoding="utf-8"))


@app.get("/NOTICE", response_class=FileResponse)
async def notice(request: Request) -> FileResponse:
    if not NOTICE_FILE.is_file():
        raise HTTPException(
            status_code=404,
            detail=t("notice_not_found", locale_from_request(request)),
        )
    return FileResponse(NOTICE_FILE, media_type="text/plain; charset=utf-8")


@app.get("/LICENSE", response_class=FileResponse)
async def license_file(request: Request) -> FileResponse:
    if not LICENSE_FILE.is_file():
        raise HTTPException(
            status_code=404,
            detail=t("license_not_found", locale_from_request(request)),
        )
    return FileResponse(LICENSE_FILE, media_type="text/plain; charset=utf-8")


@app.get("/health")
async def health() -> dict[str, str]:
    from app import upscaler as upscaler_mod

    payload = {
        "status": "ok",
        "model": "RealESRGAN_x4plus_anime_6B",
        "scale": "4x",
        "version": APP_VERSION,
        "attribution": "Model by xinntao/Real-ESRGAN (BSD-3-Clause). Not affiliated.",
        "notice_url": "/NOTICE",
    }
    if upscaler_mod._upscaler is None:
        return {**payload, "device": "lazy"}
    upscaler = upscaler_mod._upscaler
    return {
        **payload,
        "scale": f"{upscaler.scale}x",
        "device": str(upscaler.device),
    }


@app.post("/api/upscale")
async def upscale(
    request: Request,
    file: Annotated[UploadFile, File()],
) -> dict[str, object]:
    locale = locale_from_request(request)

    if not file.filename:
        raise HTTPException(status_code=400, detail=t("file_missing", locale))

    suffix = Path(file.filename).suffix.lower()
    if suffix not in ALLOWED_EXT:
        raise HTTPException(
            status_code=400,
            detail=t(
                "unsupported_format",
                locale,
                exts=", ".join(sorted(ALLOWED_EXT)),
            ),
        )

    job_id = uuid.uuid4().hex[:12]
    in_path = UPLOAD_DIR / f"{job_id}{suffix}"
    out_path = OUTPUT_DIR / f"{job_id}_4x.png"

    raw = await file.read()
    if not raw:
        raise HTTPException(status_code=400, detail=t("empty_file", locale))
    if len(raw) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=400, detail=t("file_too_large", locale))

    in_path.write_bytes(raw)

    try:
        with Image.open(in_path) as img:
            img.load()
            src_w, src_h = img.size
            if max(src_w, src_h) > MAX_INPUT_SIDE:
                raise HTTPException(
                    status_code=400,
                    detail=t("image_too_large", locale, max_side=MAX_INPUT_SIDE),
                )
            result = get_upscaler().upscale(img)
            result.save(out_path, format="PNG", optimize=True)
            out_w, out_h = result.size
    except HTTPException:
        in_path.unlink(missing_ok=True)
        out_path.unlink(missing_ok=True)
        raise
    except Exception as exc:  # noqa: BLE001 — keep UI message generic
        in_path.unlink(missing_ok=True)
        out_path.unlink(missing_ok=True)
        logger.exception("Upscale failed for job %s", job_id)
        raise HTTPException(
            status_code=500,
            detail=t("upscale_failed", locale),
        ) from exc

    return {
        "id": job_id,
        "before_url": f"/uploads/{in_path.name}",
        "after_url": f"/outputs/{out_path.name}",
        "before_size": {"w": src_w, "h": src_h},
        "after_size": {"w": out_w, "h": out_h},
        "scale": get_upscaler().scale,
        "model": "RealESRGAN_x4plus_anime_6B",
    }


@app.get("/api/download/{job_id}")
async def download(job_id: str, request: Request) -> FileResponse:
    locale = locale_from_request(request)
    if not JOB_ID_RE.fullmatch(job_id):
        raise HTTPException(status_code=400, detail=t("invalid_job_id", locale))

    path = _output_path_for(job_id)
    if not path.is_file():
        raise HTTPException(status_code=404, detail=t("result_not_found", locale))
    return FileResponse(path, filename=f"{job_id}_4x.png", media_type="image/png")
