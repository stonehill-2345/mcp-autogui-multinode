<p align="center"><a href="" target="_blank"><img src="./mcp-autogui-multinode.png?raw=true"></a></p>

<p align="center">
<a href="./"><img src="https://img.shields.io/badge/License-MIT-blue.svg" alt="License MIT"></a>
</p>

### About

An MCP and HTTP server wrapper for PyAutoGUI, enabling LLMs to control your mouse and keyboard.

### Architecture

The service supports two deployment architectures:

#### LLM -> MCP -> TOOL (Remote Tool Service)

This architecture separates the MCP server from the tool service, allowing the MCP server to connect to a remote tool service via HTTP.

```mermaid
graph LR
    LLM[LLM Client] -->|MCP Protocol| MCP[MCP Server<br/>main.py<br/>Client-based Tools]
    MCP -->|HTTP API<br/>with API Key| TOOLA[Tool Service<br/>tool.py<br/>HTTP API Server]
    MCP -->|HTTP API<br/>with API Key| TOOLB[Tool Service<br/>tool.py<br/>HTTP API Server]

    TOOLA -->|PyAutoGUI| COMPUTERA[Computer Control]
    TOOLB -->|PyAutoGUI| COMPUTERB[Computer Control]
    style LLM fill:#e1f5ff
    style MCP fill:#fff4e1
    style TOOLA fill:#ffe1f5
    style COMPUTERA fill:#e1ffe1
    style COMPUTERB fill:#e1ffe1
```

**Characteristics:**
- MCP server uses **client-based tools** (`register_computer_tools_with_client`)
- MCP server forwards requests to remote tool service via HTTP
- Tool service performs actual computer control operations
- Suitable for distributed deployments where MCP server and tool service run on different machines
- Requires `endpoint` parameter in MCP tool calls

#### Architecture 2: LLM -> MCP (Direct Tools)

This architecture uses direct tools where the MCP server directly performs computer control operations.

```mermaid
graph LR
    LLM[LLM Client] -->|MCP Protocol<br/>stdio/http| MCP[MCP Server<br/>mcp_local.py<br/>Direct Tools]
    MCP -->|PyAutoGUI| COMPUTER[Computer Control]
    
    style LLM fill:#e1f5ff
    style MCP fill:#fff4e1
    style COMPUTER fill:#e1ffe1
```

**Characteristics:**
- MCP server uses **direct tools** (`register_computer_tools`)
- MCP server directly executes computer control operations
- No separate tool service required
- Suitable for local deployments where everything runs on the same machine
- No `endpoint` parameter needed in MCP tool calls

## Features

- 🚀 **Dual Protocol Support**: HTTP REST API and MCP (Model Context Protocol)
- 🔐 **API Key Authentication**: Optional API key authentication for service-to-service communication
- 🌐 **Multiple MCP Transports**: Support for both HTTP and stdio (Standard Input/Output) transport modes
- 🖱️ **Mouse Control**: Move, click, drag, scroll operations
- ⌨️ **Keyboard Control**: Press keys, type text, key combinations
- 📸 **Screenshot**: Capture screen and get base64-encoded images
- 📊 **Screen Info**: Get cursor position and screen resolution
- ⚙️ **Configuration Management**: Pydantic Settings with environment variable support
- 📝 **Auto Documentation**: Swagger UI for HTTP API
- 🔧 **Flexible Deployment**: Run HTTP server or MCP server independently
- 📋 **Request Tracing**: Request ID middleware for request tracking
- 📝 **Structured Logging**: Loguru-based logging with request ID integration
- 🔌 **Remote MCP Support**: Optional HTTP client for remote tool server integration


## Quick Start

### Prerequisites

