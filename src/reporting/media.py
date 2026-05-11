from __future__ import annotations
from dataclasses import dataclass
from hashlib import sha1
from io import BytesIO
from pathlib import Path
from typing import Any
from PIL import Image

@dataclass
class MediaAsset:
    path: Path

def _ensure_assets_dir(assets_dir: Path) -> None:
    assets_dir.mkdir(parents=True, exist_ok=True)

def _hash_bytes(raw: bytes) -> str:
    return sha1(raw).hexdigest()[:12]

def save_pil_image(image: Image.Image, assets_dir: Path) -> Path:
    _ensure_assets_dir(assets_dir)
    buf = BytesIO()
    image.save(buf, format='PNG')
    raw = buf.getvalue()
    name = f'img_{_hash_bytes(raw)}.png'
    out = assets_dir / name
    out.write_bytes(raw)
    return out

def save_matplotlib_figure(figure: Any, assets_dir: Path) -> Path:
    _ensure_assets_dir(assets_dir)
    buf = BytesIO()
    figure.savefig(buf, format='png', bbox_inches='tight')
    raw = buf.getvalue()
    name = f'fig_{_hash_bytes(raw)}.png'
    out = assets_dir / name
    out.write_bytes(raw)
    return out

def resolve_media_value(value: Any, assets_dir: Path) -> MediaAsset | None:
    if isinstance(value, (str, Path)):
        return MediaAsset(Path(value))
    if isinstance(value, Image.Image):
        return MediaAsset(save_pil_image(value, assets_dir))
    if value.__class__.__name__ == 'Figure' and value.__class__.__module__.startswith('matplotlib'):
        return MediaAsset(save_matplotlib_figure(value, assets_dir))
    return None

def render_media_markup(asset: MediaAsset, mode: str, var_name: str) -> str:
    path_text = asset.path.as_posix()
    if mode == 'html':
        return f'<img src="{path_text}" alt="{var_name}" />'
    return f'![{var_name}]({path_text})'
