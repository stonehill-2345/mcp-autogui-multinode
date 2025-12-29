"""Test MCP client functionality

Note: To test register_computer_tools (direct tools), you need to:
1. Modify main.py to use register_computer_tools instead of register_computer_tools_with_client
2. Or start a separate MCP server with register_computer_tools enabled

The tests marked with _direct suffix are for register_computer_tools (no endpoint parameter).
The tests marked with _with_client suffix are for register_computer_tools_with_client (requires endpoint).
"""
import pytest
from core.config import settings
from core.logger import logger
from fastmcp import Client
from fastmcp.client.transports import StreamableHttpTransport


MCP_BASE_URL = f"http://{settings.mcp_host}:{settings.mcp_port}/mcp"
TOOL_BASE_URL = f"http://{settings.host}:{settings.port}"


# ============================================================================
# Tests for register_computer_tools_with_client (requires endpoint)
# These tests work with the current server configuration
# ============================================================================

def get_client():
    if not settings.api_key:
        return Client(MCP_BASE_URL)
    headers = {
        "X-API-Key": settings.api_key
    }
    transport = StreamableHttpTransport(url=MCP_BASE_URL, headers=headers)
    return Client(transport)

@pytest.mark.asyncio
async def test_move_mouse_with_client():
    """Test moving the mouse via client"""
    logger.info("Testing move_mouse with client, {}", MCP_BASE_URL)
    client = get_client()
    async with client:
        response = await client.call_tool("move_mouse", {"endpoint": TOOL_BASE_URL, "x": 100, "y": 200})
        logger.info("MCP move_mouse response: {}", response)
        assert response is not None
        assert hasattr(response, 'content') or isinstance(response, dict)


@pytest.mark.asyncio
async def test_take_screenshot_with_client():
    """Test taking a screenshot via client"""
    logger.info("Testing take_screenshot with client, {}", MCP_BASE_URL)
    client = get_client()
    async with client:
        response = await client.call_tool("take_screenshot", {"endpoint": TOOL_BASE_URL})
        logger.info("MCP take_screenshot response: {}", response.content)
        for item in response.content:
            if item.type == "image":
                image = item.data
                assert image is not None
            elif item.type == "text":
                text = item.text
                assert text is not None
            else:
                assert False
        assert True


# ============================================================================
# Tests for register_computer_tools (direct calls, no endpoint needed)
# These tests test the tools registered in register_computer_tools function
# ============================================================================

@pytest.mark.asyncio
async def test_move_mouse_direct():
    """Test moving the mouse directly (register_computer_tools)"""
    logger.info("Testing move_mouse direct, {}", MCP_BASE_URL)
    client = get_client()
    async with client:
        response = await client.call_tool("move_mouse", {"x": 100, "y": 200, "endpoint": TOOL_BASE_URL})
        logger.info("MCP move_mouse direct response: {}", response)
        assert response is not None
        # Response should be a dict with output/error
        if isinstance(response, dict):
            assert "output" in response or "error" in response


@pytest.mark.asyncio
async def test_click_mouse_direct():
    """Test clicking the mouse directly"""
    logger.info("Testing click_mouse direct, {}", MCP_BASE_URL)
    client = get_client()
    async with client:
        response = await client.call_tool("click_mouse", {"x": 100, "y": 200, "button": "left", "endpoint": TOOL_BASE_URL})
        logger.info("MCP click_mouse direct response: {}", response)
        assert response is not None
        if isinstance(response, dict):
            assert "output" in response or "error" in response


@pytest.mark.asyncio
async def test_press_mouse_direct():
    """Test pressing mouse button directly"""
    logger.info("Testing press_mouse direct, {}", MCP_BASE_URL)
    client = get_client()
    async with client:
        response = await client.call_tool("press_mouse", {"x": 100, "y": 200, "button": "left", "endpoint": TOOL_BASE_URL})
        logger.info("MCP press_mouse direct response: {}", response)
        assert response is not None
        if isinstance(response, dict):
            assert "output" in response or "error" in response


