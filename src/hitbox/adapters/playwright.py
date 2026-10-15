from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from playwright.sync_api import Page


class PlaywrightAdapter:
    """Adapter for Playwright sync Page."""

    def __init__(self, page: Page):
        self.page = page

    def take_screenshot(self) -> bytes:
        return self.page.screenshot(type="jpeg", quality=85)

    def get_viewport_size(self) -> tuple[int, int]:
        vp = self.page.viewport_size
        if vp:
            return (vp["width"], vp["height"])
        dims = self.page.evaluate("() => [window.innerWidth, window.innerHeight]")
        return (int(dims[0]), int(dims[1]))

    def click_at(self, x: float, y: float) -> None:
        self.page.mouse.click(x, y)

    def drag_to_offset(self, start_x: float, start_y: float, dx: float, dy: float) -> None:
        self.page.mouse.move(start_x, start_y)
        self.page.mouse.down()
        self.page.mouse.move(start_x + dx, start_y + dy, steps=10)
        self.page.mouse.up()