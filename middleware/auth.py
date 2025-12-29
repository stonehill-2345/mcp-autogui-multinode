"""API Key authentication middleware for tool service and MCP service communication"""
from fastapi import Request, Response, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from core.config import settings
from core.logger import logger
from middleware.request_id import get_request_id
from contextvars import ContextVar


class APIKeyMiddleware(BaseHTTPMiddleware):
    """Middleware to validate API key for service-to-service communication"""
    
    # Paths that don't require API key authentication
    EXCLUDED_PATHS = [
        "/health",
        "/docs",
        "/openapi.json",
        "/redoc",
    ]
    
    def _create_error_response(self, status_code: int, detail: str, request_id: str = None, headers: dict = None) -> JSONResponse:
        """Create a custom error response in unified format"""
        if request_id is None:
            request_id = get_request_id()
        
        error_response = {
            "ResponseMetadata": {
                "RequestId": request_id,
                "Action": "auth",
                "Version": settings.version,
            },
            "Result": {
                "error": detail,
                "output": None
            }
        }
        
        response_headers = {"X-Request-ID": request_id}
        if headers:
            response_headers.update(headers)
        
        return JSONResponse(
            status_code=status_code,
            content=error_response,
            headers=response_headers
        )
    
    async def dispatch(self, request: Request, call_next) -> Response:
        try:
            # Check if API key authentication is enabled
            if not settings.api_key_enabled:
                # API key authentication is disabled, allow all requests
                return await call_next(request)
            
            # Skip API key validation for excluded paths
            request_path = request.url.path
            for excluded_path in self.EXCLUDED_PATHS:
                # For root path "/", use exact match; for others, use startswith
                if excluded_path == "/":
                    if request_path == "/":
                        return await call_next(request)
                elif request_path.startswith(excluded_path):
                    return await call_next(request)
            
            # Get API key from request header
            api_key = request.headers.get("X-API-Key") or request.headers.get("Authorization")
            if not api_key:
                request_id = get_request_id()
                logger.warning(
                    "API key missing in request",
                    extra={"request_id": request_id, "path": request.url.path}
                )
                return self._create_error_response(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="API key is required. Please provide X-API-Key header or Authorization header with Bearer token.",
                    request_id=request_id,
                    headers={"WWW-Authenticate": "ApiKey"}
                )
            
            # Extract key from "Bearer <key>" format if using Authorization header
            if api_key and api_key.startswith("Bearer "):
                api_key = api_key[7:]
            
            # Check if API key is configured
            if not settings.api_key:
                request_id = get_request_id()
                logger.error(
                    "API key authentication is enabled but no API key is configured",
                    extra={"request_id": request_id}
                )
                return self._create_error_response(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="API key authentication is misconfigured",
                    request_id=request_id
                )
            
            # Check if API key matches configured key
            if api_key != settings.api_key:
                request_id = get_request_id()
                logger.warning(
                    "Invalid API key provided",
                    extra={
                        "request_id": request_id,
                        "path": request.url.path,
                        "provided_key_prefix": api_key[:8] + "..." if len(api_key) > 8 else "***"
                    }
                )
                return self._create_error_response(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Invalid API key",
                    request_id=request_id,
                    headers={"WWW-Authenticate": "ApiKey"}
                )
            
            # API key is valid, proceed with request
            request_id = get_request_id()
            logger.debug(
                "API key validated successfully",
                extra={"request_id": request_id, "path": request.url.path}
            )
            response = await call_next(request)
            return response
            
        except HTTPException as e:
            # Catch any HTTPException and convert to custom format
            request_id = get_request_id()
            return self._create_error_response(
                status_code=e.status_code,
                detail=e.detail if isinstance(e.detail, str) else str(e.detail),
                request_id=request_id,
                headers=e.headers if hasattr(e, 'headers') else None
            )
        except Exception as e:
            # Catch any other unexpected exceptions
            request_id = get_request_id()
            logger.exception(
                "Unexpected error in API key middleware",
                extra={"request_id": request_id, "path": request.url.path}
            )
            return self._create_error_response(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Internal server error: {str(e)}",
                request_id=request_id
            )



api_key_ctx: ContextVar[str] = ContextVar("api_key", default="")
def get_mcp_api_key() -> str:
    """Get API key from context variable"""
    return api_key_ctx.get()
    
class MCPAPIKeyMiddleware(BaseHTTPMiddleware):
    """Middleware to validate API key for MCP server communication"""
    
    # Paths that don't require API key authentication
    EXCLUDED_PATHS = [
        "/health",
    ]
    
    def _create_mcp_error_response(self, status_code: int, error_code: int, message: str, request_id: str = None) -> JSONResponse:
        """Create a MCP protocol compliant error response (JSON-RPC format)"""
        if request_id is None:
            request_id = get_request_id()
        
        # MCP uses JSON-RPC 2.0 error format
        error_response = {
            "jsonrpc": "2.0",
            "id": None,  # Will be set from request if available
            "error": {
                "code": error_code,
                "message": message,
                "data": {
                    "request_id": request_id,
                    "status_code": status_code
                }
            }
        }
        
        return JSONResponse(
            status_code=status_code,
            content=error_response,
            headers={"X-Request-ID": request_id}
        )
    
    async def dispatch(self, request: Request, call_next) -> Response:
        try:
            # Check if API key authentication is enabled
            if not settings.api_key_enabled:
                # API key authentication is disabled, allow all requests
                return await call_next(request)
            
            # Get API key from request header
            api_key = request.headers.get("X-API-Key") or request.headers.get("Authorization")
            api_key_ctx.set(api_key)
            response = await call_next(request)
            return response

        except HTTPException as e:
            # Catch HTTPException and convert to MCP error format
            request_id = get_request_id()
            return self._create_mcp_error_response(
                status_code=e.status_code,
                error_code=-32603 if e.status_code >= 500 else -32602,  # Internal error or Invalid params
                message=e.detail if isinstance(e.detail, str) else str(e.detail),
                request_id=request_id
            )
        except Exception as e:
            # Catch any other unexpected exceptions
            request_id = get_request_id()
            logger.exception(
                "Unexpected error in MCP API key middleware",
                extra={"request_id": request_id, "path": request.url.path}
            )
            return self._create_mcp_error_response(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                error_code=-32603,  # Internal error
                message=f"Internal server error: {str(e)}",
                request_id=request_id
            )

