"""config.py - 全局配置管理"""

from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    WEBHOOK_BASE_PATH: str = Field("/webhook", description="Webhook 路径前缀")
    SECRET_TOKEN: str = Field("", description="Webhook 验证密钥（可选）")
    HTTP_TIMEOUT: int = Field(30, description="HTTP 请求超时时间（秒）")
    HTTP_RETRY: int = Field(0, description="HTTP 请求重试次数（简化，默认不重试）")

    class Config:
        env_file = ".env"

settings = Settings()