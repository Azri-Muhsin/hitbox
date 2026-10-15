from __future__ import annotations
from dataclasses import dataclass
import imagehash
from PIL import Image
from hitbox.schemas import NormalizedBBox


@dataclass
class _CacheEntry:
    scene_hash: imagehash.ImageHash
    bbox: NormalizedBBox
    confidence: float


class PerceptualBBoxCache:
    """L1 perceptual dHash cache with Hamming distance tolerance."""

    def __init__(self, max_hamming_distance: int = 3):
        self.max_hamming_distance = max_hamming_distance
        self._store: dict[str, _CacheEntry] = {}

    @staticmethod
    def compute_target_key(target_identifier: str, context: dict | None) -> str:
        ctx_str = str(sorted((context or {}).items()))
        return f"{target_identifier}::{ctx_str}"

    def lookup(
        self, scene_img: Image.Image, target_key: str
    ) -> tuple[NormalizedBBox, float] | None:
        entry = self._store.get(target_key)
        if not entry:
            return None

        current_hash = imagehash.dhash(scene_img)
        if (current_hash - entry.scene_hash) <= self.max_hamming_distance:
            return (entry.bbox, entry.confidence)
        return None

    def put(
        self,
        scene_img: Image.Image,
        target_key: str,
        bbox: NormalizedBBox,
        confidence: float,
    ) -> None:
        self._store[target_key] = _CacheEntry(
            scene_hash=imagehash.dhash(scene_img),
            bbox=bbox,
            confidence=confidence,
        )