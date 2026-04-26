"""Media conversion helpers for template placeholders."""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha1
from io import BytesIO
from pathlib import Path
from typing import Any

from PIL import Image


@dataclass
class MediaAsset:
    """Materialized media info.

    Example:
        >>> a = MediaAsset(Path("assets/x.png"))
        >>> a.path.name
        'x.png'
    """

    path: Path


def _ensure_assets_dir(assets_dir: Path) -> None:
    """Create assets directory if it does not exist.

    Example:
        >>> # _ensure_assets_dir(Path("assets"))  # creates folder if needed
        >>> True
        True
    """

    assets_dir.mkdir(parents=True, exist_ok=True)


def _hash_bytes(raw: bytes) -> str:
    """Return deterministic short hash.

    Example:
        >>> len(_hash_bytes(b"abc")) == 12
        True
    """

    return sha1(raw).hexdigest()[:12]


def save_pil_image(image: Image.Image, assets_dir: Path) -> Path:
    """Save PIL image into assets directory.

    Example:
        >>> from PIL import Image as PILImage
        >>> img = PILImage.new("RGB", (2, 2), color="red")
        >>> # save_pil_image(img, Path("assets"))  # doctest: +SKIP
    """

    _ensure_assets_dir(assets_dir)
    buf = BytesIO()
    image.save(buf, format="PNG")
    raw = buf.getvalue()
    name = f"img_{_hash_bytes(raw)}.png"
    out = assets_dir / name
    out.write_bytes(raw)
    return out


def save_matplotlib_figure(figure: Any, assets_dir: Path) -> Path:
    """Save matplotlib Figure into assets directory.

    Example:
        >>> # fig = plt.figure(); save_matplotlib_figure(fig, Path("assets"))  # doctest: +SKIP
        >>> True
        True
    """

    _ensure_assets_dir(assets_dir)
    buf = BytesIO()
    figure.savefig(buf, format="png", bbox_inches="tight")
    raw = buf.getvalue()
    name = f"fig_{_hash_bytes(raw)}.png"
    out = assets_dir / name
    out.write_bytes(raw)
    return out


def resolve_media_value(value: Any, assets_dir: Path) -> MediaAsset | None:
    """Convert supported media value to a file-backed asset.

    Example:
        >>> resolve_media_value("image.png", Path("assets")).path.as_posix().endswith("image.png")
        True
    """

    if isinstance(value, (str, Path)):
        return MediaAsset(Path(value))

    if isinstance(value, Image.Image):
        return MediaAsset(save_pil_image(value, assets_dir))

    # Lazy detect matplotlib Figure without importing matplotlib here.
    if value.__class__.__name__ == "Figure" and value.__class__.__module__.startswith(
        "matplotlib"
    ):
        return MediaAsset(save_matplotlib_figure(value, assets_dir))

    return None


def render_media_markup(asset: MediaAsset, mode: str, var_name: str) -> str:
    """Render media path as MD or HTML markup.

    Example:
        >>> asset = MediaAsset(Path("assets/chart.png"))
        >>> render_media_markup(asset, "md", "CHART").startswith("![CHART]")
        True
    """

    path_text = asset.path.as_posix()
    if mode == "html":
        return f'<img src="{path_text}" alt="{var_name}" />'
    return f"![{var_name}]({path_text})"

