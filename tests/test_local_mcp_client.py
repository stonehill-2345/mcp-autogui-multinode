import pytest
from core.config import settings
from core.logger import logger
from fastmcp import Client
from mcp import types
from mcp import StdioServerParameters
from pathlib import Path
import sys
PROJECT_ROOT = Path(__file__).parent.parent
MCP_LOCAL_SCRIPT = PROJECT_ROOT / "mcp_local.py"

MCP_BASE_URL = f"http://localhost:{settings.mcp_port}/mcp"

# must start the mcp server before running the tests
# example:
# First start the mcp server:
# uv run python mcp_local.py http
# Then run the tests:
# uv run pytest tests/test_local_mcp_client.py

@pytest.mark.asyncio
async def test_move_mouse_with_client():
    """Test moving the mouse via client"""
    logger.info("Testing move_mouse with client, {}", MCP_BASE_URL)
    client = Client(MCP_BASE_URL)
    async with client:
        response = await client.call_tool("move_mouse", {"x": 100, "y": 200})
        logger.info("MCP move_mouse response: {}", response)
        assert response is not None
        # Response should be a dict with output/error
        if isinstance(response, dict):
            assert "output" in response or "error" in response
        elif hasattr(response, 'content'):
            # Handle FastMCP response format
            assert response.content is not None

@pytest.mark.asyncio
@pytest.mark.parametrize("button_type,description", [
    ("left", "Left click"),
    ("right", "Right click"),
    ("middle", "Middle click"),
    ("double_left", "Double click"),
])
async def test_click_mouse_types_with_client(button_type, description):
    """Test different mouse click types: left, right, and double click"""
    logger.info("Testing click_mouse ({}) with client, {}", description, MCP_BASE_URL)
    client = Client(MCP_BASE_URL)
    async with client:
        response = await client.call_tool("click_mouse", {
            "x": 100,
            "y": 200,
            "button": button_type
        })
        logger.info("MCP click_mouse ({}) response: {}", description, response)
        assert response is not None
        if isinstance(response, dict):
            assert "output" in response or "error" in response
        elif hasattr(response, 'content'):
            assert response.content is not None


@pytest.mark.asyncio
async def test_get_cursor_position_with_client():
    """Test getting cursor position via client"""
    logger.info("Testing get_cursor_position with client, {}", MCP_BASE_URL)
    client = Client(MCP_BASE_URL)
    async with client:
        response = await client.call_tool("get_cursor_position", {})
        logger.info("MCP get_cursor_position response: {}", response)
        assert response is not None
        if isinstance(response, dict):
            assert "output" in response or "error" in response
            # Cursor position should have PositionX and PositionY
            if response.get("output"):
                output = response["output"]
                assert isinstance(output, dict)
                assert "PositionX" in output or "PositionY" in output


@pytest.mark.asyncio
async def test_take_screenshot_with_client():
    """Test taking screenshot via client"""
    logger.info("Testing take_screenshot with client, {}", MCP_BASE_URL)
    client = Client(MCP_BASE_URL)
    async with client:
        response = await client.call_tool("take_screenshot", {})
        logger.info("MCP take_screenshot response: {}", response)
        assert response is not None
        if isinstance(response, list):
            # Screenshot should return base64 encoded image
            if len(response) > 0:
                for item in response:
                    if item.type == "image":
                        image = item.data
                        assert image is not None
                    elif item.type == "text":
                        text = item.text
                        assert text is not None
                    else:
                        assert False


@pytest.mark.asyncio
async def test_press_mouse_with_client():
    """Test pressing mouse button via client"""
    logger.info("Testing press_mouse with client, {}", MCP_BASE_URL)
    client = Client(MCP_BASE_URL)
    async with client:
        response = await client.call_tool("press_mouse", {"x": 100, "y": 190, "button": "left"})
        logger.info("MCP press_mouse response: {}", response)
        assert response is not None
        if isinstance(response, dict):
            assert "output" in response or "error" in response


@pytest.mark.asyncio
async def test_release_mouse_with_client():
    """Test releasing mouse button via client"""
    logger.info("Testing release_mouse with client, {}", MCP_BASE_URL)
    client = Client(MCP_BASE_URL)
    async with client:
        response = await client.call_tool("release_mouse", {"x": 100, "y": 200, "button": "left"})
        logger.info("MCP release_mouse response: {}", response)
        assert response is not None
        if isinstance(response, dict):
            assert "output" in response or "error" in response


@pytest.mark.asyncio
async def test_drag_mouse_with_client():
    """Test dragging mouse via client"""
    logger.info("Testing drag_mouse with client, {}", MCP_BASE_URL)
    client = Client(MCP_BASE_URL)
    async with client:
        response = await client.call_tool("drag_mouse", {
            "source_x": 100,
            "source_y": 200,
            "target_x": 300,
            "target_y": 400
        })
        logger.info("MCP drag_mouse response: {}", response)
        assert response is not None
        if isinstance(response, dict):
            assert "output" in response or "error" in response