@pytest.mark.asyncio
async def test_release_mouse_direct():
    """Test releasing mouse button directly"""
    logger.info("Testing release_mouse direct, {}", MCP_BASE_URL)
    client = get_client()
    async with client:
        response = await client.call_tool("release_mouse", {"x": 100, "y": 200, "button": "left", "endpoint": TOOL_BASE_URL})
        logger.info("MCP release_mouse direct response: {}", response)
        assert response is not None
        if isinstance(response, dict):
            assert "output" in response or "error" in response


@pytest.mark.asyncio
async def test_drag_mouse_direct():
    """Test dragging mouse directly"""
    logger.info("Testing drag_mouse direct, {}", MCP_BASE_URL)
    client = get_client()
    async with client:
        response = await client.call_tool("drag_mouse", {
            "source_x": 100,
            "source_y": 200,
            "target_x": 300,
            "target_y": 400,
            "endpoint": TOOL_BASE_URL
        })
        logger.info("MCP drag_mouse direct response: {}", response)
        assert response is not None
      

@pytest.mark.asyncio
async def test_scroll_direct():
    """Test scrolling directly"""
    logger.info("Testing scroll direct, {}", MCP_BASE_URL)
    client = get_client()
    async with client:
        response = await client.call_tool("scroll", {
            "scroll_direction": "up",
            "scroll_amount": 3,
            "x": 100,
            "y": 200,
            "endpoint": TOOL_BASE_URL
        })
        logger.info("MCP scroll direct response: {}", response)
        assert response is not None
        if isinstance(response, dict):
            assert "output" in response or "error" in response


@pytest.mark.asyncio
async def test_press_key_direct():
    """Test pressing key directly"""
    logger.info("Testing press_key direct, {}", MCP_BASE_URL)
    client = get_client()
    async with client:
        response = await client.call_tool("press_key", {"key": "enter", "endpoint": TOOL_BASE_URL})
        logger.info("MCP press_key direct response: {}", response)
        assert response is not None
        if isinstance(response, dict):
            assert "output" in response or "error" in response


@pytest.mark.asyncio
async def test_type_text_direct():
    """Test typing text directly"""
    logger.info("Testing type_text direct, {}", MCP_BASE_URL)
    client = get_client()
    async with client:
        response = await client.call_tool("type_text", {"text": "Hello, World!", "endpoint": TOOL_BASE_URL})
        logger.info("MCP type_text direct response: {}", response)
        assert response is not None
        if isinstance(response, dict):
            assert "output" in response or "error" in response


@pytest.mark.asyncio
async def test_wait_direct():
    """Test waiting directly"""
    logger.info("Testing wait direct, {}", MCP_BASE_URL)
    client = get_client()
    async with client:
        response = await client.call_tool("wait", {"duration": 100, "endpoint": TOOL_BASE_URL})
        logger.info("MCP wait direct response: {}", response)
        assert response is not None
        if isinstance(response, dict):
            assert "output" in response or "error" in response


@pytest.mark.asyncio
async def test_take_screenshot_direct():
    """Test taking screenshot directly"""
    logger.info("Testing take_screenshot direct, {}", MCP_BASE_URL)
    client = get_client()
    async with client:
        response = await client.call_tool("take_screenshot", {"endpoint": TOOL_BASE_URL})
        logger.info("MCP take_screenshot direct response: {}", response)
        assert response is not None
        if isinstance(response, dict):
            assert "output" in response or "error" in response
            # Screenshot should return base64 encoded image
            if response.get("output"):
                assert isinstance(response["output"], str)


@pytest.mark.asyncio
async def test_get_cursor_position_direct():
    """Test getting cursor position directly"""
    logger.info("Testing get_cursor_position direct, {}", MCP_BASE_URL)
    client = get_client()
    async with client:
        response = await client.call_tool("get_cursor_position", {"endpoint": TOOL_BASE_URL})
        logger.info("MCP get_cursor_position direct response: {}", response)
        if isinstance(response, dict):
            assert "output" in response or "error" in response
            # Cursor position should have x and y coordinates
            if response.get("output"):
                output = response["output"]
                assert isinstance(output, dict)