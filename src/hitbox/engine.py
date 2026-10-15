from __future__ import annotations
import io
from pathlib import Path
from typing import Any, Callable
from PIL import Image

from hitbox.adapters.base import BrowserAdapter
from hitbox.annotator import render_visual_receipt
from hitbox.cache import PerceptualBBoxCache
from hitbox.client import JevVisionClient
from hitbox.schemas import HitboxActionabilityError, ResolutionResult
from hitbox.transforms import extract_micro_zoom_crop, reproject_zoom_bbox_to_global


class VisualTargetHandle:
    """Fluent handle returned by hitbox.locate_by_image() or hitbox.locate_by_description()."""

    def __init__(
        self,
        engine: HitboxEngine,
        *,
        reference_image_path: str | Path | None = None,
        description: str | None = None,
        context: dict[str, Any] | None = None,
        confidence_gate: float = 0.88,
        zoom_threshold: float = 0.70,
    ):
        self.engine = engine
        self.reference_image_path = Path(reference_image_path) if reference_image_path else None
        self.description = description
        self.context = context
        self.confidence_gate = confidence_gate
        self.zoom_threshold = zoom_threshold

    def resolve(self) -> tuple[ResolutionResult, tuple[float, float]]:
        """Resolves the target bounding box and returns (ResolutionResult, (css_x, css_y))."""
        return self.engine._resolve_target(
            reference_image_path=self.reference_image_path,
            description=self.description,
            context=self.context,
            confidence_gate=self.confidence_gate,
            zoom_threshold=self.zoom_threshold,
        )

    def click(self) -> ResolutionResult:
        """Resolves target via Jev Vision, verifies actionability, and clicks center point."""
        result, (x, y) = self.resolve()
        self.engine.adapter.click_at(x, y)
        return result

    def drag_to_offset(self, dx: float, dy: float) -> ResolutionResult:
        """Resolves target via Jev Vision and drags from its center by (dx, dy) CSS pixels."""
        result, (x, y) = self.resolve()
        self.engine.adapter.drag_to_offset(x, y, dx, dy)
        return result


class HitboxEngine:
    """Driver-agnostic core engine orchestrating Jev Vision localization, zoom, and caching."""

    def __init__(
        self,
        adapter: BrowserAdapter,
        client: JevVisionClient | None = None,
        receipt_callback: Callable[[str, bytes], None] | None = None,
    ):
        self.adapter = adapter
        self.client = client or JevVisionClient()
        self.cache = PerceptualBBoxCache()
        self.receipt_callback = receipt_callback

    def locate_by_image(
        self,
        reference_image_path: str | Path,
        *,
        description: str | None = None,
        context: dict[str, Any] | None = None,
        confidence_gate: float = 0.88,
    ) -> VisualTargetHandle:
        return VisualTargetHandle(
            self,
            reference_image_path=reference_image_path,
            description=description,
            context=context,
            confidence_gate=confidence_gate,
        )

    def locate_by_description(
        self,
        description: str,
        *,
        context: dict[str, Any] | None = None,
        confidence_gate: float = 0.88,
    ) -> VisualTargetHandle:
        return VisualTargetHandle(
            self,
            description=description,
            context=context,
            confidence_gate=confidence_gate,
        )

    def _resolve_target(
        self,
        *,
        reference_image_path: Path | None,
        description: str | None,
        context: dict[str, Any] | None,
        confidence_gate: float,
        zoom_threshold: float,
    ) -> tuple[ResolutionResult, tuple[float, float]]:
        raw_scene = self.adapter.take_screenshot()
        scene_img = Image.open(io.BytesIO(raw_scene))
        ref_img = Image.open(reference_image_path) if reference_image_path else None

        target_id = str(reference_image_path or description)
        cache_key = self.cache.compute_target_key(target_id, context)

        # 1. Primary /v1/systemone Vision pass
        result = self.client.resolve_target(
            scene_img,
            reference_img=ref_img,
            description=description,
            context=context,
        )

        # 2. 2x Micro-Zoom Fallback when confidence lands in ambiguous band [0.70, gate)
        if zoom_threshold <= result.confidence < confidence_gate:
            crop_img, crop_bounds = extract_micro_zoom_crop(scene_img, result.bbox)
            zoom_res = self.client.resolve_target(
                crop_img,
                reference_img=ref_img,
                description=description,
                context=context,
            )
            refined_bbox = reproject_zoom_bbox_to_global(
                zoom_res.bbox, crop_bounds, scene_img.size
            )
            result = zoom_res.model_copy(
                update={"bbox": refined_bbox, "used_micro_zoom": True}
            )

        # 3. Render annotated PNG receipt for test runner traces
        receipt_bytes = render_visual_receipt(scene_img, result)
        if self.receipt_callback:
            self.receipt_callback(f"hitbox-{Path(target_id).stem}.png", receipt_bytes)

        # 4. Enforce Actionability & Confidence Gates
        if not result.is_unobstructed or not result.is_visually_enabled or result.confidence < confidence_gate:
            raise HitboxActionabilityError(
                f"Hitbox Actionability Gate failed for '{target_id}': "
                f"confidence={result.confidence:.2f} (gate={confidence_gate}), "
                f"unobstructed={result.is_unobstructed} ({result.unobstructed_prob:.2f}), "
                f"enabled={result.is_visually_enabled} ({result.enabled_prob:.2f})",
                result=result,
                receipt_bytes=receipt_bytes,
            )

        self.cache.put(scene_img, cache_key, result.bbox, result.confidence)
        vp_w, vp_h = self.adapter.get_viewport_size()
        return result, result.bbox.to_viewport_xy(vp_w, vp_h)