"""Test MCP client functionality with stdio transport

This test suite tests the MCP server running in stdio mode.
The server is started as a subprocess and communicates via stdin/stdout.
"""
import pytest
import sys
import subprocess
import time
from pathlib import Path
from core.config import settings
from core.logger import logger
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent
MCP_LOCAL_SCRIPT = PROJECT_ROOT / "mcp_local.py"


@pytest.fixture(scope="module")
def mcp_server_params():
    """Create stdio server parameters for MCP client
    
    The stdio_client will automatically start the server process when used.
    This fixture just provides the configuration for starting the server.
    """
    logger.info("Creating MCP server parameters for stdio transport")
    logger.info("Server command: {} {}", sys.executable, MCP_LOCAL_SCRIPT)
    logger.info("MCP_LOCAL_SCRIPT path: {}", MCP_LOCAL_SCRIPT)
    logger.info("MCP_LOCAL_SCRIPT exists: {}", MCP_LOCAL_SCRIPT.exists())
    
    # Verify the script exists
    if not MCP_LOCAL_SCRIPT.exists():
        raise FileNotFoundError(f"MCP server script not found: {MCP_LOCAL_SCRIPT}")
    
    return StdioServerParameters(
        command=sys.executable,
        args=[str(MCP_LOCAL_SCRIPT), "stdio"],
    )