- Python >= 3.12
- `uv` package manager (recommended)

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd computer-use-mcp
```

2. Install dependencies based on your deployment scenario:

#### Local Full Development
For local development with all features (GUI control + testing):
```bash
uv sync --group gui --group dev
```

#### Deploy MCP Server Only
For deploying MCP server that connects to remote tool service (no GUI dependencies needed):
```bash
uv sync --no-group gui
```

#### Deploy Tool Service Only
For deploying HTTP tool service that performs actual computer control (requires GUI):
```bash
uv sync --group gui
```

### Running the Service

The service supports two independent servers:

#### 1. Run Tool Service (HTTP API)
Starts the HTTP API server for computer control:
```bash
uv run python tool.py
```

#### 2. Run MCP Server
Starts the MCP server that can connect to remote tool services. The server supports two transport modes:

**HTTP Transport Mode:**
```bash
uv run python mcp_local.py http
```

**stdio Transport Mode (default):**
```bash
uv run python mcp_local.py stdio
```

After starting, you can access:

- **HTTP API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health
- **MCP Endpoint**: http://localhost:8001/mcp (if using HTTP transport)

## API Endpoints

### Base Endpoints

- `GET /` - Root path, returns API information
- `GET /health` - Health check endpoint

### Computer Control Endpoints

All computer control actions are available at:
- `POST /api/computer/{action}` - Execute a computer control action
- `GET /api/computer/actions` - List all available actions

#### Available Actions

| Action | Description | Parameters |
|--------|-------------|------------|
| `MoveMouse` | Move mouse cursor | `x`, `y` (coordinates) |
| `ClickMouse` | Click mouse button | `x`, `y`, `button`, `press`, `release` |
| `PressMouse` | Press mouse button (hold) | `x`, `y`, `button` |
| `ReleaseMouse` | Release mouse button | `x`, `y`, `button` |
| `DragMouse` | Drag mouse from source to target | `source_x`, `source_y`, `target_x`, `target_y` |
| `Scroll` | Scroll mouse wheel | `scroll_direction`, `scroll_amount`, `x`, `y` |
| `PressKey` | Press keyboard key(s) | `key` (e.g., "enter", "ctrl c") |
| `TypeText` | Type text (uses clipboard) | `text` |
| `Wait` | Wait for duration | `duration` (milliseconds) |
| `TakeScreenshot` | Capture screen | (no parameters) |
| `GetCursorPosition` | Get mouse position | (no parameters) |
| `GetScreenSize` | Get screen resolution | (no parameters) |

### Example API Usage

#### Move Mouse
```bash
curl -X POST "http://localhost:8000/api/computer/MoveMouse" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-secret-api-key-here" \
  -d '{"x": 100, "y": 200}'
```

#### Click Mouse
```bash
curl -X POST "http://localhost:8000/api/computer/ClickMouse" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-secret-api-key-here" \
  -d '{"x": 100, "y": 200, "button": "left"}'
```

#### Take Screenshot
```bash
curl -X POST "http://localhost:8000/api/computer/TakeScreenshot" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-secret-api-key-here" \
  -d '{}'
```

#### Get Cursor Position
```bash
curl -X POST "http://localhost:8000/api/computer/GetCursorPosition" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-secret-api-key-here" \
  -d '{}'
```

**Note**: If `API_KEY_ENABLED=false`, the `X-API-Key` header is optional. If `API_KEY_ENABLED=true`, the header is required for all requests except health checks and documentation endpoints.

## MCP Tools

The service also exposes all computer control operations as MCP tools. When running the MCP server, you can use these tools through any MCP-compatible client.

### Available MCP Tools

All HTTP API actions are available as MCP tools. The MCP tool names use snake_case, while the HTTP API uses PascalCase:
- `move_mouse` - Move mouse cursor (HTTP: `MoveMouse`)
- `click_mouse` - Click mouse button (HTTP: `ClickMouse`)
- `press_mouse` - Press mouse button (HTTP: `PressMouse`)
- `release_mouse` - Release mouse button (HTTP: `ReleaseMouse`)
- `drag_mouse` - Drag mouse (HTTP: `DragMouse`)
- `scroll` - Scroll mouse wheel (HTTP: `Scroll`)
- `press_key` - Press keyboard key (HTTP: `PressKey`)
- `type_text` - Type text (HTTP: `TypeText`)
- `wait` - Wait for duration (HTTP: `Wait`)
- `take_screenshot` - Take screenshot (HTTP: `TakeScreenshot`)
- `get_cursor_position` - Get cursor position (HTTP: `GetCursorPosition`)
- `get_screen_size` - Get screen size (HTTP: `GetScreenSize`)

### MCP Transport Modes

The MCP server supports two transport modes:

1. **stdio** (default): Standard input/output transport
   - Used for local communication via stdin/stdout
   - Suitable for direct integration with MCP clients
   - Start with: `python mcp_local.py stdio`

2. **http**: HTTP-based transport with stateless mode
   - Used for remote communication over HTTP
   - Suitable for service-to-service communication
   - Start with: `python mcp_local.py http`
   - Accessible at: `http://localhost:8001/mcp`

### MCP Tool Registration Modes

The service supports two modes of MCP tool registration:

