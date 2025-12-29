from pydantic import BaseModel, Field
from typing import Dict, Any
from core.logger import logger
from mcp import types

class ResponseMetadataModel(BaseModel):
    """Response metadata model"""
    RequestId: str = ""
    Action: str
    Version: str

class BaseResponse(BaseModel):
    """Base response model for all API calls"""
    ResponseMetadata: ResponseMetadataModel = None
    Result: Dict[str, Any] = None

class BaseError(Exception):
    """Represents the result of a tool execution."""

    def __init__(self, message):
        self.message = message

class BaseResult(BaseModel):
    """Represents the result of a tool execution."""
    output: str | None = Field(default=None, description="Output result")
    error: str | None = Field(default=None, description="Error message if any")

    model_config = {
        "frozen": True,  # Make the model immutable
        "populate_by_name": True,
    }

    def replace(self, **kwargs):
        """Returns a new BaseResult with the given fields replaced."""
        return self.model_copy(update=kwargs)

class MBaseModel(BaseModel):
    """
    Base model with populate_by_name enabled.
    
    populate_by_name = True means:
    - Fields can be populated using either their field name (e.g., 'x') 
      OR their alias (e.g., 'PositionX')
    - This allows flexible input: both {"x": 100} and {"PositionX": 100} work
    - Useful when integrating with APIs that use different naming conventions
    """
    model_config = {
        "populate_by_name": True,  # Allow both field name and alias
    }

#--------------------------------------------------------
# handle empty response error
def _handle_empty_response(action_name):
    logger.error(f"{action_name} returned empty response")
    return [
        types.TextContent(
            type="text",
            text="Error: empty response"
        )
    ]
# handle exception error
def _handle_exception(action_name, error):
    logger.error(f"Exception when calling {action_name}: {str(error)}")
    return [
        types.TextContent(
            type="text",
            text=f"Error: {str(error)}"
        )
    ]
# handle error response
def handle_error(action_name, error=None):
    """Handle API error response

    Args:
        action_name: API action name
        error: Exception object (optional)

    Returns:
        A list of TextContent objects representing the error in a unified format
    """
    # create a mapping table for handling functions
    handlers = {
        True: lambda: _handle_exception(action_name, error),
        False: lambda: _handle_empty_response(action_name),
    }

    return handlers[error is not None]()
#--------------------------------------------------------