"""Register computer control tools with FastMCP server"""
from pydantic import Field
from typing import Any
from src.computer.client import get_computer_use_mcp_client
from src.computer.base import handle_error
from mcp import types
from fastmcp import FastMCP
from loguru import logger
from middleware.auth import get_mcp_api_key
from src.computer.client import ComputerUseMCPClient

def get_computer_use_mcp_client_with_api_key(endpoint: str) -> ComputerUseMCPClient:
    api_key = get_mcp_api_key()
    print(f"API key: {api_key}")
    return get_computer_use_mcp_client(endpoint, api_key=get_mcp_api_key())

def register_computer_tools_with_client(mcp: FastMCP):
    """Register all computer control tools with the MCP server.
    For remote usage with client
    """
    # ============================================================================
    # Mouse Control Tools
    # ============================================================================
    
    @mcp.tool(
        name="move_mouse",
        description="Move the mouse cursor to the specified coordinates"
    )
    async def move_mouse(
        x: int = Field(description="X coordinate (horizontal position)"),
        y: int = Field(description="Y coordinate (vertical position)"),
        endpoint: str = Field(default=None, description="Endpoint of the Computer Use Tool Server"),
    ) -> dict:
        try:
            client = get_computer_use_mcp_client_with_api_key(endpoint)
            response = client.move_mouse(x, y)
            if not response:
                return handle_error("move_mouse", "Failed to move mouse")
            return types.TextContent(
                type="text",
                text="Operation successful"
            )
        except Exception as e:
            logger.error("Error in move_mouse: {}", e)
            return handle_error("move_mouse", e)
    
    @mcp.tool(
        name="click_mouse",
        description="Click the mouse button at the specified coordinates"
    )
    async def click_mouse(
        x: int = Field(default=0, description="X coordinate"),
        y: int = Field(default=0, description="Y coordinate"),
        button: str = Field(default="left", description="Mouse button: left, right, middle, double_click, double_left"),
        press: bool = Field(default=False, description="Only press without releasing"),
        release: bool = Field(default=False, description="Only release without pressing"),
        endpoint: str = Field(default=None, description="Endpoint of the Computer Use Tool Server")
    ) -> dict:
        try:
            client = get_computer_use_mcp_client_with_api_key(endpoint)
            response = client.click_mouse(x, y, button, press, release)
            if not response:
                return handle_error("click_mouse", "Failed to click mouse")
            return types.TextContent(
                type="text",
                text="Operation successful"
            )
        except Exception as e:
            logger.error("Error in click_mouse: {}", e)
            return handle_error("click_mouse", e)
    
    @mcp.tool(
        name="press_mouse",
        description="Press down a mouse button at the specified coordinates"
    )
    async def press_mouse(
        x: int = Field(default=0, description="X coordinate"),
        y: int = Field(default=0, description="Y coordinate"),
        button: str = Field(default="left", description="Mouse button: left, right, middle"),
        endpoint: str = Field(default=None, description="Endpoint of the Computer Use Tool Server")
    ) -> dict:
        try:
            client = get_computer_use_mcp_client_with_api_key(endpoint)
            response = client.press_mouse(x, y, button)
            if not response:
                return handle_error("press_mouse", "Failed to press mouse")
            return types.TextContent(
                type="text",
                text="Operation successful"
            )
        except Exception as e:
            logger.error("Error in press_mouse: {}", e)
            return handle_error("press_mouse", e)
    
    @mcp.tool(
        name="release_mouse",
        description="Release a mouse button at the specified coordinates"
    )
    async def release_mouse(
        endpoint: str = Field(default=None, description="Endpoint of the Computer Use Tool Server"),
        x: int = Field(default=0, description="X coordinate"),
        y: int = Field(default=0, description="Y coordinate"),
        button: str = Field(default="left", description="Mouse button: left, right, middle")
    ) -> dict:
        try:
            client = get_computer_use_mcp_client_with_api_key(endpoint)
            response = client.release_mouse(x, y, button)
            if not response:
                return handle_error("release_mouse", "Failed to release mouse")
            return types.TextContent(
                type="text",
                text="Operation successful"
            )
        except Exception as e:
            logger.error("Error in release_mouse: {}", e)
            return handle_error("release_mouse", e)
    
    @mcp.tool(
        name="drag_mouse",
        description="Drag the mouse from source coordinates to target coordinates"
    )
    async def drag_mouse(
        source_x: int = Field(description="Source X coordinate"),
        source_y: int = Field(description="Source Y coordinate"),
        target_x: int = Field(description="Target X coordinate"),
        target_y: int = Field(description="Target Y coordinate"),
        endpoint: str = Field(default=None, description="Endpoint of the Computer Use Tool Server")
    ) -> dict:
        try:
            client = get_computer_use_mcp_client_with_api_key(endpoint)
            response = client.drag_mouse(source_x, source_y, target_x, target_y)
            if not response:
                return handle_error("drag_mouse", "Failed to drag mouse")
            return types.TextContent(
                type="text",
                text="Operation successful"
            )
        except Exception as e:
            logger.error("Error in drag_mouse: {}", e)
            return handle_error("drag_mouse", e)
    
    @mcp.tool(
        name="scroll",
        description="Scroll the mouse wheel at the specified coordinates"
    )
    async def scroll(
        x: int = Field(default=0, description="X coordinate"),
        y: int = Field(default=0, description="Y coordinate"),
        scroll_direction: str = Field(default="up", description="Scroll direction: up, down, left, right"),
        scroll_amount: int = Field(default=1, description="Amount to scroll"),
        endpoint: str = Field(default=None, description="Endpoint of the Computer Use Tool Server")
    ) -> dict:
        try:
            client = get_computer_use_mcp_client_with_api_key(endpoint)
            response = client.scroll(x, y, scroll_direction, scroll_amount)
            if not response:
                return handle_error("scroll", "Failed to scroll")
            return types.TextContent(
                type="text",
                text="Operation successful"
            )
        except Exception as e:
            logger.error("Error in scroll: {}", e)
            return handle_error("scroll", e)
    
    # ============================================================================
    # Keyboard Control Tools
    # ============================================================================
    
    @mcp.tool(
        name="press_key",
        description="Press a keyboard key or key combination"
    )
    async def press_key(
        key: str = Field(description="Key name or key combination (e.g., 'enter', 'ctrl c', 'alt tab')"),
        endpoint: str = Field(default=None, description="Endpoint of the Computer Use Tool Server"),
    ) -> dict:
        try:
            client = get_computer_use_mcp_client_with_api_key(endpoint)
            response = client.press_key(key)
            if not response:
                return handle_error("press_key", "Failed to press key")
            return types.TextContent(
                type="text",
                text="Operation successful"
            )
        except Exception as e:
            logger.error("Error in press_key: {}", e)
            return handle_error("press_key", e)
    
    @mcp.tool(
        name="type_text",
        description="Type the specified text using clipboard paste"
    )
    async def type_text(
        text: str = Field(description="Text to type"),
        endpoint: str = Field(default=None, description="Endpoint of the Computer Use Tool Server"),
    ) -> dict:
        try:
            client = get_computer_use_mcp_client_with_api_key(endpoint)
            response = client.type_text(text)
            if not response:
                return handle_error("type_text", "Failed to type text")
            return types.TextContent(
                type="text",
                text="Operation successful"
            )
        except Exception as e:
            logger.error("Error in type_text: {}", e)
            return handle_error("type_text", e)
    
    # ============================================================================
    # Utility Tools
    # ============================================================================
    
    @mcp.tool(
        name="wait",
        description="Wait for a specified duration in milliseconds"
    )
    async def wait(
        duration: int = Field(description="Duration to wait in milliseconds"),
        endpoint: str = Field(default=None, description="Endpoint of the Computer Use Tool Server")
    ) -> dict:
        try:
            client = get_computer_use_mcp_client_with_api_key(endpoint)
            response = client.wait(duration)
            if not response:
                return handle_error("wait", "Failed to wait")
            return types.TextContent(
                type="text",
                text="Operation successful"
            )
        except Exception as e:
            logger.error("Error in wait: {}", e)
            return handle_error("wait", e)
    
    @mcp.tool(
        name="take_screenshot",
        description="Take a screenshot of the current screen"
    )
    async def take_screenshot(
       endpoint: str = Field(default=None, description="Endpoint of the Computer Use Tool Server")
    ) -> list[dict[str, Any]]:
        try:
            client = get_computer_use_mcp_client_with_api_key(endpoint)
            # Call synchronous method
            screenshot_response = client.take_screenshot()
            if not screenshot_response or not hasattr(screenshot_response, 'Result'):
                return handle_error("take_screenshot", "Failed to take screenshot")
            
            # Extract data
            result = screenshot_response.model_dump().get('Result')
            if not result or 'screenshot' not in result:
                return handle_error("take_screenshot", "Invalid screenshot response")
            
            image = result['screenshot']
            # get screen size
            screen_size_response = client.get_screen_size()
            if not screen_size_response or not hasattr(screen_size_response, 'Result'):
                return handle_error("get_screen_size", "Failed to get screen size")

            screen_result = screen_size_response.model_dump().get('Result')
            if not screen_result:
                return handle_error("get_screen_size", "Invalid screen size response")

            width = screen_result.get('width') or screen_result.get('Width')
            height = screen_result.get('height') or screen_result.get('Height')
            logger.info(f"Get screen size, width: {width}, height: {height}")
            return [
                types.TextContent(
                    type="text",
                    text=str(
                        {
                            "width": width,
                            "height": height,
                        }
                    )
                ),
                types.ImageContent(
                    type="image",
                    data=image,
                    mimeType="image/png",
                )
            ]
        except Exception as e:
            logger.error("Error in take_screenshot: {}", e)
            return handle_error("take_screenshot", e)
    
    @mcp.tool(
        name="get_cursor_position",
        description="Get the current mouse cursor position"
    )
    async def get_cursor_position(
        endpoint: str = Field(default=None, description="Endpoint of the Computer Use Tool Server")
    ) -> dict:
        try:
            client = get_computer_use_mcp_client_with_api_key(endpoint)
            response = client.get_cursor_position()
            if not response:
                return handle_error("get_cursor_position", "Failed to get cursor position")
            return types.TextContent(
                type="text",
                text=str(
                    {
                        "x": response.Result.x,
                        "y": response.Result.y
                    }
                )
            )
        except Exception as e:
            logger.error("Error in get_cursor_position: {}", e)
            return handle_error("get_cursor_position", e)
    