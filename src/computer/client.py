from typing import Dict, Any, Literal
import httpx
from loguru import logger 
from core.config import settings

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
    BaseResponse,
)
from src.computer.schema import (
    CursorPositionResponse,
    ScreenSizeResponse,
    ScreenshotResponse,
)

class ComputerUseMCPClient:
    def __init__(self, base_url: str, api_key: str = None):
        """
        Initialize the Computer Use SDK client
        
        Args:
            base_url: Base URL of the Computer Use Tool Server
            api_key: Optional API key for authentication
        """
        self.base_url = base_url
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        # Add API key to headers if provided
        if api_key:
            self.headers["X-API-Key"] = api_key

    def _make_request(self, action: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Make a request to the Computer Use Tool Server
        
        Args:
            action: Action to perform
            params: Parameters for the action
            
        Returns:
            Response from the server
        """
        url = self.base_url + "/api/computer/" + action
        
        # Use existing client if available (from context manager), otherwise create a new one
        try:
            with httpx.Client() as client:
                response = client.post(url, json=params, headers=self.headers)
                response.raise_for_status()
                return response.json()
        except httpx.RequestError as e:
            logger.error(f"Error making request to {url}: {str(e)}")
            raise e
        except httpx.HTTPStatusError as e:
            logger.error(f"Error making request to {url}: {str(e)}")
            raise e

    def move_mouse(self, x: int, y: int) -> BaseResponse:
        """
        Move the mouse to the specified position
        
        Args:
            x: X position
            y: Y position
            
        Returns:
            Response from the server
        """
        request = MoveMouseRequest(PositionX=x, PositionY=y)
        response_data = self._make_request("MoveMouse", request.model_dump(by_alias=True))
        return BaseResponse(**response_data)

    def click_mouse(
            self,
            x: int,
            y: int,
            button: Literal["left", "right", "middle", "double_click", "double_left"] = "left",
            press: bool = False,
            release: bool = False
    ) -> BaseResponse:
        """
        Click the mouse at the specified position
        
        Args:
            x: X position
            y: Y position
            button: Mouse button to click
            press: Whether to press the mouse button
            release: Whether to release the mouse button
            
        Returns:
            Response from the server
        """
        request = ClickMouseRequest(
            PositionX=x,
            PositionY=y,
            button=button,
            press=press,
            release=release
        )
        response_data = self._make_request("ClickMouse", request.model_dump(by_alias=True))
        return BaseResponse(**response_data)

    def press_mouse(
            self,
            x: int,
            y: int,
            button: Literal["left", "right", "middle"] = "left"
    ) -> BaseResponse:
        """
        Press the mouse button at the specified position
        
        Args:
            x: X position
            y: Y position
            button: Mouse button to press
            
        Returns:
            Response from the server
        """
        request = PressMouseRequest(
            PositionX=x,
            PositionY=y,
            button=button
        )
        response_data = self._make_request("PressMouse", request.model_dump(by_alias=True))
        return BaseResponse(**response_data)

    def release_mouse(
            self,
            x: int,
            y: int,
            button: Literal["left", "right", "middle"] = "left"
    ) -> BaseResponse:
        """
        Release the mouse button at the specified position
        
        Args:
            x: X position
            y: Y position
            button: Mouse button to release
            
        Returns:
            Response from the server
        """
        request = ReleaseMouseRequest(
            PositionX=x,
            PositionY=y,
            button=button
        )
        response_data = self._make_request("ReleaseMouse", request.model_dump(by_alias=True))
        return BaseResponse(**response_data)

    def drag_mouse(
            self,
            source_x: int,
            source_y: int,
            target_x: int,
            target_y: int
    ) -> BaseResponse:
        """
        Drag the mouse from source to target position
        
        Args:
            source_x: Source X position
            source_y: Source Y position
            target_x: Target X position
            target_y: Target Y position
            
        Returns:
            Response from the server
        """
        request = DragMouseRequest(
            source_x=source_x,
            source_y=source_y,
            target_x=target_x,
            target_y=target_y
        )
        response_data = self._make_request("DragMouse", request.model_dump(by_alias=True))
        return BaseResponse(**response_data)

    def scroll(
            self,
            x: int,
            y: int,
            scroll_direction: Literal["up", "down", "left", "right"] = "up",
            scroll_amount: int = 1
    ) -> BaseResponse:
        """
        Scroll at the specified position
        
        Args:
            x: X position
            y: Y position
            scroll_direction: Direction to scroll
            scroll_amount: Amount to scroll
            
        Returns:
            Response from the server
        """
        request = ScrollRequest(
            PositionX=x,
            PositionY=y,
            scroll_direction=scroll_direction,
            scroll_amount=scroll_amount
        )
        response_data = self._make_request("Scroll", request.model_dump(by_alias=True))
        return BaseResponse(**response_data)

    def press_key(self, key: str) -> BaseResponse:
        """
        Press the specified key
        
        Args:
            key: Key to press
            
        Returns:
            Response from the server
        """
        request = PressKeyRequest(key=key)
        response_data = self._make_request("PressKey", request.model_dump(by_alias=True))
        return BaseResponse(**response_data)

    def type_text(self, text: str) -> BaseResponse:
        """
        Type the specified text
        
        Args:
            text: Text to type
            
        Returns:
            Response from the server
        """
        request = TypeTextRequest(text=text)
        response_data = self._make_request("TypeText", request.model_dump(by_alias=True))
        return BaseResponse(**response_data)

    def wait(self, duration: int) -> BaseResponse:
        """
        Wait for the specified duration in milliseconds
        
        Args:
            duration: Duration to wait in milliseconds
            
        Returns:
            Response from the server
        """
        request = WaitRequest(duration=duration)
        response_data = self._make_request("Wait", request.model_dump(by_alias=True))
        return BaseResponse(**response_data)

    def take_screenshot(self) -> ScreenshotResponse:
        """
        Take a screenshot
        
        Returns:
            Response from the server with screenshot data
        """
        request = TakeScreenshotRequest()
        response_data = self._make_request("TakeScreenshot", request.model_dump(by_alias=True))
        return ScreenshotResponse(**response_data)

    def get_cursor_position(self) -> CursorPositionResponse:
        """
        Get the current cursor position
        
        Returns:
            Response containing cursor position in Result.x and Result.y
        """
        request = GetCursorPositionRequest()
        response_data = self._make_request("GetCursorPosition", request.model_dump(by_alias=True))
        return CursorPositionResponse(**response_data)

    def get_screen_size(self) -> ScreenSizeResponse:
        """
        Get the screen size
        
        Returns:
            Response containing screen size in Result.width and Result.height
        """
        request = GetScreenSizeRequest()
        response_data = self._make_request("GetScreenSize", request.model_dump(by_alias=True))
        return ScreenSizeResponse(**response_data)

def get_computer_use_mcp_client(base_url: str = None, api_key: str = None) -> ComputerUseMCPClient:
    """
    Get the Computer Use MCP client
    
    Args:
        base_url: Base URL of the Computer Use Tool Server
        api_key: Optional API key for authentication. If not provided, uses settings.api_key
    """
    try:
        print(f"API key: {api_key}")
        return ComputerUseMCPClient(base_url, api_key=api_key)
    except  Exception as e:
        _local_client = ComputerUseMCPClient(base_url, api_key=api_key)
        raise ConnectionError(f"Cannot connect to tool server at {base_url}: {str(e)}") from e
