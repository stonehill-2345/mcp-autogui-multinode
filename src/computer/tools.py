from typing import Dict, Any
from fastmcp import FastMCP
from mcp import types
from src.computer.computer_pyautogui import PyAutoGUIComputerTool
from src.common import BaseResult
from core.constants import REQUEST_MODELS
from core.logger import logger
from src.computer.computer_pyautogui import PyAutoGUIComputerTool
from src.computer.base import IComputerTool
from src.common import handle_error
from src.computer.schema import (
    TakeScreenshotRequest,
    GetCursorPositionRequest,
)

def new_computer_tool() -> IComputerTool:
    return PyAutoGUIComputerTool()

async def execute_computer_action(method_name: str, request_data: Dict[str, Any]) -> dict:
    """
    Execute computer control action (similar to action_route in HTTP API)
    """
    # Create computer tool instance
    computer_tool = new_computer_tool()
    try:
        # Convert camelCase action to snake_case method name
        # method_name = camel_to_snake(action)
        request_model = REQUEST_MODELS.get(method_name)
        logger.info(f"Request model: {request_model}")
        if not request_model:
            return {"Result": None, "error": f"Action '{method_name}' not found"}
        
        # Create validated request object
        validated_request = request_model(**request_data)
        method = getattr(computer_tool, method_name)
        # Execute the method
        result = await method(validated_request)
        
        # Handle different return types
        if isinstance(result, BaseResult):
            return result.model_dump()
        elif isinstance(result, dict):
            return {"output": result, "error": None}
        elif result is None:
            return {"output": None, "error": None}
        else:
            return {"output": result if result else None, "error": None}
    except Exception as e:
        raise e

