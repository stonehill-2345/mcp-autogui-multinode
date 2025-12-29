from abc import ABC, abstractmethod
from typing import Tuple
import re
from src.common import BaseResult, BaseError
from .schema import (
    MoveMouseRequest,
    ClickMouseRequest,
    PressMouseRequest,
    ReleaseMouseRequest,
    DragMouseRequest,
    ScrollRequest,
    PressKeyRequest,
    TypeTextRequest,
    WaitRequest,
    TakeScreenshotRequest,
    GetCursorPositionRequest,
    GetScreenSizeRequest,
    ScreenshotResponse,
)
from core.logger import logger
from mcp import types

class IComputerTool(ABC):
    @abstractmethod
    def move_mouse(self, request: MoveMouseRequest):
        pass

    @abstractmethod
    def click_mouse(self, request: ClickMouseRequest):
        pass

    @abstractmethod
    def press_mouse(self, request: PressMouseRequest):
        pass

    @abstractmethod
    def release_mouse(self, request: ReleaseMouseRequest):
        pass

    @abstractmethod
    async def drag_mouse(self, request: DragMouseRequest):
        pass

    @abstractmethod
    def scroll(self, request: ScrollRequest):
        pass

    @abstractmethod
    def press_key(self, request: PressKeyRequest):
        pass

    @abstractmethod
    def type_text(self, request: TypeTextRequest):
        pass

    @abstractmethod
    def wait(self, request: WaitRequest):
        pass

    @abstractmethod
    def take_screenshot(self, request: TakeScreenshotRequest) -> ScreenshotResponse:
        pass

    @abstractmethod
    def get_cursor_position(self, request: GetCursorPositionRequest) -> Tuple[int, int]:
        pass

    @abstractmethod
    def get_screen_size(self, request: GetScreenSizeRequest) -> Tuple[int, int]:
        pass



def wrap_pyautogui_async(fn):
    async def wrapper(*args, **kwargs):
        try:
            result = fn(*args, **kwargs)
            if isinstance(result, (BaseResult, BaseError)):
                return result
            elif result is None:
                return BaseResult(output="", error="")
            else:
                return BaseResult(output=f"{result}", error="")
        except Exception as e:
            raise BaseError(f"pyautogui error: {e}")

    return wrapper

def snake_to_camel(s: str) -> str:
    return s[0].upper() + s.title().replace('_', '')[1:] if s else ""

def camel_to_snake(name: str) -> str:
    name = re.sub(r'([A-Z]+)([A-Z][a-z])', r'\1_\2', name)
    name = re.sub(r'([a-z\d])([A-Z])', r'\1_\2', name)
    return name.lower()


# handle empty response error
def _handle_empty_response(action_name):
    logger.error(f"{action_name} returned empty response")
    return [
        types.TextContent(
            type="text",
            text="Error: empty response"
        )
    ]
# handle exception error
def _handle_exception(action_name, error):
    logger.error(f"Exception when calling {action_name}: {str(error)}")
    return [
        types.TextContent(
            type="text",
            text=f"Error: {str(error)}"
        )
    ]
def handle_error(action_name, error=None):
    """Handle API error response

    Args:
        action_name: API action name
        error: Exception object (optional)

    Returns:
        A list of TextContent objects representing the error in a unified format
    """
    # create a mapping table for handling functions
    handlers = {
        True: lambda: _handle_exception(action_name, error),
        False: lambda: _handle_empty_response(action_name),
    }

    return handlers[error is not None]()
