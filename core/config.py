from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    """Application settings class, automatically loads configuration from .env file"""
    environment : str = Field(default="development", description="Environment")

    # API configuration
    title: str = Field(default="Computer Use MCP Service", description="API title")
    version: str = Field(default="0.1.0", description="API version")
    api_prefix: str = Field(default="/api", description="API route prefix")

    # Server configuration
    host: str = Field(default="0.0.0.0", description="Server listening address")
    port: int = Field(default=8000, description="Server port")
    reload: bool = Field(default=True, description="Auto reload in development mode")

    # MCP configuration
    mcp_host: str = Field(default="0.0.0.0", description="MCP listening address")
    mcp_port: int = Field(default=8001, description="MCP port")
    mcp_transport: str = Field(default="stdio", description="MCP transport protocol")
    mcp_remote: bool = Field(default=False, description="Enable remote MCP to Tool server")
    
    # Security configuration
    api_key: str = Field(default="", description="API key for service-to-service authentication")
    api_key_enabled: bool = Field(default=False, description="Enable API key authentication")
    
    # Computer control configuration
    drag_step: int = Field(default=30, description="Step size for mouse drag operations")
    mouse_operate_interval: float = Field(default=0.1, description="Interval between mouse operations in seconds")
    scroll_scale: int = Field(default=100, description="Scale factor for scroll amount")
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )
    
    
# Create global settings instance
settings = Settings()

