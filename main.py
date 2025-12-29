from fastmcp import FastMCP
from starlette.requests import Request
from starlette.responses import JSONResponse
from core.config import settings
from core.logger import logger
import uvicorn
# Register computer control tools
from mcp_server.register import register_computer_tools_with_client
from middleware.auth import MCPAPIKeyMiddleware

def create_mcp_server() -> FastMCP:
    """Create MCP server and register tools"""
    mcp = FastMCP(settings.title)
    # Register computer control tools
    register_computer_tools_with_client(mcp)
    return mcp

# Create MCP server instance here to ensure tools are registered before starting
mcp_server = create_mcp_server()

def start_mcp_server():
    """Start MCP server (synchronous, mcp.run() manages its own event loop) with http transport"""
    """ remote usage only, use this for remote usage"""
    logger.info("Starting MCP server with http transport")
    # Force HTTP transport for this server (mcp_server.py is for HTTP mode only)
    app = mcp_server.http_app(transport="http")
    if app is None:
        raise RuntimeError("Failed to create HTTP app. Make sure transport is set to 'http'")
    
    # Add API key authentication middleware for MCP server
    app.add_middleware(MCPAPIKeyMiddleware)
    # ✅ add health check route
    async def health(request: Request):
        return JSONResponse({
            "status": "ok",
            "service": settings.title,
            "transport": "http",
        })
    app.add_route("/health", health, methods=["GET"])
    
    return app

mcp_app = start_mcp_server()

if __name__ == "__main__":
   uvicorn.run(mcp_app, host=settings.mcp_host, port=settings.mcp_port)