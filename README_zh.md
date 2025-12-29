<p align="center"><a href="" target="_blank"><img src="./mcp-autogui-multinode.png?raw=true"></a></p>

<p align="center">
<a href="./"><img src="https://img.shields.io/badge/License-MIT-blue.svg" alt="License MIT"></a>
</p>

[English](./README.md)|[中文](./README_zh.md)  

### 关于

一个用于 PyAutoGUI 的 MCP 和 HTTP 服务器包装器，使 LLM 能够控制您的鼠标和键盘。

### 架构

该服务支持两种部署架构：

#### LLM -> MCP -> TOOL (远程工具服务)

此架构将 MCP 服务器与工具服务分离，允许 MCP 服务器通过 HTTP 连接到远程工具服务。

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

**特点：**
- MCP 服务器使用**基于客户端的工具** (`register_computer_tools_with_client`)
- MCP 服务器通过 HTTP 将请求转发到远程工具服务
- 工具服务执行实际的计算机控制操作
- 适用于 MCP 服务器和工具服务运行在不同机器上的分布式部署
- 在 MCP 工具调用中需要 `endpoint` 参数

#### 架构 2: LLM -> MCP (直接工具)

此架构使用直接工具，MCP 服务器直接执行计算机控制操作。

```mermaid
graph LR
    LLM[LLM Client] -->|MCP Protocol<br/>stdio/http| MCP[MCP Server<br/>mcp_local.py<br/>Direct Tools]
    MCP -->|PyAutoGUI| COMPUTER[Computer Control]
    
    style LLM fill:#e1f5ff
    style MCP fill:#fff4e1
    style COMPUTER fill:#e1ffe1
```

**特点：**
- MCP 服务器使用**直接工具** (`register_computer_tools`)
- MCP 服务器直接执行计算机控制操作
- 不需要单独的工具服务
- 适用于所有组件在同一台机器上运行的本地部署
- MCP 工具调用中不需要 `endpoint` 参数

## 功能特性

- 🚀 **双协议支持**：HTTP REST API 和 MCP（模型上下文协议）
- 🔐 **API 密钥认证**：服务间通信的可选 API 密钥认证
- 🌐 **多种 MCP 传输方式**：支持 HTTP 和 stdio（标准输入/输出）传输模式
- 🖱️ **鼠标控制**：移动、点击、拖拽、滚动操作
- ⌨️ **键盘控制**：按键、输入文本、组合键
- 📸 **截图功能**：捕获屏幕并获取 base64 编码的图像
- 📊 **屏幕信息**：获取光标位置和屏幕分辨率
- ⚙️ **配置管理**：支持环境变量的 Pydantic Settings
- 📝 **自动文档**：HTTP API 的 Swagger UI
- 🔧 **灵活部署**：独立运行 HTTP 服务器或 MCP 服务器
- 📋 **请求追踪**：用于请求跟踪的请求 ID 中间件
- 📝 **结构化日志**：基于 Loguru 的日志记录，集成请求 ID
- 🔌 **远程 MCP 支持**：用于远程工具服务器集成的可选 HTTP 客户端


## 快速开始

### 前置要求

- Python >= 3.12
- `uv` 包管理器（推荐）

### 安装

1. 克隆仓库：
```bash
git clone https://github.com/stonehill-2345/mcp-autogui-multinode.git
cd mcp-autogui-multinode
```

2. 根据您的部署场景安装依赖：

#### 本地完整开发
用于本地开发，包含所有功能（GUI 控制 + 测试）：
```bash
uv sync --group gui --group dev
```

#### 仅部署 MCP 服务器
用于部署连接到远程工具服务的 MCP 服务器（不需要 GUI 依赖）：
```bash
uv sync --no-group gui
```

#### 仅部署工具服务
用于部署执行实际计算机控制的 HTTP 工具服务（需要 GUI）：
```bash
uv sync --group gui
```

### 运行服务

该服务支持两个独立的服务器：

#### 1. 运行工具服务（HTTP API）
启动用于计算机控制的 HTTP API 服务器：
```bash
uv run python tool.py
```

#### 2. 运行 MCP 服务器
启动可以连接到远程工具服务的 MCP 服务器。服务器支持两种传输模式：

**HTTP 传输模式：**
```bash
uv run python mcp_local.py http
```

**stdio 传输模式（默认）：**
```bash
uv run python mcp_local.py stdio
```

启动后，您可以访问：

- **HTTP API 文档**：http://localhost:8000/docs
- **健康检查**：http://localhost:8000/health
- **MCP 端点**：http://localhost:8001/mcp（如果使用 HTTP 传输）

## API 端点

### 基础端点

- `GET /` - 根路径，返回 API 信息
- `GET /health` - 健康检查端点

