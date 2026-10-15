from __future__ import annotations
import io
from PIL import Image, ImageDraw
from hitbox.schemas import ResolutionResult


def render_visual_receipt(scene_img: Image.Image, result: ResolutionResult) -> bytes:
    """Draws the predicted BBox, center crosshair, and Jev telemetry HUD onto a PNG buffer."""
    annotated = scene_img.convert("RGBA").copy()
    draw = ImageDraw.Draw(annotated)
    w, h = annotated.size

    box = result.bbox
    x1 = (box.xmin / 1000.0) * w
    y1 = (box.ymin / 1000.0) * h
    x2 = (box.xmax / 1000.0) * w
    y2 = (box.ymax / 1000.0) * h
    cx, cy = (x1 + x2) / 2.0, (y1 + y2) / 2.0

    passed = result.is_unobstructed and result.is_visually_enabled and result.confidence >= 0.85
    color = (16, 185, 129, 255) if passed else (239, 68, 68, 255)  # Emerald green vs Red

    # 1. Bounding box & center crosshair
    draw.rectangle([x1, y1, x2, y2], outline=color, width=3)
    r = 6
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=color)
    draw.line([cx - 12, cy, cx + 12, cy], fill=color, width=2)
    draw.line([cx, cy - 12, cx, cy + 12], fill=color, width=2)

    # 2. Telemetry banner above the box
    zoom_tag = " [2x-ZOOM]" if result.used_micro_zoom else ""
    cache_tag = " [L1-CACHE]" if result.cache_hit else ""
    label = (
        f"Jev conf={result.confidence:.2f} | "
        f"unobstructed={result.unobstructed_prob:.2f} | "
        f"enabled={result.enabled_prob:.2f}{zoom_tag}{cache_tag}"
    )

    banner_y = max(0.0, y1 - 22.0)
    draw.rectangle([x1, banner_y, min(w, x1 + len(label) * 6.5), banner_y + 20], fill=color)
    draw.text((x1 + 4, banner_y + 3), label, fill=(255, 255, 255, 255))

    out = io.BytesIO()
    annotated.convert("RGB").save(out, format="PNG")
    return out.getvalue()