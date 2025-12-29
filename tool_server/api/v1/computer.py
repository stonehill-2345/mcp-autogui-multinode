from fastapi import APIRouter, HTTPException, Body
from typing import Dict, Any
from pydantic import ValidationError
from middleware.request_id import get_request_id
from src.computer.computer_pyautogui import PyAutoGUIComputerTool
from src.computer.base import IComputerTool
from core.constants import REQUEST_MODELS
from core.logger import logger
from src.common import BaseResponse, ResponseMetadataModel
from core.config import settings

router = APIRouter(prefix="/computer", tags=["Computer Control"])


def camel_to_snake_method(s: str) -> str:
    """Convert camelCase action to snake_case method name"""
    import re
    s = re.sub(r'([A-Z]+)([A-Z][a-z])', r'\1_\2', s)
    s = re.sub(r'([a-z\d])([A-Z])', r'\1_\2', s)
    return s.lower()

def new_computer_tool(*args, **kwargs):
    return PyAutoGUIComputerTool(*args, **kwargs)

computer_tool: IComputerTool = new_computer_tool()

@router.post("/{action}")
async def computer_action(
    action: str,
    request: Dict[str, Any] = Body(...)
):
    """
    Dynamic route for computer control actions
    
    Supported actions (camelCase):
    - moveMouse: Move mouse cursor
    - clickMouse: Click mouse button
    - pressMouse: Press mouse button
    - releaseMouse: Release mouse button
    - dragMouse: Drag mouse from source to target
    - scroll: Scroll mouse wheel
    - pressKey: Press keyboard key
    - typeText: Type text
    - wait: Wait for specified duration
    - takeScreenshot: Take a screenshot
    - getCursorPosition: Get current cursor position
    - getScreenSize: Get screen size
    """
    request_id = get_request_id()
    version = settings.version
    action = camel_to_snake_method(action)
    if action not in REQUEST_MODELS:
        raise HTTPException(
            status_code=404,
            detail=f"Action '{action}' not found. Available actions: {list(REQUEST_MODELS.keys())}"
        )
    # Validate request using the corresponding model
    request_model = REQUEST_MODELS[action]
    try:
        validated_request = request_model(**request)
        logger.info("Validated request: {}", validated_request)
    except ValidationError as e:
        return BaseResponse(
            ResponseMetadata=ResponseMetadataModel(RequestId=request_id, Action=action, Version=version),
            Result={"Error": "Invalid request"},
        ).model_dump()
    except Exception as e:
        return BaseResponse(
            ResponseMetadata=ResponseMetadataModel(RequestId=request_id, Action=action, Version=version),
            Result={"Error": f"Invalid request: {str(e)}"},
        ).model_dump()
    
    # Execute computer control action
    result = await action_route(computer_tool, action, validated_request)
    if hasattr(result, 'model_dump'):
        return BaseResponse(ResponseMetadata=ResponseMetadataModel(RequestId=request_id, Action=action, Version=version), Result=result.model_dump()).model_dump()
    return BaseResponse(ResponseMetadata=ResponseMetadataModel(RequestId=request_id, Action=action, Version=version), Result=result).model_dump()


async def action_route(obj: IComputerTool, action: str, params):
    """
    Route action to corresponding method on computer tool object.
    Converts camelCase action name to snake_case method name.
    """
    try:
        # Convert camelCase action to snake_case method name
        method_name = camel_to_snake_method(action)
        method = getattr(obj, method_name)
        result = await method(params)
        return result
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=f"Invalid request: {e.errors()}")
    except AttributeError as e:
        raise HTTPException(status_code=404, detail=f"Method not found: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid request: {str(e)}")


@router.get("/actions")
async def list_actions():
    """List all available computer control actions"""
    return {
        "actions": list(REQUEST_MODELS.keys()),
        "count": len(REQUEST_MODELS),
    }
