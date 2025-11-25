"""应用配置"""
from typing import List
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """应用配置类"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Telegram Bot配置
    BOT_TOKEN: str = Field(..., description="Telegram Bot Token")
    BOT_USERNAME: str = Field(default="", description="Bot用户名")

    # 数据库配置
    DATABASE_URL: str = Field(
        default="sqlite+aiosqlite:///./data/xiuxian.db",
        description="数据库连接URL"
    )

    # Redis配置（可选）
    REDIS_HOST: str = Field(default="localhost", description="Redis主机")
    REDIS_PORT: int = Field(default=6379, description="Redis端口")
    REDIS_DB: int = Field(default=0, description="Redis数据库")
    REDIS_PASSWORD: str = Field(default="", description="Redis密码")

    # 游戏配置
    GAME_NAME: str = Field(default="修仙世界", description="游戏名称")
    GAME_VERSION: str = Field(default="1.0.0", description="游戏版本")

    # 修炼配置
    BASE_CULTIVATION_RATE: int = Field(default=100, description="基础修炼速度（修为/小时）")
    BREAKTHROUGH_BASE_CHANCE: float = Field(default=0.7, description="基础突破成功率")
    CULTIVATION_MIN_DURATION: int = Field(default=60, description="最小修炼时长（秒）")
    CULTIVATION_MAX_DURATION: int = Field(default=86400, description="最大修炼时长（秒）")

    # 战斗配置
    PVE_COOLDOWN: int = Field(default=300, description="PVE战斗冷却时间（秒）")
    PVP_COOLDOWN: int = Field(default=600, description="PVP战斗冷却时间（秒）")
    MAX_BATTLE_ROUNDS: int = Field(default=50, description="最大战斗回合数")

    # 经济配置
    DAILY_SIGN_REWARD: int = Field(default=1000, description="每日签到奖励灵石")
    NEWBIE_GIFT: int = Field(default=5000, description="新手礼包灵石")
    MARKET_TAX_RATE: float = Field(default=0.05, description="交易税率")

    # 宗门配置（已平衡优化）
    SECT_CREATE_COST: int = Field(default=50000, description="创建宗门消耗灵石（已降低50%）")
    SECT_MAX_MEMBERS_BASE: int = Field(default=20, description="宗门基础最大成员数")

    # 日志配置
    LOG_LEVEL: str = Field(default="INFO", description="日志级别")
    LOG_FILE: str = Field(default="./data/logs/xiuxian.log", description="日志文件路径")

    # 管理员配置
    ADMIN_IDS: List[int] = Field(default_factory=list, description="管理员Telegram ID列表")

    @property
    def is_production(self) -> bool:
        """是否生产环境"""
        return self.LOG_LEVEL == "INFO"

    @property
    def redis_url(self) -> str:
        """Redis连接URL"""
        if self.REDIS_PASSWORD:
            return f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"


settings = Settings()
