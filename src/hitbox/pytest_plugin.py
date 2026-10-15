from __future__ import annotations
from pathlib import Path
import pytest
from hitbox.adapters.playwright import PlaywrightAdapter
from hitbox. adapters.selenium import SeleniumAdapter
from hitbox.engine import HitboxEngine


@pytest.fixture
def hitbox(request: pytest.FixtureRequest) -> HitboxEngine:
    """
    Auto-detects Playwright `page` or Selenium `driver` fixture in the test
    and returns a configured HitboxEngine instance.
    """
    trace_dir = Path(".hitbox-traces")
    trace_dir.mkdir(exist_ok=True)

    def _save_receipt(filename: str, png_bytes: bytes) -> None:
        safe_node = request.node.name.replace("/", "_").replace(":", "_")
        (trace_dir / f"{safe_node}_{filename}").write_bytes(png_bytes)

    if "page" in request.fixturenames:
        page = request.getfixturevalue("page")
        return HitboxEngine(adapter=PlaywrightAdapter(page), receipt_callback=_save_receipt)

    if "driver" in request.fixturenames:
        driver = request.getfixturevalue("driver")
        return HitboxEngine(adapter=SeleniumAdapter(driver), receipt_callback=_save_receipt)

    raise pytest.UsageError(
        "The `hitbox` fixture requires either a Playwright `page` fixture "
        "or a Selenium `driver` fixture in the test signature."
    )