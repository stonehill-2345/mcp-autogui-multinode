import base64
import time
from fastapi import HTTPException
import pyautogui
from src.common import BaseError
from .schema import *
from .base import IComputerTool, wrap_pyautogui_async, camel_to_snake
from core.logger import logger
from core.config import settings

class PyAutoGUIComputerTool(IComputerTool):
    def __init__(self):
        super().__init__()
        self.logger = logger.bind(name=__name__)

    @wrap_pyautogui_async
    def move_mouse(self, r: MoveMouseRequest):
        return pyautogui.moveTo(r.x, r.y)

    @wrap_pyautogui_async
    def click_mouse(self, r: ClickMouseRequest):
        button = r.button
        press = r.press
        release = r.release
        x, y = r.x, r.y
        if button is None or button == "":
            button = "left"
        button = camel_to_snake(button)
        if button not in ["left", "right", "middle", "double_left"]:
            raise HTTPException(status_code=400, detail=f"Invalid button")
        if press and not release:
            return self.press_mouse(PressMouseRequest(x=x, y=y, button=button))
        elif release and not press:
            return self.release_mouse(ReleaseMouseRequest(x=x, y=y, button=button))
        else:
            clicks = 1
            if button == "double_click" or button == "double_left":
                button = "left"
                clicks = 2
            return pyautogui.click(x, y, clicks=clicks, button=button.upper())

    @wrap_pyautogui_async
    def press_mouse(self, r: PressMouseRequest):
        return pyautogui.mouseDown(r.x, r.y, button=r.button.upper())

    @wrap_pyautogui_async
    def release_mouse(self, r: ReleaseMouseRequest):
        return pyautogui.mouseUp(r.x, r.y, button=r.button.upper())

    async def drag_mouse(self, r: DragMouseRequest):
        drag_path = gen_path(r.source_x, r.source_y, r.target_x, r.target_y)
        if drag_path is None or len(drag_path) < 2:
            raise BaseError(f"drag_path is required for drag")
        for loc in drag_path:
            if len(loc) != 2:
                raise BaseError(f"drag_path location must be x, y")

        await self.press_mouse(PressMouseRequest(x=drag_path[0][0], y=drag_path[0][1], button="left"))
        for loc in drag_path:
            time.sleep(settings.mouse_operate_interval)
            await self.move_mouse(MoveMouseRequest(x=loc[0], y=loc[1]))
        time.sleep(settings.mouse_operate_interval)
        return await self.release_mouse(ReleaseMouseRequest(x=drag_path[-1][0], y=drag_path[-1][1], button="left"))

    @wrap_pyautogui_async
    def scroll(self, r: ScrollRequest):
        scroll_direction = r.scroll_direction
        scroll_amount = r.scroll_amount
        x, y = r.x, r.y
        scroll_amount = int(scroll_amount) * settings.scroll_scale
        self.logger.info("scroll in windows, amount: {}, direction: {}", scroll_amount, scroll_direction)
        if scroll_direction == "up":
            scroll = pyautogui.vscroll
        elif scroll_direction == "down":
            scroll_amount = -scroll_amount
            scroll = pyautogui.vscroll
        elif scroll_direction == "left":
            scroll = pyautogui.hscroll
        elif scroll_direction == "right":
            scroll_amount = -scroll_amount
            scroll = pyautogui.hscroll
        else:
            raise ValueError(f"Invalid scroll direction: {scroll_direction}")
        return scroll(scroll_amount, x, y)

    @wrap_pyautogui_async
    def press_key(self, r: PressKeyRequest):
        keys = [x for x in r.key.split(' ') if x]
        if len(keys) == 0:
            return pyautogui.press(r.key)
        else:
            return pyautogui.hotkey(*keys)

    @wrap_pyautogui_async
    def type_text(self, r: TypeTextRequest):
        return paste(r.text)

    @wrap_pyautogui_async
    def wait(self, r: WaitRequest):
        duration = r.duration
        if isinstance(duration, str):
            duration = int(duration)
        return time.sleep(duration / 1000)

    async def take_screenshot(self, r: TakeScreenshotRequest):
        """Capture screenshot and return base64-encoded PNG"""
        try:
            # Capture screenshot directly to memory and return base64-encoded PNG
            image = pyautogui.screenshot()
            from io import BytesIO
            buffer = BytesIO()
            image.save(buffer, format="PNG")
            buffer.seek(0)
            return ScreenshotResource(screenshot=base64.b64encode(buffer.read()).decode())
        except Exception as e:
            error_msg = str(e)
            raise BaseError(f"Failed to take screenshot: {error_msg}")

    # @wrap_pyautogui
    async def get_cursor_position(self, r: GetCursorPositionRequest):
        x, y = pyautogui.position()
        return {"PositionX": x, "PositionY": y}

    async def get_screen_size(self, r: GetScreenSizeRequest):
        x, y = pyautogui.size()
        return {"Width": x, "Height": y}