def register_computer_tools(mcp: FastMCP):
    """Register all computer control tools with the MCP server"""
    
    # ============================================================================
    # Mouse Control Tools
    # ============================================================================
    
    @mcp.tool()
    async def move_mouse(x: int, y: int) -> dict:
        """
        Move the mouse cursor to the specified coordinates.
        
        Args:
            x: The x-coordinate (horizontal position) on the screen
            y: The y-coordinate (vertical position) on the screen
        
        Returns:
            dict: Result with output and error fields
                - output: Success message or None
                - error: Error message if any, None otherwise
        
        Example:
            move_mouse(x=100, y=200)  # Move mouse to position (100, 200)
        """
        request_data = {"x": x, "y": y}
        try:
            result = await execute_computer_action("move_mouse", request_data)
            if not result:
                return handle_error("move_mouse", "Failed to move mouse")
            output = result.get("output", "Operation successful")
            return types.TextContent(
                type="text",
                text=output
            )
        except Exception as e:
            return handle_error("move_mouse", e)
    
    @mcp.tool()
    async def click_mouse(
        x: int = 0,
        y: int = 0,
        button: str = "left",
        press: bool = False,
        release: bool = False
    ) -> dict:
        """
        Click the mouse button at the specified coordinates.
        
        Args:
            x: The x-coordinate where to click (default: 0, uses current position)
            y: The y-coordinate where to click (default: 0, uses current position)
            button: Mouse button to click - "left", "right", "middle", "double_click", or "double_left" (default: "left")
            press: If True, only press the button without releasing (default: False)
            release: If True, only release the button without pressing (default: False)
        
        Returns:
            dict: Result with output and error fields
        
        Example:
            click_mouse(x=100, y=200, button="left")  # Left click at (100, 200)
            click_mouse(x=100, y=200, button="right")  # Right click at (100, 200)
            click_mouse(x=100, y=200, button="double_left")  # Double click at (100, 200)
        """
        request_data = {"x": x, "y": y, "button": button, "press": press, "release": release}
        try:
            result = await execute_computer_action("click_mouse", request_data)
            if not result:
                return handle_error("click_mouse", "Failed to click mouse")
            output = result.get("output", "") if result.get("output", "") != "" else "Operation successful"
            return types.TextContent(
                type="text",
                text= output
            )
        except Exception as e:
            return handle_error("click_mouse", e)
    
    @mcp.tool()
    async def press_mouse(x: int = 0, y: int = 0, button: str = "left") -> dict:
        """
        Press down a mouse button at the specified coordinates without releasing it.
        Useful for drag operations.
        
        Args:
            x: The x-coordinate where to press (default: 0, uses current position)
            y: The y-coordinate where to press (default: 0, uses current position)
            button: Mouse button to press - "left", "right", or "middle" (default: "left")
        
        Returns:
            dict: Result with output and error fields
        
        Example:
            press_mouse(x=100, y=200, button="left")  # Press left button at (100, 200)
        """
        request_data = {"x": x, "y": y, "button": button}
        try:
            result = await execute_computer_action("press_mouse", request_data)
            if not result:
                return handle_error("press_mouse", "Failed to press mouse")
            output = result.get("output", "Operation successful")
            if output == "":
                output = "Operation successful"
            return types.TextContent(
                type="text",
                text= output
            )
        except Exception as e:
            return handle_error("press_mouse", e)
    
    @mcp.tool()
    async def release_mouse(x: int = 0, y: int = 0, button: str = "left") -> dict:
        """
        Release a mouse button at the specified coordinates.
        Usually called after press_mouse to complete a drag operation.
        
        Args:
            x: The x-coordinate where to release (default: 0, uses current position)
            y: The y-coordinate where to release (default: 0, uses current position)
            button: Mouse button to release - "left", "right", or "middle" (default: "left")
        
        Returns:
            dict: Result with output and error fields
        
        Example:
            release_mouse(x=300, y=400, button="left")  # Release left button at (300, 400)
        """
        request_data = {"x": x, "y": y, "button": button}
        try:
            result = await execute_computer_action("release_mouse", request_data)
            if not result:
                return handle_error("release_mouse", "Failed to release mouse")
            output = result.get("output", "Operation successful")
            if output == "":
                output = "Operation successful"
            return types.TextContent(
                type="text",
                text=output
            )
        except Exception as e:
            return handle_error("release_mouse", e)
        return result
    
    @mcp.tool()
    async def drag_mouse(source_x: int, source_y: int, target_x: int, target_y: int) -> dict:
        """
        Drag the mouse from source coordinates to target coordinates.
        This performs a complete drag operation: press at source, move to target, then release.
        
        Args:
            source_x: The starting x-coordinate
            source_y: The starting y-coordinate
            target_x: The ending x-coordinate
            target_y: The ending y-coordinate
        
        Returns:
            dict: Result with output and error fields
        
        Example:
            drag_mouse(source_x=100, source_y=200, target_x=300, target_y=400)
            # Drags mouse from (100, 200) to (300, 400)
        """
        request_data = {
            "source_x": source_x,
            "source_y": source_y,
            "target_x": target_x,
            "target_y": target_y
        }
        try:
            result = await execute_computer_action("drag_mouse", request_data)
            if not result:
                return handle_error("drag_mouse", "Failed to drag mouse")
            output = result.get("output", "Operation successful")
            if output == "":
                output = "Operation successful"
            return types.TextContent(
                type="text",
                text=output
            )
        except Exception as e:
            return handle_error("drag_mouse", e)
        return result
    
    @mcp.tool()
    async def scroll(
        scroll_direction: str = "up",
        scroll_amount: int = 0,
        x: int = 0,
        y: int = 0
    ) -> dict:
        """
        Scroll the mouse wheel at the specified coordinates.
        
        Args:
            scroll_direction: Direction to scroll - "up", "down", "left", or "right" (default: "up")
            scroll_amount: Amount to scroll (positive number, will be scaled automatically) (default: 0)
            x: The x-coordinate where to scroll (default: 0, uses current position)
            y: The y-coordinate where to scroll (default: 0, uses current position)
        
        Returns:
            dict: Result with output and error fields
        
        Example:
            scroll(scroll_direction="up", scroll_amount=3, x=100, y=200)  # Scroll up 3 units at (100, 200)
            scroll(scroll_direction="down", scroll_amount=5)  # Scroll down 5 units at current position
        """
        request_data = {
            "scroll_direction": scroll_direction,
            "scroll_amount": scroll_amount,
            "x": x,
            "y": y
        }
        try:
            result = await execute_computer_action("scroll", request_data)
            if not result:
                return handle_error("scroll", "Failed to scroll")
            output = result.get("output", "Operation successful")
            if output == "":
                output = "Operation successful"
            return types.TextContent(
                type="text",
                text=output
            )
        except Exception as e:
            return handle_error("scroll", e)
    
    # ============================================================================
    # Keyboard Control Tools
    # ============================================================================
    
    @mcp.tool()
    async def press_key(key: str) -> dict:
        """
        Press a keyboard key or key combination.
        
        Args:
            key: Single key name (e.g., "enter", "space", "tab") or key combination 
                 separated by spaces (e.g., "ctrl c", "alt tab", "shift f10")
        
        Returns:
            dict: Result with output and error fields
        
        Example:
            press_key("enter")  # Press Enter key
            press_key("ctrl c")  # Press Ctrl+C (copy)
            press_key("alt tab")  # Press Alt+Tab (switch windows)
        """
        request_data = {"key": key}
        try:
            result = await execute_computer_action("press_key", request_data)
            if not result:
                return handle_error("press_key", "Failed to press key")
            output = result.get("output", "Operation successful")
            if output == "":
                output = "Operation successful"
            return types.TextContent(
                type="text",
                text=output
            )
        except Exception as e:
            return handle_error("press_key", e)
    
    @mcp.tool()
    async def type_text(text: str) -> dict:
        """
        Type the specified text. The text will be pasted using clipboard (Ctrl+V).
        This is more reliable than typing character by character for special characters.
        
        Args:
            text: The text string to type
        
        Returns:
            dict: Result with output and error fields
        
        Example:
            type_text("Hello, World!")  # Types "Hello, World!"
            type_text("username@example.com")  # Types email address
        """
        request_data = {"text": text}
        try:
            result = await execute_computer_action("type_text", request_data)
            if not result:
                return handle_error("type_text", "Failed to type text")
            output = result.get("output", "Operation successful")
            if output == "":
                output = "Operation successful"
            return types.TextContent(
                type="text",
                text=output
            )
        except Exception as e:
            return handle_error("type_text", e)
        return result
    
    # ============================================================================
    # Utility Tools
    # ============================================================================
    
    @mcp.tool()
    async def wait(duration: int) -> dict:
        """
        Wait for a specified duration in milliseconds.
        
        Args:
            duration: Duration to wait in milliseconds (e.g., 1000 = 1 second)
        
        Returns:
            dict: Result with output and error fields
        
        Example:
            wait(1000)  # Wait for 1 second
            wait(500)  # Wait for 0.5 seconds
        """
        request_data = {"duration": duration}
        try:
            result = await execute_computer_action("wait", request_data)
            if not result:
                return handle_error("wait", "Failed to wait")
            return types.TextContent(
                type="text",
                text="Operation successful"
            )
        except Exception as e:
            return handle_error("wait", e)
    
    @mcp.tool()
    async def take_screenshot() -> list[types.Content]:
        """
        Take a screenshot of the entire screen and return it as a base64-encoded PNG image.
        
        Returns:
            dict: Result with output and error fields
                - output: Base64-encoded PNG image string if successful, None otherwise
                - error: Error message if any, None otherwise
        
        Example:
            result = take_screenshot()
            # result["output"] contains the base64-encoded PNG image
            # You can decode it to display or save the screenshot
        """

        # get screen size
        screen_size = await execute_computer_action("get_screen_size", {})
        if not screen_size:
            return handle_error("take_screenshot", "Failed to get screen size")
        output = screen_size.get("output", {})
        width = output.get("Width", 0)
        height = output.get("Height", 0)
        if width <= 0 or height <= 0:
            return handle_error("take_screenshot", "Invalid screen size")
        # take screenshot
        request = TakeScreenshotRequest()
        screenshot = await execute_computer_action("take_screenshot", request.model_dump())
        if not screenshot:
            return handle_error("take_screenshot", "Failed to take screenshot")
        screenshot_output = screenshot.get("output", None)
        if not screenshot_output:
            return handle_error("take_screenshot", "Failed to take screenshot")
        return [
            types.TextContent(type="text", text=str({"width": width, "height": height})),
            types.ImageContent(type="image", data=screenshot_output.screenshot, mimeType="image/png")
        ]
        
    
    @mcp.tool()
    async def get_cursor_position() -> dict:
        """
        Get the current mouse cursor position on the screen.
        
        Returns:
            dict: Result with output and error fields
                - output: Dictionary with "PositionX" and "PositionY" keys containing coordinates
                - error: Error message if any, None otherwise
        
        Example:
            result = get_cursor_position()
            # result["output"] = {"PositionX": 100, "PositionY": 200}
        """
        request = GetCursorPositionRequest()
        try:
            result = await execute_computer_action("get_cursor_position", request.model_dump())
            if not result:
                return handle_error("get_cursor_position", "Failed to get cursor position")
            output = result.get("output", {})
            return types.TextContent(
                type="text",
                text=str({
                    "x": output.get("PositionX", output.get("x", 0)),
                    "y": output.get("PositionY", output.get("y", 0))
                })
            )
        except Exception as e:
            logger.error("Error in get_cursor_position: {}", e)
            return handle_error("get_cursor_position", e)