from typing import Literal
from pydantic import  Field
from core.config import settings
from src.common import BaseResponse, MBaseModel
import pyperclip
import pyautogui

class MoveMouseRequest(MBaseModel):
    x: int = Field(0, description="x position", alias="PositionX")
    y: int = Field(0, description="y position", alias="PositionY")

class ClickMouseRequest(MBaseModel):
    x: int = Field(0, description="x position", alias="PositionX")
    y: int = Field(0, description="y position", alias="PositionY")
    button: Literal["left", "right", "middle", "double_click", "double_left"] = Field(
        "left", alias="Button"
    )
    press: bool = Field(False, description="press mouse", alias="Press")
    release: bool = Field(False, description="release mouse", alias="Release")

class PressMouseRequest(MBaseModel):
    x: int = Field(0, description="x position", alias="PositionX")
    y: int = Field(0, description="y position", alias="PositionY")
    button: Literal["left", "right", "middle"] = Field(
        "left", alias="Button"
    )

class ReleaseMouseRequest(MBaseModel):
    x: int = Field(0, description="x position", alias="PositionX")
    y: int = Field(0, description="y position", alias="PositionY")
    button: Literal["left", "right", "middle"] = Field(
        "left", alias="Button"
    )

class DragMouseRequest(MBaseModel):
    source_x: int = Field(0, description="source x position", alias="SourceX")
    source_y: int = Field(0, description="source y position", alias="SourceY")
    target_x: int = Field(0, description="target x position", alias="TargetX")
    target_y: int = Field(0, description="target y position", alias="TargetY")

class ScrollRequest(MBaseModel):
    scroll_direction: Literal["up", "down", "left", "right"] = Field(
        "up", alias="Direction"
    )
    scroll_amount: int = Field(0, description="scroll amount", alias="Amount")
    x: int = Field(0, description="x position", alias="PositionX")
    y: int = Field(0, description="y position", alias="PositionY")

class PressKeyRequest(MBaseModel):
    key: str = Field("", description="key", alias="Key")

class TypeTextRequest(MBaseModel):
    text: str = Field("", description="text", alias="Text")

class WaitRequest(MBaseModel):
    duration: int = Field(0, description="duration", alias="Duration")


class TakeScreenshotRequest(MBaseModel):
    pass


class GetCursorPositionRequest(MBaseModel):
    pass


class GetScreenSizeRequest(MBaseModel):
    pass

# Response models
class CursorPositionResource(MBaseModel):
    """Resource model for cursor position"""
    x: int = Field(0, description="x position", alias="PositionX")
    y: int = Field(0, description="y position", alias="PositionY")

class CursorPositionResponse(BaseResponse):
    """Response model for getting cursor position"""
    Result: CursorPositionResource = None

class ScreenSizeResource(MBaseModel):
    """Resource model for screen size"""
    width: int = Field(0, description="width", alias="Width")
    height: int = Field(0, description="height", alias="Height")

class ScreenSizeResponse(BaseResponse):
    """Response model for getting screen size"""
    Result: ScreenSizeResource = None

class ScreenshotResource(MBaseModel):
    """Resource model for screenshot"""
    screenshot: str = Field(alias="Screenshot")

class ScreenshotResponse(BaseResponse):
    """Response model for taking screenshot"""
    Result: ScreenshotResource = None


def chunks(s: str, chunk_size: int) -> list[str]:
    return [s[i: i + chunk_size] for i in range(0, len(s), chunk_size)]

def paste(foo):

    pyperclip.copy(foo)
    pyautogui.hotkey('ctrl', 'v')

def gen_path(source_x, source_y, target_x, target_y):
    drag_path = [[source_x, source_y]]
    dx = target_x - source_x
    dy = target_y - source_y
    steps = max(abs(int(dx / settings.drag_step)), abs(int(dy / settings.drag_step)))
    for i in range(steps):
        x = source_x + int(dx * i / steps)
        y = source_y + int(dy * i / steps)
        drag_path.append([x, y])
    drag_path.append([target_x, target_y])
    return drag_path
