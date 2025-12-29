"""Core constants for computer control actions"""
from typing import Dict
from src.computer.schema import (
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
)


# Request model mapping with camelCase keys
# Maps action names (camelCase) to their corresponding Pydantic request models
REQUEST_MODELS: Dict[str, type] = {
    "move_mouse": MoveMouseRequest,
    "click_mouse": ClickMouseRequest,
    "press_mouse": PressMouseRequest,
    "release_mouse": ReleaseMouseRequest,
    "drag_mouse": DragMouseRequest,
    "scroll": ScrollRequest,
    "press_key": PressKeyRequest,
    "type_text": TypeTextRequest,
    "wait": WaitRequest,
    "take_screenshot": TakeScreenshotRequest,
    "get_cursor_position": GetCursorPositionRequest,
    "get_screen_size": GetScreenSizeRequest,
}