1. **Direct Tools** (`register_computer_tools`): Tools that directly call the local computer control implementation. No `endpoint` parameter required.
   - Used in `mcp_local.py` for local MCP server
   - Tools execute computer control actions directly

2. **Client-based Tools** (`register_computer_tools_with_client`): Tools that use an HTTP client to call a remote tool server. Requires an `endpoint` parameter.
   - Used in `mcp_server/register.py` for remote MCP server
   - Tools forward requests to a remote tool service via HTTP

The local MCP server (`mcp_local.py`) uses direct tools by default. The remote MCP server uses client-based tools.

### Code Style

- Use type hints for all function parameters and return types
- Follow PEP 8 style guidelines
- Use descriptive docstrings for all public functions
- Keep functions focused and single-purpose

## Security Considerations

⚠️ **Warning**: This service provides direct control over your computer's mouse and keyboard. Use with caution:

- Only run on trusted networks
- Restrict CORS origins in production (currently allows all origins)
- **Enable API Key Authentication**: Set `API_KEY_ENABLED=true` and configure a strong `API_KEY` in production
- Be aware of the security implications of remote computer control

### API Key Authentication

The service supports optional API key authentication for securing service-to-service communication:

1. **Enable Authentication**: Set `API_KEY_ENABLED=true` in your `.env` file
2. **Set API Key**: Configure `API_KEY=your-secret-api-key-here` in your `.env` file
3. **Pass API Key in Requests**: Include the API key in request headers:
   - `X-API-Key: your-secret-api-key-here` (recommended)
   - `Authorization: Bearer your-secret-api-key-here` (alternative)

**Excluded Paths** (no authentication required):
- `/health` - Health check endpoint
- `/docs` - API documentation
- `/openapi.json` - OpenAPI schema
- `/redoc` - Alternative API documentation

**MCP Client Usage with API Key**:
```python
from fastmcp import Client
from fastmcp.client.transports import StreamableHttpTransport

# Create transport with API key
transport = StreamableHttpTransport(
    url="http://localhost:8001/mcp",
    headers={"X-API-Key": "your-secret-api-key-here"}
)

# Create client with transport
client = Client(transport)
async with client:
    response = await client.call_tool("move_mouse", {"x": 100, "y": 200})
```

## Logging

The service uses Loguru for structured logging with the following features:

- **Request ID Tracking**: Each request gets a unique ID that appears in all log entries
- **Environment-aware**: Console output in development, file logging in production
- **Structured Format**: Includes timestamp, level, request ID, module, function, and line number

Log files are stored in the `logs/` directory:
- `app_YYYY-MM-DD.log`: General application logs
- `error_YYYY-MM-DD.log`: Error logs only

In development mode, logs are only output to the console. In production mode, logs are written to both console and files.

## Testing

Run tests using pytest:
```bash
# Run all tests
uv pytest

# Run specific test file
uvpytest tests/test_mcp_client.py

# Run with verbose output
pytest -v
```

The test suite includes:
- `test_local_mcp_client.py`: Tests for local MCP server with HTTP transport (direct tools)
- `test_stdio_mcp_client.py`: Tests for local MCP server with stdio transport (direct tools)
- `test_mcp_client.py`: Tests for remote MCP server with client-based tools (requires endpoint parameter)

## Troubleshooting

### Port Already in Use

If you get a port already in use error:
```bash
# Change ports in .env file
PORT=8002
MCP_PORT=8003
```

### MCP Connection Issues

For HTTP transport, ensure the MCP server is running and accessible:
```bash
# Test MCP endpoint
curl http://localhost:8001/mcp

# Test with API key (if enabled)
curl -H "X-API-Key: your-secret-api-key-here" http://localhost:8001/mcp
```

For stdio transport, ensure the MCP server is started with stdio mode:
```bash
# Start MCP server in stdio mode
uv python mcp_local.py stdio
```

### API Key Authentication Issues

If you're getting authentication errors:
- Verify `API_KEY_ENABLED` is set correctly in `.env`
- Check that `API_KEY` matches between client and server
- Ensure the API key is passed in the `X-API-Key` header or `Authorization: Bearer <key>` header
- Check that the request path is not in the excluded paths list

### Screenshot Issues

If screenshot functionality fails:
- Check Python version compatibility (requires Python >= 3.12)
- Verify display permissions on macOS/Linux
- Ensure PyAutoGUI and its dependencies are properly installed


## License

[MIT license](./LICENSE)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
