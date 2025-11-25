"""积分同步API接口

提供RESTful API供其他项目调用，实现跨项目积分打通。

使用方式：
1. 其他项目通过HTTP请求调用这些接口
2. 需要提供验证令牌（token）进行安全验证
3. 支持单笔��批量同步

API端点：
- POST /api/credits/sync - 同步积分（单笔）
- POST /api/credits/sync/batch - 批量同步积分
- GET /api/credits/balance/{telegram_id} - 查询积分余额
- GET /api/credits/records/{telegram_id} - 查询积分记录
"""
from typing import Optional, List
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Header, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from bot.models import get_db
from bot.services.credit_sync_service import (
    CreditSyncService,
    SyncSource,
    sync_credits_in,
    sync_credits_out
)

# 创建路由
router = APIRouter(prefix="/api/credits", tags=["credits"])


# ============================================
# 请求/响应模型
# ============================================

class SyncCreditRequest(BaseModel):
    """同步积分请求"""
    telegram_id: int = Field(..., description="Telegram用户ID")
    amount: int = Field(..., description="积分数量（正数增加，负数扣除）")
    source: str = Field(..., description="来���项目")
    reason: str = Field(..., description="变动原因")
    external_reference: Optional[str] = Field(None, description="外部引用ID（用于去重）")
    timestamp: int = Field(..., description="请求时间戳")
    token: str = Field(..., description="验证令牌")

    class Config:
        json_schema_extra = {
            "example": {
                "telegram_id": 123456789,
                "amount": 100,
                "source": "media_bot",
                "reason": "观看视频奖励",
                "external_reference": "video_12345",
                "timestamp": 1234567890,
                "token": "abc123def456..."
            }
        }


class BatchSyncItem(BaseModel):
    """批量同步项"""
    telegram_id: int
    amount: int
    reason: str
    external_reference: Optional[str] = None


class BatchSyncRequest(BaseModel):
    """批量同步请求"""
    source: str = Field(..., description="来源项目")
    items: List[BatchSyncItem] = Field(..., description="同步项列表")
    timestamp: int = Field(..., description="请求时间戳")
    token: str = Field(..., description="批量验证令牌")


class CreditResponse(BaseModel):
    """积分响应"""
    success: bool
    message: str
    data: Optional[dict] = None


class BalanceResponse(BaseModel):
    """余额查询响应"""
    telegram_id: int
    credits: int
    nickname: str
    sync_time: str


class RecordItem(BaseModel):
    """积分记录项"""
    id: int
    change: int
    type: str
    reason: str
    created_at: str


class RecordsResponse(BaseModel):
    """记录查询响应"""
    telegram_id: int
    credits: int
    records: List[RecordItem]


# ============================================
# 辅助函数
# ============================================

def verify_api_key(x_api_key: Optional[str] = Header(None)) -> bool:
    """验证API密钥

    Args:
        x_api_key: 请求头中的API密钥

    Returns:
        是否有效

    Raises:
        HTTPException: 验证失败
    """
    # TODO: 从配置读取有效的API密钥列表
    VALID_API_KEYS = [
        "xiuxian-api-key-2024",
        "media-bot-api-key-2024"
    ]

    if not x_api_key or x_api_key not in VALID_API_KEYS:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key"
        )
    return True


# ============================================
# API端点
# ============================================

@router.post("/sync", response_model=CreditResponse)
async def sync_credits(
    request: SyncCreditRequest,
    db: AsyncSession = Depends(get_db),
    _: bool = Depends(verify_api_key)
):
    """同步积分（单笔）

    Args:
        request: 同步请求
        db: 数据库会话
        _: API密钥验证

    Returns:
        同步结果
    """
    try:
        source = SyncSource(request.source)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid source: {request.source}"
        )

    success, message, balance = await CreditSyncService.sync_credits_from_external(
        db=db,
        telegram_id=request.telegram_id,
        amount=request.amount,
        source=source,
        reason=request.reason,
        external_reference=request.external_reference,
        token=request.token,
        timestamp=request.timestamp
    )

    return CreditResponse(
        success=success,
        message=message,
        data={"balance": balance} if balance is not None else None
    )


