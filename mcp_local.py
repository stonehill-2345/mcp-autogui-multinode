from fastmcp import FastMCP
from starlette.requests import Request
from starlette.responses import JSONResponse
from core.config import settings
from core.logger import logger
import uvicorn
import sys
# Register computer control tools
from src.computer.tools import register_computer_tools

def create_mcp_server() -> FastMCP:
    """Create MCP server and register tools"""
    mcp = FastMCP(settings.title)
    # Register computer control tools
    register_computer_tools(mcp)
    return mcp

# Create MCP server instance here to ensure tools are registered before starting
mcp = create_mcp_server()

def start_mcp_server_http():
    """Start MCP server with HTTP transport"""
    """Remote usage only, use this for remote usage"""
    logger.info("Starting MCP server with HTTP transport")
    app = mcp.http_app(transport="http")
    # ✅ add health check route
    async def health(request: Request):
        return JSONResponse({
            "status": "ok",
            "service": settings.title,
            "transport": "http",
        })
    app.add_route("/health", health, methods=["GET"])
    return app

def start_mcp_server_stdio():
    """Start MCP server with stdio transport"""
    """Local usage, communicates via stdin/stdout"""
    logger.info("Starting MCP server with stdio transport")
    logger.info("MCP server ready, listening on stdin/stdout")
    # FastMCP's run() method handles stdio transport automatically
    # For stdio mode, we don't pass transport parameter, it defaults to stdio
    try:
        mcp.run(transport="stdio")
    except Exception as e:
        logger.error("Error starting stdio server: {}", e)
        import traceback
        logger.error("Traceback: {}", traceback.format_exc())
        raise

if __name__ == "__main__":
    # Check transport mode from settings or command line argument
    transport_mode = settings.mcp_transport.lower()
    
    # Allow override via command line argument
    if len(sys.argv) > 1:
        arg_transport = sys.argv[1].lower()
        if arg_transport in ["stdio", "http"]:
            transport_mode = arg_transport
        else:
            logger.warning(f"Invalid transport mode '{arg_transport}', using '{transport_mode}' from settings")
    
    if transport_mode == "stdio":
        # Start stdio mode (blocking, reads from stdin/stdout)
        start_mcp_server_stdio()
    elif transport_mode == "http":
        # Start HTTP mode (runs uvicorn server)
        app = start_mcp_server_http()
        uvicorn.run(app, host=settings.mcp_host, port=settings.mcp_port)
    else:
        logger.error(f"Unsupported transport mode: {transport_mode}. Supported modes: 'stdio', 'http'")
        sys.exit(1)