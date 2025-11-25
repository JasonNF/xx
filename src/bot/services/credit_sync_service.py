"""跨项目积分同步服务

支持多项目间积分打通，实现统一积分账户。
设计原则：
1. 积分记录可追溯来源项目
2. 支持双向同步
3. 防止重复同步
4. 支持积分冻结/解冻（用于跨项目事务）
"""
import hashlib
import hmac
import json
import time
from datetime import datetime
from typing import Optional, Tuple, Dict, Any
from enum import Enum

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from bot.models import Player, PlayerCreditRecord, CreditType


class SyncSource(str, Enum):
    """积分来源项目"""
    XIUXIAN_GAME = "xiuxian_game"       # 修仙游戏
    MEDIA_BOT = "media_bot"             # 媒体机器人（另一个项目）
    EXTERNAL_API = "external_api"       # 外部API调用
    ADMIN = "admin"                     # 管理员操作


class CreditSyncService:
    """积分同步服务"""

    # 用于验证跨项目请求的密钥（生产环境应从配置读取）
    SYNC_SECRET_KEY = "your-secret-key-here"

    @staticmethod
    def generate_sync_token(
        user_id: int,
        amount: int,
        source: str,
        timestamp: int
    ) -> str:
        """生成同步验证令牌

        Args:
            user_id: 用户ID（Telegram ID）
            amount: 积分数量
            source: 来源项目
            timestamp: 时间戳

        Returns:
            验证令牌
        """
        message = f"{user_id}:{amount}:{source}:{timestamp}"
        signature = hmac.new(
            CreditSyncService.SYNC_SECRET_KEY.encode(),
            message.encode(),
            hashlib.sha256
        ).hexdigest()
        return signature

    @staticmethod
    def verify_sync_token(
        user_id: int,
        amount: int,
        source: str,
        timestamp: int,
        token: str,
        max_age: int = 300  # 5分钟有效期
    ) -> bool:
        """验证同步令牌

        Args:
            user_id: 用户ID
            amount: 积分数量
            source: 来源项目
            timestamp: 时间戳
            token: 待验证的令牌
            max_age: 最大有效期（秒）

        Returns:
            是否有效
        """
        # 检查时间戳
        current_time = int(time.time())
        if abs(current_time - timestamp) > max_age:
            return False

        # 验证签名
        expected_token = CreditSyncService.generate_sync_token(
            user_id, amount, source, timestamp
        )
        return hmac.compare_digest(token, expected_token)

    @staticmethod
    async def sync_credits_from_external(
        db: AsyncSession,
        telegram_id: int,
        amount: int,
        source: SyncSource,
        reason: str,
        external_reference: Optional[str] = None,
        token: Optional[str] = None,
        timestamp: Optional[int] = None
    ) -> Tuple[bool, str, Optional[int]]:
        """从外部项目同步积分

        Args:
            db: 数据库会话
            telegram_id: Telegram用户ID
            amount: 积分数量（正数增加，负数扣除）
            source: 来源项目
            reason: 同步原因
            external_reference: 外部引用ID（用于去重）
            token: 验证令牌（可选，用于安全验证）
            timestamp: 时间戳（配合token使用）

        Returns:
            (success, message, new_balance)
        """
        # 验证令牌（如果提供）
        if token and timestamp:
            if not CreditSyncService.verify_sync_token(
                telegram_id, amount, source.value, timestamp, token
            ):
                return False, "同步验证失败：无效的令牌", None

        # 查找玩家
        result = await db.execute(
            select(Player).where(Player.telegram_id == telegram_id)
        )
        player = result.scalar_one_or_none()

        if not player:
            return False, f"玩家不存在：Telegram ID {telegram_id}", None

        # 检查是否重复同步（通过external_reference去重）
        if external_reference:
            existing = await db.execute(
                select(PlayerCreditRecord).where(
                    and_(
                        PlayerCreditRecord.player_id == player.id,
                        PlayerCreditRecord.reason.contains(f"[REF:{external_reference}]")
                    )
                )
            )
            if existing.scalar_one_or_none():
                return False, f"重复同步：引用ID {external_reference} 已处理", player.credits

        # 检查余额（扣除时）
        if amount < 0 and player.credits < abs(amount):
            return False, f"积分不足：需要 {abs(amount)}，当前 {player.credits}", player.credits

        # 执行积分变动
        credit_before = player.credits
        player.credits += amount
        credit_after = player.credits

        # 构建原因（包含来源和引用）
        full_reason = f"[{source.value}] {reason}"
        if external_reference:
            full_reason += f" [REF:{external_reference}]"

        # 记录变动
        record = PlayerCreditRecord(
            player_id=player.id,
            credit_change=amount,
            credit_before=credit_before,
            credit_after=credit_after,
            credit_type=CreditType.ACTIVITY_REWARD if amount > 0 else CreditType.EXCHANGE_DEDUCT,
            reason=full_reason,
            reference_id=None
        )

        db.add(record)
        await db.commit()
        await db.refresh(player)

        action = "增加" if amount > 0 else "扣除"
        return True, f"同步成功：{action} {abs(amount)} 积分", player.credits

    @staticmethod
    async def get_player_credits_for_sync(
        db: AsyncSession,
        telegram_id: int
    ) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """获取玩家积分信息（用于同步）

        Args:
            db: 数据库会话
            telegram_id: Telegram用户ID

        Returns:
            (success, message, data)
        """
        result = await db.execute(
            select(Player).where(Player.telegram_id == telegram_id)
        )
        player = result.scalar_one_or_none()

        if not player:
            return False, f"玩家不存在：Telegram ID {telegram_id}", None

        # 获取最近的积分记录
        records_result = await db.execute(
            select(PlayerCreditRecord)
            .where(PlayerCreditRecord.player_id == player.id)
            .order_by(PlayerCreditRecord.created_at.desc())
            .limit(10)
        )
        records = records_result.scalars().all()

        data = {
            "telegram_id": telegram_id,
            "player_id": player.id,
            "nickname": player.nickname,
            "credits": player.credits,
            "recent_records": [
                {
                    "id": r.id,
                    "change": r.credit_change,
                    "type": r.credit_type.value,
                    "reason": r.reason,
                    "created_at": r.created_at.isoformat()
                }
                for r in records
            ],
            "sync_time": datetime.now().isoformat()
        }

        return True, "获取成功", data

    @staticmethod
    async def batch_sync_credits(
        db: AsyncSession,
        sync_items: list[Dict[str, Any]],
        source: SyncSource
    ) -> Dict[str, Any]:
        """批量同步积分

        Args:
            db: 数据库会话
            sync_items: 同步项列表，每项包含：
                - telegram_id: int
                - amount: int
                - reason: str
                - external_reference: Optional[str]
            source: 来源项目

        Returns:
            批量处理结果
        """
        results = {
            "total": len(sync_items),
            "success": 0,
            "failed": 0,
            "details": []
        }

        for item in sync_items:
            success, message, balance = await CreditSyncService.sync_credits_from_external(
                db=db,
                telegram_id=item["telegram_id"],
                amount=item["amount"],
                source=source,
                reason=item.get("reason", "批量同步"),
                external_reference=item.get("external_reference")
            )

            if success:
                results["success"] += 1
            else:
                results["failed"] += 1

            results["details"].append({
                "telegram_id": item["telegram_id"],
                "success": success,
                "message": message,
                "balance": balance
            })

        return results

    @staticmethod
    def create_sync_request(
        telegram_id: int,
        amount: int,
        source: SyncSource,
        reason: str,
        external_reference: Optional[str] = None
    ) -> Dict[str, Any]:
        """创建同步请求数据（供其他项目调用）

        Args:
            telegram_id: Telegram用户ID
            amount: 积分数量
            source: 来源项目
            reason: 原因
            external_reference: 外部引用ID

        Returns:
            同步请求数据（包含验证令牌）
        """
        timestamp = int(time.time())
        token = CreditSyncService.generate_sync_token(
            telegram_id, amount, source.value, timestamp
        )

        return {
            "telegram_id": telegram_id,
            "amount": amount,
            "source": source.value,
            "reason": reason,
            "external_reference": external_reference,
            "timestamp": timestamp,
            "token": token
        }


# 便捷函数
async def sync_credits_in(
    db: AsyncSession,
    telegram_id: int,
    amount: int,
    source: str,
    reason: str,
    reference: Optional[str] = None
) -> Tuple[bool, str]:
    """从外部增加积分（便捷函数）"""
    try:
        source_enum = SyncSource(source)
    except ValueError:
        source_enum = SyncSource.EXTERNAL_API

    success, message, _ = await CreditSyncService.sync_credits_from_external(
        db, telegram_id, abs(amount), source_enum, reason, reference
    )
    return success, message


async def sync_credits_out(
    db: AsyncSession,
    telegram_id: int,
    amount: int,
    source: str,
    reason: str,
    reference: Optional[str] = None
) -> Tuple[bool, str]:
    """向外部扣除积分（便捷函数）"""
    try:
        source_enum = SyncSource(source)
    except ValueError:
        source_enum = SyncSource.EXTERNAL_API

    success, message, _ = await CreditSyncService.sync_credits_from_external(
        db, telegram_id, -abs(amount), source_enum, reason, reference
    )
    return success, message
