from __future__ import annotations
from typing import Any
from pydantic import BaseModel, Field


class NormalizedBBox(BaseModel):
    """Jev normalized coordinates in [0, 1000] scale: [ymin, xmin, ymax, xmax]."""
    ymin: float = Field(..., ge=0.0, le=1000.0)
    xmin: float = Field(..., ge=0.0, le=1000.0)
    ymax: float = Field(..., ge=0.0, le=1000.0)
    xmax: float = Field(..., ge=0.0, le=1000.0)

    @classmethod
    def from_list(cls, box_2d: list[float]) -> NormalizedBBox:
        if len(box_2d) != 4:
            raise ValueError(f"Expected 4 coordinates [ymin, xmin, ymax, xmax], got {box_2d}")
        return cls(ymin=box_2d[0], xmin=box_2d[1], ymax=box_2d[2], xmax=box_2d[3])

    def to_list(self) -> list[float]:
        return [self.ymin, self.xmin, self.ymax, self.xmax]

    @property
    def center_norm(self) -> tuple[float, float]:
        """Normalized (x, y) center in [0.0, 1.0] scale."""
        return ((self.xmin + self.xmax) / 2000.0, (self.ymin + self.ymax) / 2000.0)

    def to_viewport_xy(self, viewport_w: int, viewport_h: int) -> tuple[float, float]:
        """Projects normalized bbox center into logical CSS viewport pixels."""
        cx, cy = self.center_norm
        return (round(cx * viewport_w, 2), round(cy * viewport_h, 2))


class ResolutionResult(BaseModel):
    """Combined single-pass Jev Vision BBox + Actionability verdict."""
    bbox: NormalizedBBox
    confidence: float
    is_unobstructed: bool
    unobstructed_prob: float
    is_visually_enabled: bool
    enabled_prob: float
    rendering_health_score: float = 3.0
    used_micro_zoom: bool = False
    cache_hit: bool = False
    raw_answers: dict[str, Any] = Field(default_factory=dict)


class HitboxActionabilityError(AssertionError):
    """Raised when Jev detects an obstructed, disabled, or low-confidence visual target."""
    def __init__(self, message: str, result: ResolutionResult, receipt_bytes: bytes | None = None):
        super().__init__(message)
        self.result = result
        self.receipt_bytes = receipt_bytes