### 计算机控制端点

所有计算机控制操作都可在以下端点使用：
- `POST /api/computer/{action}` - 执行计算机控制操作
- `GET /api/computer/actions` - 列出所有可用操作

#### 可用操作

| 操作 | 描述 | 参数 |
|--------|-------------|------------|
| `MoveMouse` | 移动鼠标光标 | `x`, `y`（坐标） |
| `ClickMouse` | 点击鼠标按钮 | `x`, `y`, `button`, `press`, `release` |
| `PressMouse` | 按下鼠标按钮（按住） | `x`, `y`, `button` |
| `ReleaseMouse` | 释放鼠标按钮 | `x`, `y`, `button` |
| `DragMouse` | 从源位置拖拽鼠标到目标位置 | `source_x`, `source_y`, `target_x`, `target_y` |
| `Scroll` | 滚动鼠标滚轮 | `scroll_direction`, `scroll_amount`, `x`, `y` |
| `PressKey` | 按下键盘按键 | `key`（例如："enter", "ctrl c"） |
| `TypeText` | 输入文本（使用剪贴板） | `text` |
| `Wait` | 等待指定时长 | `duration`（毫秒） |
| `TakeScreenshot` | 捕获屏幕 | （无参数） |
| `GetCursorPosition` | 获取鼠标位置 | （无参数） |
| `GetScreenSize` | 获取屏幕分辨率 | （无参数） |

### API 使用示例

#### 移动鼠标
```bash
curl -X POST "http://localhost:8000/api/computer/MoveMouse" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-secret-api-key-here" \
  -d '{"x": 100, "y": 200}'
```

#### 点击鼠标
```bash
curl -X POST "http://localhost:8000/api/computer/ClickMouse" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-secret-api-key-here" \
  -d '{"x": 100, "y": 200, "button": "left"}'
```

#### 截图
```bash
curl -X POST "http://localhost:8000/api/computer/TakeScreenshot" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-secret-api-key-here" \
  -d '{}'
```

#### 获取光标位置
```bash
curl -X POST "http://localhost:8000/api/computer/GetCursorPosition" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-secret-api-key-here" \
  -d '{}'
```

**注意**：如果 `API_KEY_ENABLED=false`，`X-API-Key` 请求头是可选的。如果 `API_KEY_ENABLED=true`，除了健康检查和文档端点外，所有请求都需要该请求头。

## MCP 工具

该服务还将所有计算机控制操作公开为 MCP 工具。运行 MCP 服务器时，您可以通过任何兼容 MCP 的客户端使用这些工具。

### 可用的 MCP 工具

所有 HTTP API 操作都可用作 MCP 工具。MCP 工具名称使用 snake_case，而 HTTP API 使用 PascalCase：
- `move_mouse` - 移动鼠标光标（HTTP: `MoveMouse`）
- `click_mouse` - 点击鼠标按钮（HTTP: `ClickMouse`）
- `press_mouse` - 按下鼠标按钮（HTTP: `PressMouse`）
- `release_mouse` - 释放鼠标按钮（HTTP: `ReleaseMouse`）
- `drag_mouse` - 拖拽鼠标（HTTP: `DragMouse`）
- `scroll` - 滚动鼠标滚轮（HTTP: `Scroll`）
- `press_key` - 按下键盘按键（HTTP: `PressKey`）
- `type_text` - 输入文本（HTTP: `TypeText`）
- `wait` - 等待指定时长（HTTP: `Wait`）
- `take_screenshot` - 截图（HTTP: `TakeScreenshot`）
- `get_cursor_position` - 获取光标位置（HTTP: `GetCursorPosition`）
- `get_screen_size` - 获取屏幕大小（HTTP: `GetScreenSize`）

### MCP 传输模式

MCP 服务器支持两种传输模式：

1. **stdio**（默认）：标准输入/输出传输
   - 用于通过 stdin/stdout 进行本地通信
   - 适用于与 MCP 客户端的直接集成
   - 启动方式：`python mcp_local.py stdio`

2. **http**：基于 HTTP 的无状态传输
   - 用于通过 HTTP 进行远程通信
   - 适用于服务间通信
   - 启动方式：`python mcp_local.py http`
   - 访问地址：`http://localhost:8001/mcp`

### MCP 工具注册模式

该服务支持两种 MCP 工具注册模式：

1. **直接工具** (`register_computer_tools`)：直接调用本地计算机控制实现的工具。不需要 `endpoint` 参数。
   - 在 `mcp_local.py` 中用于本地 MCP 服务器
   - 工具直接执行计算机控制操作

2. **基于客户端的工具** (`register_computer_tools_with_client`)：使用 HTTP 客户端调用远程工具服务器的工具。需要 `endpoint` 参数。
   - 在 `mcp_server/register.py` 中用于远程 MCP 服务器
   - 工具通过 HTTP 将请求转发到远程工具服务

