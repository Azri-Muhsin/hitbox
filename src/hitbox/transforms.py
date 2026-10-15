from __future__ import annotations
import base64
import io
from PIL import Image
from hitbox.schemas import NormalizedBBox


def image_to_data_url(img: Image.Image, fmt: str = "JPEG", quality: int = 85) -> str:
    """Encodes a Pillow Image into a base64 data URI for /v1/systemone."""
    buf = io.BytesIO()
    save_img = img.convert("RGB") if fmt.upper() == "JPEG" else img
    save_img.save(buf, format=fmt, quality=quality)
    b64 = base64.b64encode(buf.getvalue()).decode("utf-8")
    mime = "image/jpeg" if fmt.upper() == "JPEG" else "image/png"
    return f"data:{mime};base64,{b64}"


def extract_micro_zoom_crop(
    scene_img: Image.Image,
    coarse_box: NormalizedBBox,
    padding_factor: float = 2.0,
) -> tuple[Image.Image, tuple[int, int, int, int]]:
    """
    Crops a high-resolution padded window around a candidate bbox.
    Returns (cropped_image, (crop_left, crop_top, crop_w, crop_h)) in physical pixels.
    """
    img_w, img_h = scene_img.size

    box_w = ((coarse_box.xmax - coarse_box.xmin) / 1000.0) * img_w
    box_h = ((coarse_box.ymax - coarse_box.ymin) / 1000.0) * img_h
    cx = ((coarse_box.xmin + coarse_box.xmax) / 2000.0) * img_w
    cy = ((coarse_box.ymin + coarse_box.ymax) / 2000.0) * img_h

    # Enforce at least a 256x256 pixel context window so Jev keeps spatial landmarks
    half_w = max(128.0, (box_w * padding_factor) / 2.0)
    half_h = max(128.0, (box_h * padding_factor) / 2.0)

    left = max(0, int(cx - half_w))
    top = max(0, int(cy - half_h))
    right = min(img_w, int(cx + half_w))
    bottom = min(img_h, int(cy + half_h))

    crop_w = max(1, right - left)
    crop_h = max(1, bottom - top)

    return scene_img.crop((left, top, right, bottom)), (left, top, crop_w, crop_h)


def reproject_zoom_bbox_to_global(
    local_box: NormalizedBBox,
    crop_bounds: tuple[int, int, int, int],
    full_img_size: tuple[int, int],
) -> NormalizedBBox:
    """
    Affine transformation mapping a [0, 1000] bbox predicted inside a cropped
    window back into the global [0, 1000] coordinate space of the full viewport.
    """
    left, top, crop_w, crop_h = crop_bounds
    full_w, full_h = full_img_size

    global_xmin = ((left + (local_box.xmin / 1000.0) * crop_w) / full_w) * 1000.0
    global_xmax = ((left + (local_box.xmax / 1000.0) * crop_w) / full_w) * 1000.0
    global_ymin = ((top + (local_box.ymin / 1000.0) * crop_h) / full_h) * 1000.0
    global_ymax = ((top + (local_box.ymax / 1000.0) * crop_h) / full_h) * 1000.0

    return NormalizedBBox(
        ymin=round(min(1000.0, max(0.0, global_ymin)), 2),
        xmin=round(min(1000.0, max(0.0, global_xmin)), 2),
        ymax=round(min(1000.0, max(0.0, global_ymax)), 2),
        xmax=round(min(1000.0, max(0.0, global_xmax)), 2),
    )