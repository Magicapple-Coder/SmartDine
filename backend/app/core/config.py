from functools import lru_cache
from urllib.parse import quote_plus

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """全局配置，从 .env 加载（对应 .env.example）"""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # 云端 MySQL
    DB_HOST: str = "127.0.0.1"
    DB_PORT: int = 3306
    DB_USER: str = "root"
    DB_PASSWORD: str = ""
    DB_NAME: str = "smartdine"

    # JWT
    JWT_SECRET: str = "change-me"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 720

    # Dify（Linux 虚拟机自托管）
    DIFY_BASE_URL: str = "http://127.0.0.1/v1"
    DIFY_ORDER_KEY: str = ""
    DIFY_STOCK_KEY: str = ""
    DIFY_SERVICE_KEY: str = ""
    DIFY_ANALYTICS_KEY: str = ""
    DIFY_TIMEOUT: int = 15

    # 微信
    WX_APPID: str = ""
    WX_SECRET: str = ""
    WX_PAY_MCHID: str = ""
    WX_PAY_KEY: str = ""

    # Redis（可选，用于会话缓存与租户隔离缓存）
    REDIS_HOST: str = "127.0.0.1"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: str = ""
    REDIS_DB: int = 0

    # 文件上传
    UPLOAD_BASE_PATH: str = "./uploads"

    @property
    def database_url(self) -> str:
        return (
            f"mysql+pymysql://{quote_plus(self.DB_USER)}:{quote_plus(self.DB_PASSWORD)}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}?charset=utf8mb4"
        )

    @property
    def redis_url(self) -> str:
        if self.REDIS_PASSWORD:
            return f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