本地 MCP 服务器（`mcp_local.py`）默认使用直接工具。远程 MCP 服务器使用基于客户端的工具。

### 代码风格

- 为所有函数参数和返回类型使用类型提示
- 遵循 PEP 8 风格指南
- 为所有公共函数使用描述性文档字符串
- 保持函数专注和单一职责

## 安全注意事项

⚠️ **警告**：此服务提供对计算机鼠标和键盘的直接控制。请谨慎使用：

- 仅在受信任的网络上运行
- 在生产环境中限制 CORS 来源（当前允许所有来源）
- **启用 API 密钥认证**：在生产环境中设置 `API_KEY_ENABLED=true` 并配置强 `API_KEY`
- 注意远程计算机控制的安全影响

### API 密钥认证

该服务支持可选的 API 密钥认证，用于保护服务间通信：

1. **启用认证**：在 `.env` 文件中设置 `API_KEY_ENABLED=true`
2. **设置 API 密钥**：在 `.env` 文件中配置 `API_KEY=your-secret-api-key-here`
3. **在请求中传递 API 密钥**：在请求头中包含 API 密钥：
   - `X-API-Key: your-secret-api-key-here`（推荐）
   - `Authorization: Bearer your-secret-api-key-here`（替代方案）

**排除路径**（不需要认证）：
- `/health` - 健康检查端点
- `/docs` - API 文档
- `/openapi.json` - OpenAPI 架构
- `/redoc` - 替代 API 文档

**使用 API 密钥的 MCP 客户端用法**：
```python
from fastmcp import Client
from fastmcp.client.transports import StreamableHttpTransport

# 创建带有 API 密钥的传输
transport = StreamableHttpTransport(
    url="http://localhost:8001/mcp",
    headers={"X-API-Key": "your-secret-api-key-here"}
)

# 使用传输创建客户端
client = Client(transport)
async with client:
    response = await client.call_tool("move_mouse", {"x": 100, "y": 200})
```

## 日志记录

该服务使用 Loguru 进行结构化日志记录，具有以下功能：

- **请求 ID 追踪**：每个请求都有一个唯一的 ID，出现在所有日志条目中
- **环境感知**：开发环境输出到控制台，生产环境记录到文件
- **结构化格式**：包括时间戳、级别、请求 ID、模块、函数和行号

日志文件存储在 `logs/` 目录中：
- `app_YYYY-MM-DD.log`：常规应用程序日志
- `error_YYYY-MM-DD.log`：仅错误日志

在开发模式下，日志仅输出到控制台。在生产模式下，日志会同时写入控制台和文件。

## 测试

使用 pytest 运行测试：
```bash
# 运行所有测试
uv pytest

# 运行特定测试文件
uv pytest tests/test_mcp_client.py

# 运行详细输出
pytest -v
```

测试套件包括：
- `test_local_mcp_client.py`：本地 MCP 服务器与 HTTP 传输的测试（直接工具）
- `test_stdio_mcp_client.py`：本地 MCP 服务器与 stdio 传输的测试（直接工具）
- `test_mcp_client.py`：远程 MCP 服务器与基于客户端的工具的测试（需要 endpoint 参数）

## 故障排除

### 端口已被占用

如果遇到端口已被占用的错误：
```bash
# 在 .env 文件中更改端口
PORT=8002
MCP_PORT=8003
```

### MCP 连接问题

对于 HTTP 传输，确保 MCP 服务器正在运行且可访问：
```bash
# 测试 MCP 端点
curl http://localhost:8001/mcp

# 使用 API 密钥测试（如果已启用）
curl -H "X-API-Key: your-secret-api-key-here" http://localhost:8001/mcp
```

对于 stdio 传输，确保 MCP 服务器以 stdio 模式启动：
```bash
# 以 stdio 模式启动 MCP 服务器
uv run python mcp_local.py stdio
```

### API 密钥认证问题

如果遇到认证错误：
- 验证 `.env` 中 `API_KEY_ENABLED` 设置是否正确
- 检查客户端和服务器之间的 `API_KEY` 是否匹配
- 确保 API 密钥在 `X-API-Key` 请求头或 `Authorization: Bearer <key>` 请求头中传递
- 检查请求路径是否不在排除路径列表中

### 截图问题

如果截图功能失败：
- 检查 Python 版本兼容性（需要 Python >= 3.12）
- 在 macOS/Linux 上验证显示权限
- 确保 PyAutoGUI 及其依赖项已正确安装


## 许可证

[MIT 许可证](./LICENSE)

## 贡献

欢迎贡献！请随时提交 Pull Request。

