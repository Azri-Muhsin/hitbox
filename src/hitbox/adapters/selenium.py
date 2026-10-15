from __future__ import annotations
from typing import TYPE_CHECKING
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.actions.action_builder import ActionBuilder

if TYPE_CHECKING:
    from selenium.webdriver.remote.webdriver import WebDriver


class SeleniumAdapter:
    """Adapter for Selenium WebDriver using W3C Pointer Actions."""

    def __init__(self, driver: WebDriver):
        self.driver = driver

    def take_screenshot(self) -> bytes:
        return self.driver.get_screenshot_as_png()

    def get_viewport_size(self) -> tuple[int, int]:
        w, h = self.driver.execute_script("return [window.innerWidth, window.innerHeight];")
        return (int(w), int(h))

    def click_at(self, x: float, y: float) -> None:
        actions = ActionChains(self.driver)
        actions.w3c_actions = ActionBuilder(self.driver)
        actions.w3c_actions.pointer_action.move_to_location(int(x), int(y))
        actions.w3c_actions.pointer_action.click()
        actions.perform()

    def drag_to_offset(self, start_x: float, start_y: float, dx: float, dy: float) -> None:
        actions = ActionChains(self.driver)
        actions.w3c_actions = ActionBuilder(self.driver)
        pa = actions.w3c_actions.pointer_action
        pa.move_to_location(int(start_x), int(start_y))
        pa.pointer_down()
        pa.move_to_location(int(start_x + dx), int(start_y + dy))
        pa.pointer_up()
        actions.perform()