@pytest.fixture(scope="module")
def mcp_server_process():
    """Start MCP server in stdio mode as a subprocess for manual testing"""
    logger.info("Starting MCP server process in stdio mode")
    
    # Start the server process
    process = subprocess.Popen(
        [sys.executable, str(MCP_LOCAL_SCRIPT), "stdio"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=0  # Unbuffered
    )
    
    # Give the server a moment to start
    time.sleep(0.5)
    
    logger.info("MCP server process started with PID: {}", process.pid)
    
    yield process
    
    # Cleanup: terminate the process
    logger.info("Terminating MCP server process (PID: {})", process.pid)
    process.terminate()
    try:
        process.wait(timeout=5)
        logger.info("MCP server process terminated successfully")
    except subprocess.TimeoutExpired:
        logger.warning("MCP server process did not terminate, killing it")
        process.kill()
        process.wait()
        logger.info("MCP server process killed")


@pytest.mark.asyncio
async def test_server_connection_stdio(mcp_server_params):
    """Test basic server connection via stdio"""
    logger.info("Testing server connection with stdio client")
    
    try:
        async with stdio_client(mcp_server_params) as (read, write):
            logger.info("Successfully connected to stdio server")
            async with ClientSession(read, write) as session:
                logger.info("Initializing client session")
                await session.initialize()
                logger.info("Client session initialized successfully")
                
                # List available tools
                tools = await session.list_tools()
                logger.info("Available tools: {}", [tool.name for tool in tools.tools] if hasattr(tools, 'tools') else tools)
                
                assert tools is not None
    except Exception as e:
        logger.error("Failed to connect to stdio server: {}", e)
        logger.error("Error type: {}", type(e).__name__)
        import traceback
        logger.error("Traceback: {}", traceback.format_exc())
        raise


@pytest.mark.asyncio
async def test_move_mouse_stdio(mcp_server_params):
    """Test moving the mouse via stdio client"""
    logger.info("Testing move_mouse with stdio client")
    
    try:
        async with stdio_client(mcp_server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                response = await session.call_tool("move_mouse", {"x": 100, "y": 200})
                logger.info("MCP move_mouse stdio response: {}", response)
                assert response is not None
                assert hasattr(response, 'content') or isinstance(response, dict)
    except Exception as e:
        logger.error("Error in test_move_mouse_stdio: {}", e)
        import traceback
        logger.error("Traceback: {}", traceback.format_exc())
        raise


@pytest.mark.asyncio
@pytest.mark.parametrize("button_type,description", [
    ("left", "Left click"),
    ("right", "Right click"),
    ("middle", "Middle click"),
    ("double_left", "Double click"),
])
async def test_click_mouse_types_stdio(mcp_server_params, button_type, description):
    """Test different mouse click types via stdio client"""
    logger.info("Testing click_mouse ({}) with stdio client", description)
    
    async with stdio_client(mcp_server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            response = await session.call_tool("click_mouse", {
                "x": 100,
                "y": 200,
                "button": button_type
            })
            logger.info("MCP click_mouse ({}) stdio response: {}", description, response)
            assert response is not None
            assert hasattr(response, 'content') or isinstance(response, dict)


@pytest.mark.asyncio
async def test_get_cursor_position_stdio(mcp_server_params):
    """Test getting cursor position via stdio client"""
    logger.info("Testing get_cursor_position with stdio client")
    
    async with stdio_client(mcp_server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            response = await session.call_tool("get_cursor_position", {})
            logger.info("MCP get_cursor_position stdio response: {}", response)
            assert response is not None
            assert hasattr(response, 'content') or isinstance(response, dict)
            # Check if response has content with cursor position data
            if hasattr(response, 'content') and response.content:
                for item in response.content:
                    if hasattr(item, 'text'):
                        # Parse text content to check for position data
                        assert item.text is not None


@pytest.mark.asyncio
async def test_take_screenshot_stdio(mcp_server_params):
    """Test taking screenshot via stdio client"""
    logger.info("Testing take_screenshot with stdio client")
    
    async with stdio_client(mcp_server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            response = await session.call_tool("take_screenshot", {})
            logger.info("MCP take_screenshot stdio response: {}", response)
            assert response is not None
            assert hasattr(response, 'content') or isinstance(response, dict)
            if hasattr(response, 'content') and response.content:
                for item in response.content:
                    if hasattr(item, 'type'):
                        if item.type == "image":
                            assert hasattr(item, 'data') and item.data is not None
                        elif item.type == "text":
                            assert hasattr(item, 'text') and item.text is not None


@pytest.mark.asyncio
async def test_press_mouse_stdio(mcp_server_params):
    """Test pressing mouse button via stdio client"""
    logger.info("Testing press_mouse with stdio client")
    
    async with stdio_client(mcp_server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            response = await session.call_tool("press_mouse", {"x": 100, "y": 190, "button": "left"})
            logger.info("MCP press_mouse stdio response: {}", response)
            assert response is not None
            assert hasattr(response, 'content') or isinstance(response, dict)


@pytest.mark.asyncio
async def test_release_mouse_stdio(mcp_server_params):
    """Test releasing mouse button via stdio client"""
    logger.info("Testing release_mouse with stdio client")
    
    async with stdio_client(mcp_server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            response = await session.call_tool("release_mouse", {"x": 100, "y": 200, "button": "left"})
            logger.info("MCP release_mouse stdio response: {}", response)
            assert response is not None
            assert hasattr(response, 'content') or isinstance(response, dict)


@pytest.mark.asyncio
async def test_drag_mouse_stdio(mcp_server_params):
    """Test dragging mouse via stdio client"""
    logger.info("Testing drag_mouse with stdio client")
    
    async with stdio_client(mcp_server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            response = await session.call_tool("drag_mouse", {
                "source_x": 100,
                "source_y": 200,
                "target_x": 300,
                "target_y": 400
            })
            logger.info("MCP drag_mouse stdio response: {}", response)
            assert response is not None
            assert hasattr(response, 'content') or isinstance(response, dict)


@pytest.mark.asyncio
async def test_scroll_stdio(mcp_server_params):
    """Test scrolling via stdio client"""
    logger.info("Testing scroll with stdio client")
    
    async with stdio_client(mcp_server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            # Move to safe area first
            await session.call_tool("move_mouse", {"x": 500, "y": 500})
            await session.call_tool("wait", {"duration": 100})
            
            response = await session.call_tool("scroll", {
                "scroll_direction": "up",
                "scroll_amount": 3,
                "x": 500,
                "y": 500
            })
            logger.info("MCP scroll stdio response: {}", response)
            assert response is not None
            assert hasattr(response, 'content') or isinstance(response, dict)


@pytest.mark.asyncio
async def test_scroll_down_stdio(mcp_server_params):
    """Test scrolling down via stdio client"""
    logger.info("Testing scroll down with stdio client")
    
    async with stdio_client(mcp_server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            # Move to safe area first
            await session.call_tool("move_mouse", {"x": 500, "y": 500})
            await session.call_tool("wait", {"duration": 100})
            
            response = await session.call_tool("scroll", {
                "scroll_direction": "down",
                "scroll_amount": 1,
                "x": 500,
                "y": 500
            })
            logger.info("MCP scroll down stdio response: {}", response)
            assert response is not None
            assert hasattr(response, 'content') or isinstance(response, dict)


@pytest.mark.asyncio
async def test_press_key_stdio(mcp_server_params):
    """Test pressing key via stdio client"""
    logger.info("Testing press_key with stdio client")
    
    async with stdio_client(mcp_server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            response = await session.call_tool("press_key", {"key": "enter"})
            logger.info("MCP press_key stdio response: {}", response)
            assert response is not None
            assert hasattr(response, 'content') or isinstance(response, dict)


@pytest.mark.asyncio
async def test_press_key_combination_stdio(mcp_server_params):
    """Test pressing key combination via stdio client"""
    logger.info("Testing press_key combination with stdio client")
    
    async with stdio_client(mcp_server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            response = await session.call_tool("press_key", {"key": "ctrl space"})
            logger.info("MCP press_key combination stdio response: {}", response)
            assert response is not None
            assert hasattr(response, 'content') or isinstance(response, dict)


@pytest.mark.asyncio
async def test_type_text_stdio(mcp_server_params):
    """Test typing text via stdio client"""
    logger.info("Testing type_text with stdio client")
    
    async with stdio_client(mcp_server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            response = await session.call_tool("type_text", {"text": "Hello, World!"})
            logger.info("MCP type_text stdio response: {}", response)
            assert response is not None
            assert hasattr(response, 'content') or isinstance(response, dict)


@pytest.mark.asyncio
async def test_wait_stdio(mcp_server_params):
    """Test waiting via stdio client"""
    logger.info("Testing wait with stdio client")
    
    async with stdio_client(mcp_server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            response = await session.call_tool("wait", {"duration": 100})
            logger.info("MCP wait stdio response: {}", response)
            assert response is not None
            assert hasattr(response, 'content') or isinstance(response, dict)
