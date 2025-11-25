"""积分同步API服务器

独立的FastAPI服务器，用于提供跨项目积分同步的RESTful API。

运行方式：
    开发环境：python3 api_server.py
    生产环境：uvicorn api_server:app --host 0.0.0.0 --port 8000

API文档：
    启动后访问 http://localhost:8000/docs 查看Swagger文档
    或访问 http://localhost:8000/redoc 查看ReDoc文档
"""
import sys
import asyncio
from pathlib import Path

# 添加项目路径到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from bot.api.credit_sync_api import router as credit_router
from bot.models import init_db, close_db

# 创建FastAPI应用
app = FastAPI(
    title="修仙游戏积分同步API",
    version="1.0.0",
    description="""
## 积分同步API

跨项目积分同步服务，支持：
- 单笔积分同步（增加/扣除）
- 批量积分同步
- 积分余额查询
- 积分记录查询
- Webhook回调通知

## 认证方式

所有请求需要在Header中提供API密钥：
```
X-Api-Key: your-api-key-here
```

## 安全机制

- HMAC-SHA256令牌验证
- 时间戳验证（5分钟有效期）
- 去重机制（external_reference）
- API密钥认证

## 文档

详细文档请参考项目的 docs/ 目录：
- 积分同步API文档.md
- 积分同步部署指南.md
- 积分同步快速开始.md
    """,
    docs_url="/docs",
    redoc_url="/redoc"
)

# 配置CORS（如果需要跨域访问）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应该限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """应用启动事件"""
    print("🚀 启动积分同步API服务...")
    print("📊 初始化数据库连接...")

    # 初始化数据库
    await init_db()

    print("✅ 数据库初始化完成")
    print("📡 API服务已就绪")
    print("📖 API文档: http://localhost:8000/docs")
    print("📖 ReDoc文档: http://localhost:8000/redoc")


@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭事件"""
    print("🛑 关闭积分同步API服务...")

    # 关闭数据库连接
    await close_db()

    print("✅ 服务已安全关闭")


# 健康检查端点
@app.get("/", tags=["system"])
async def root():
    """根路径 - 服务状态检查"""
    return {
        "service": "修仙游戏积分同步API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "redoc": "/redoc"
    }


@app.get("/health", tags=["system"])
async def health_check():
    """健康检查端点"""
    return {
        "status": "healthy",
        "service": "credit_sync_api",
        "version": "1.0.0"
    }


# 注册积分同步路由
app.include_router(credit_router)


# 主程序入口
if __name__ == "__main__":
    import uvicorn

    print("="*60)
    print("🎮 修仙游戏 - 积分同步API服务器")
    print("="*60)

    # 开发环境配置
    uvicorn.run(
        "api_server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # 开发模式：自动重载
        log_level="info",
        access_log=True
    )