@router.post("/sync/batch", response_model=CreditResponse)
async def batch_sync_credits(
    request: BatchSyncRequest,
    db: AsyncSession = Depends(get_db),
    _: bool = Depends(verify_api_key)
):
    """批量同步积分

    Args:
        request: 批量同步请求
        db: 数据库会话
        _: API密钥验证

    Returns:
        批量处理结果
    """
    try:
        source = SyncSource(request.source)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid source: {request.source}"
        )

    # 转换为字典列表
    sync_items = [item.model_dump() for item in request.items]

    result = await CreditSyncService.batch_sync_credits(
        db=db,
        sync_items=sync_items,
        source=source
    )

    return CreditResponse(
        success=result["success"] > 0,
        message=f"处理完成：成功 {result['success']}，失败 {result['failed']}",
        data=result
    )


@router.get("/balance/{telegram_id}", response_model=BalanceResponse)
async def get_balance(
    telegram_id: int,
    db: AsyncSession = Depends(get_db),
    _: bool = Depends(verify_api_key)
):
    """查询积分余额

    Args:
        telegram_id: Telegram用户ID
        db: 数据库会话
        _: API密钥验证

    Returns:
        余额信息
    """
    success, message, data = await CreditSyncService.get_player_credits_for_sync(
        db=db,
        telegram_id=telegram_id
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=message
        )

    return BalanceResponse(
        telegram_id=data["telegram_id"],
        credits=data["credits"],
        nickname=data["nickname"],
        sync_time=data["sync_time"]
    )


@router.get("/records/{telegram_id}", response_model=RecordsResponse)
async def get_records(
    telegram_id: int,
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
    _: bool = Depends(verify_api_key)
):
    """查询积分记录

    Args:
        telegram_id: Telegram用户ID
        limit: 返回记录数量
        db: 数据库会话
        _: API密钥验证

    Returns:
        积分记录
    """
    success, message, data = await CreditSyncService.get_player_credits_for_sync(
        db=db,
        telegram_id=telegram_id
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=message
        )

    # 限制返回数量
    records = data["recent_records"][:limit]

    return RecordsResponse(
        telegram_id=data["telegram_id"],
        credits=data["credits"],
        records=[RecordItem(**r) for r in records]
    )


@router.post("/token/generate")
async def generate_token(
    telegram_id: int,
    amount: int,
    source: str,
    _: bool = Depends(verify_api_key)
):
    """生成同步令牌（供其他项目调用）

    Args:
        telegram_id: Telegram用户ID
        amount: 积分数量
        source: 来源项目
        _: API密钥验证

    Returns:
        令牌信息
    """
    try:
        source_enum = SyncSource(source)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid source: {source}"
        )

    sync_request = CreditSyncService.create_sync_request(
        telegram_id=telegram_id,
        amount=amount,
        source=source_enum,
        reason="令牌生成"
    )

    return CreditResponse(
        success=True,
        message="令牌生成成功",
        data=sync_request
    )


# ============================================
# Webhook回调（可选）
# ============================================

class WebhookRequest(BaseModel):
    """Webhook请求"""
    event: str = Field(..., description="事件类型")
    telegram_id: int
    amount: int
    source: str
    reason: str
    timestamp: int
    signature: str


@router.post("/webhook")
async def webhook_handler(
    request: WebhookRequest,
    db: AsyncSession = Depends(get_db),
    _: bool = Depends(verify_api_key)
):
    """Webhook回调处理

    用于接收其他项目的异步通知
    """
    # 验证签名
    expected_signature = CreditSyncService.generate_sync_token(
        request.telegram_id,
        request.amount,
        request.source,
        request.timestamp
    )

    if request.signature != expected_signature:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid signature"
        )

    # 根据事件类型处理
    if request.event == "credit_earned":
        success, message = await sync_credits_in(
            db, request.telegram_id, request.amount,
            request.source, request.reason
        )
    elif request.event == "credit_spent":
        success, message = await sync_credits_out(
            db, request.telegram_id, request.amount,
            request.source, request.reason
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unknown event: {request.event}"
        )

    return CreditResponse(
        success=success,
        message=message
    )
