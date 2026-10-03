from __future__ import annotations

from pathlib import Path

import numpy as np
import torch
from PIL import Image
from spandrel import ImageModelDescriptor, ModelLoader

ROOT = Path(__file__).resolve().parent.parent
WEIGHTS_PATH = ROOT / "weights" / "RealESRGAN_x4plus_anime_6B.pth"

# Tile size keeps VRAM/RAM usage bounded for larger images.
TILE_SIZE = 256
TILE_PAD = 10


def _pick_device() -> torch.device:
    if torch.backends.mps.is_available():
        return torch.device("mps")
    if torch.cuda.is_available():
        return torch.device("cuda")
    return torch.device("cpu")


class AnimeUpscaler:
    """4x RealESRGAN anime (6B) upscaler via Spandrel."""

    def __init__(self, weights: Path = WEIGHTS_PATH) -> None:
        if not weights.is_file():
            raise FileNotFoundError(
                f"Model weights not found: {weights}\n"
                "They should ship with this repo at weights/RealESRGAN_x4plus_anime_6B.pth.\n"
                "Fallback download: "
                "https://github.com/xinntao/Real-ESRGAN/releases/download/v0.2.2.4/RealESRGAN_x4plus_anime_6B.pth"
            )
        self.device = _pick_device()
        loaded = ModelLoader().load_from_file(str(weights))
        if not isinstance(loaded, ImageModelDescriptor):
            raise TypeError(f"Unexpected model type: {type(loaded)}")
        self.model = loaded.to(self.device).eval()
        self.scale = int(self.model.scale)

    @torch.inference_mode()
    def upscale(self, image: Image.Image) -> Image.Image:
        rgb = image.convert("RGB")
        arr = np.asarray(rgb, dtype=np.float32) / 255.0
        tensor = torch.from_numpy(arr).permute(2, 0, 1).unsqueeze(0).to(self.device)

        h, w = tensor.shape[2], tensor.shape[3]
        if max(h, w) <= TILE_SIZE:
            out = self.model(tensor)
        else:
            out = self._tiled(tensor)

        out = out.clamp(0.0, 1.0).squeeze(0).permute(1, 2, 0).cpu().numpy()
        out_u8 = (out * 255.0).round().astype(np.uint8)
        return Image.fromarray(out_u8, mode="RGB")

    def _tiled(self, tensor: torch.Tensor) -> torch.Tensor:
        """Process large images in overlapping tiles."""
        _, _, height, width = tensor.shape
        scale = self.scale
        output = torch.zeros(
            (1, 3, height * scale, width * scale),
            dtype=tensor.dtype,
            device=tensor.device,
        )

        tiles_x = (width + TILE_SIZE - 1) // TILE_SIZE
        tiles_y = (height + TILE_SIZE - 1) // TILE_SIZE

        for ty in range(tiles_y):
            for tx in range(tiles_x):
                x0 = tx * TILE_SIZE
                y0 = ty * TILE_SIZE
                x1 = min(x0 + TILE_SIZE, width)
                y1 = min(y0 + TILE_SIZE, height)

                ox0 = max(x0 - TILE_PAD, 0)
                oy0 = max(y0 - TILE_PAD, 0)
                ox1 = min(x1 + TILE_PAD, width)
                oy1 = min(y1 + TILE_PAD, height)

                tile = tensor[:, :, oy0:oy1, ox0:ox1]
                up = self.model(tile)

                # Crop padding back to the core tile region.
                left = (x0 - ox0) * scale
                top = (y0 - oy0) * scale
                right = left + (x1 - x0) * scale
                bottom = top + (y1 - y0) * scale
                output[:, :, y0 * scale : y1 * scale, x0 * scale : x1 * scale] = up[
                    :, :, top:bottom, left:right
                ]

        return output


_upscaler: AnimeUpscaler | None = None


def get_upscaler() -> AnimeUpscaler:
    global _upscaler
    if _upscaler is None:
        _upscaler = AnimeUpscaler()
    return _upscaler
