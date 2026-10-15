from __future__ import annotations
from typing import Protocol, runtime_checkable


@runtime_checkable
class BrowserAdapter(Protocol):
    """Driver-agnostic interface connecting Hitbox to Playwright, Selenium, or Appium."""

    def take_screenshot(self) -> bytes:
        """Captures current viewport as raw image bytes."""
        ...

    def get_viewport_size(self) -> tuple[int, int]:
        """Returns logical CSS (width, height) of the active viewport."""
        ...

    def click_at(self, x: float, y: float) -> None:
        """Clicks at logical CSS coordinates (x, y)."""
        ...

    def drag_to_offset(self, start_x: float, start_y: float, dx: float, dy: float) -> None:
        """Drags from logical (start_x, start_y) by (dx, dy) offset."""
        ...