@pytest.mark.asyncio
async def test_scroll_with_client():
    """Test scrolling via client"""
    logger.info("Testing scroll with client, {}", MCP_BASE_URL)
    client = Client(MCP_BASE_URL)
    async with client:
        # 移动到屏幕中央的安全区域，避免在系统UI区域滚动
        await client.call_tool("move_mouse", {"x": 500, "y": 500})
        await client.call_tool("wait", {"duration": 100})
        # 在安全位置进行滚动，使用屏幕中央坐标
        response = await client.call_tool("scroll", {
            "scroll_direction": "up",
            "scroll_amount": 3,
            "x": 500,  # 使用屏幕中央位置，远离系统UI区域
            "y": 500   # 避免在顶部菜单栏或底部Dock区域
        })
        logger.info("MCP scroll response: {}", response)
        assert response is not None
        if isinstance(response, dict):
            assert "output" in response or "error" in response
        elif hasattr(response, 'content'):
            assert response.content is not None

@pytest.mark.asyncio
async def test_scroll_down_with_client():
    """Test scrolling down via client"""
    logger.info("Testing scroll down with client, {}", MCP_BASE_URL)
    client = Client(MCP_BASE_URL)
    async with client:
        # 先移动到屏幕中央的安全区域（避免在系统UI区域滚动）
        # 使用较大的 y 坐标，避免在顶部菜单栏区域
        await client.call_tool("move_mouse", {"x": 500, "y": 500})
        # 添加短暂延迟，确保鼠标位置稳定
        await client.call_tool("wait", {"duration": 100})
        # 在安全位置进行滚动，明确指定坐标，使用较小的滚动量
        response = await client.call_tool("scroll", {
            "scroll_direction": "down",
            "scroll_amount": 1,
            "x": 500,  # 明确指定坐标，避免使用当前鼠标位置
            "y": 500   # 使用屏幕中央位置，远离系统UI区域
        })
        logger.info("MCP scroll down response: {}", response)
        assert response is not None
        if isinstance(response, types.Content):
            assert response.text is not None


@pytest.mark.asyncio
async def test_press_key_with_client():
    """Test pressing key via client"""
    logger.info("Testing press_key with client, {}", MCP_BASE_URL)
    client = Client(MCP_BASE_URL)
    async with client:
        response = await client.call_tool("press_key", {"key": "enter"})
        logger.info("MCP press_key response: {}", response)
        assert response is not None
        if isinstance(response, types.Content):
            assert response.text is not None


@pytest.mark.asyncio
async def test_press_key_combination_with_client():
    """Test pressing key combination via client"""
    logger.info("Testing press_key combination with client, {}", MCP_BASE_URL)
    client = Client(MCP_BASE_URL)
    async with client:
        response = await client.call_tool("press_key", {"key": "ctrl space"})
        logger.info("MCP press_key combination response: {}", response)
        assert response is not None
        if isinstance(response, types.Content):
            assert response.text is not None


@pytest.mark.asyncio
async def test_type_text_with_client():
    """Test typing text via client"""
    logger.info("Testing type_text with client, {}", MCP_BASE_URL)
    client = Client(MCP_BASE_URL)
    async with client:
        response = await client.call_tool("type_text", {"text": "Hello, World!"})
        logger.info("MCP type_text response: {}", response)
        assert response is not None
        if isinstance(response, types.Content):
            assert response.text is not None


@pytest.mark.asyncio
async def test_wait_with_client():
    """Test waiting via client"""
    logger.info("Testing wait with client, {}", MCP_BASE_URL)
    client = Client(MCP_BASE_URL)
    async with client:
        response = await client.call_tool("wait", {"duration": 100})
        logger.info("MCP wait response: {}", response)
        assert response is not None
        if isinstance(response, types.Content):
            assert response.text is not None


@pytest.mark.asyncio
async def test_click_mouse_right_button_with_client():
    """Test right clicking mouse via client"""
    logger.info("Testing click_mouse right button with client, {}", MCP_BASE_URL)
    client = Client(MCP_BASE_URL)
    async with client:
        response = await client.call_tool("click_mouse", {"x": 100, "y": 200, "button": "right"})
        logger.info("MCP click_mouse right button response: {}", response)
        assert response is not None
        if isinstance(response, dict):
            assert "output" in response or "error" in response
        elif hasattr(response, 'content'):
            assert response.content is not None


@pytest.mark.asyncio
async def test_click_mouse_double_click_with_client():
    """Test double clicking mouse via client"""
    logger.info("Testing click_mouse double click with client, {}", MCP_BASE_URL)
    client = Client(MCP_BASE_URL)
    async with client:
        response = await client.call_tool("click_mouse", {"x": 100, "y": 200, "button": "double_left"})
        logger.info("MCP click_mouse double click response: {}", response)
        assert response is not None
        if isinstance(response, dict):
            assert "output" in response or "error" in response
        elif hasattr(response, 'content'):
            assert response.content is not None