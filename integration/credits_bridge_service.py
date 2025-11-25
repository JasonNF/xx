"""
PMS积分桥接服务
用于连接PMSManageBot的积分系统和修仙游戏的灵石系统
"""
import sqlite3
from datetime import datetime, date
from typing import Tuple, Optional
from pathlib import Path


class CreditsBridgeService:
    """PMS积分桥接服务"""

    def __init__(self, pms_db_path: str):
        """
        初始化积分桥接服务

        Args:
            pms_db_path: PMSManageBot数据库路径
        """
        self.pms_db_path = pms_db_path

    def _get_pms_connection(self) -> sqlite3.Connection:
        """获取PMS数据库连接"""
        con = sqlite3.connect(self.pms_db_path)
        con.row_factory = sqlite3.Row
        return con

    def get_pms_credits(self, telegram_id: int) -> int:
        """获取PMS积分余额

        Args:
            telegram_id: Telegram用户ID

        Returns:
            积分余额，如果用户不存在返回0
        """
        con = self._get_pms_connection()
        cur = con.cursor()

        # 尝试从user表获取
        cur.execute("SELECT credits FROM user WHERE tg_id = ?", (telegram_id,))
        row = cur.fetchone()
        if row:
            credits = row['credits'] or 0
            con.close()
            return int(credits)

        # 尝试从emby_user表获取
        cur.execute("SELECT emby_credits FROM emby_user WHERE tg_id = ?", (telegram_id,))
        row = cur.fetchone()
        con.close()

        if row:
            return int(row['emby_credits'] or 0)

        return 0

    def deduct_pms_credits(
        self,
        telegram_id: int,
        amount: int,
        reason: str = "修仙游戏消费"
    ) -> Tuple[bool, str]:
        """扣除PMS积分

        Args:
            telegram_id: Telegram用户ID
            amount: 扣除数量
            reason: 扣除原因

        Returns:
            (success, message)
        """
        if amount <= 0:
            return False, "扣除数量必须大于0"

        con = self._get_pms_connection()
        cur = con.cursor()

        try:
            # 检查余额
            cur.execute("SELECT credits FROM user WHERE tg_id = ?", (telegram_id,))
            row = cur.fetchone()

            if not row:
                # 尝试emby_user表
                cur.execute("SELECT emby_credits FROM emby_user WHERE tg_id = ?", (telegram_id,))
                row = cur.fetchone()
                if not row:
                    con.close()
                    return False, "用户不存在"

                current_credits = int(row['emby_credits'] or 0)
                if current_credits < amount:
                    con.close()
                    return False, f"积分不足，当前积分：{current_credits}"

                # 扣除emby积分
                new_credits = current_credits - amount
                cur.execute(
                    "UPDATE emby_user SET emby_credits = ? WHERE tg_id = ?",
                    (new_credits, telegram_id)
                )
            else:
                current_credits = int(row['credits'] or 0)
                if current_credits < amount:
                    con.close()
                    return False, f"积分不足，当前积分：{current_credits}"

                # 扣除plex积分
                new_credits = current_credits - amount
                cur.execute(
                    "UPDATE user SET credits = ? WHERE tg_id = ?",
                    (new_credits, telegram_id)
                )

            con.commit()
            con.close()
            return True, f"成功扣除{amount}积分，剩余{new_credits}积分"

        except Exception as e:
            con.rollback()
            con.close()
            return False, f"扣除失败：{str(e)}"

    def add_pms_credits(
        self,
        telegram_id: int,
        amount: int,
        reason: str = "修仙游戏奖励"
    ) -> Tuple[bool, str]:
        """增加PMS积分（用于游戏奖励等）

        Args:
            telegram_id: Telegram用户ID
            amount: 增加数量
            reason: 增加原因

        Returns:
            (success, message)
        """
        if amount <= 0:
            return False, "增加数量必须大于0"

        con = self._get_pms_connection()
        cur = con.cursor()

        try:
            # 尝试更新user表
            cur.execute("SELECT credits FROM user WHERE tg_id = ?", (telegram_id,))
            row = cur.fetchone()

            if row:
                current_credits = int(row['credits'] or 0)
                new_credits = current_credits + amount
                cur.execute(
                    "UPDATE user SET credits = ? WHERE tg_id = ?",
                    (new_credits, telegram_id)
                )
            else:
                # 尝试emby_user表
                cur.execute("SELECT emby_credits FROM emby_user WHERE tg_id = ?", (telegram_id,))
                row = cur.fetchone()
                if not row:
                    con.close()
                    return False, "用户不存在"

                current_credits = int(row['emby_credits'] or 0)
                new_credits = current_credits + amount
                cur.execute(
                    "UPDATE emby_user SET emby_credits = ? WHERE tg_id = ?",
                    (new_credits, telegram_id)
                )

            con.commit()
            con.close()
            return True, f"成功增加{amount}积分，当前{new_credits}积分"

        except Exception as e:
            con.rollback()
            con.close()
            return False, f"增加失败：{str(e)}"

    def exchange_to_spirit_stones(
        self,
        telegram_id: int,
        credits_amount: int,
        exchange_rate: float = 0.1,  # 1积分=0.1灵石，即10积分=1灵石
        xiuxian_db_path: str = None
    ) -> Tuple[bool, str, int]:
        """积分兑换灵石

        Args:
            telegram_id: Telegram用户ID
            credits_amount: 消耗积分数量
            exchange_rate: 兑换比例（1积分兑换多少灵石）
            xiuxian_db_path: 修仙游戏数据库路径

        Returns:
            (success, message, spirit_stones_gained)
        """
        # 检查兑换数量
        if credits_amount < 10:
            return False, "最少需要10积分才能兑换", 0

        # 计算灵石数量
        spirit_stones = int(credits_amount * exchange_rate)
        if spirit_stones < 1:
            return False, "兑换数量太少，至少需要10积分", 0

        # 扣除积分
        success, message = self.deduct_pms_credits(
            telegram_id,
            credits_amount,
            reason=f"兑换修仙灵石×{spirit_stones}"
        )

        if not success:
            return False, message, 0

        # 增加灵石（如果提供了修仙数据库路径）
        if xiuxian_db_path:
            try:
                self._add_spirit_stones_to_xiuxian(
                    telegram_id,
                    spirit_stones,
                    xiuxian_db_path
                )
            except Exception as e:
                # 如果增加灵石失败，回退积分
                self.add_pms_credits(telegram_id, credits_amount, reason="兑换失败回退")
                return False, f"灵石发放失败：{str(e)}", 0

        # 记录兑换历史
        self._record_exchange(telegram_id, credits_amount, spirit_stones, exchange_rate)

        return True, f"兑换成功！消耗{credits_amount}积分，获得{spirit_stones}灵石", spirit_stones

    def _add_spirit_stones_to_xiuxian(
        self,
        telegram_id: int,
        spirit_stones: int,
        xiuxian_db_path: str
    ) -> None:
        """增加修仙游戏灵石

        Args:
            telegram_id: Telegram用户ID
            spirit_stones: 灵石数量
            xiuxian_db_path: 修仙游戏数据库路径
        """
        con = sqlite3.connect(xiuxian_db_path)
        cur = con.cursor()

        try:
            # 检查玩家是否存在
            cur.execute(
                "SELECT spirit_stones FROM xiuxian_players WHERE telegram_id = ?",
                (telegram_id,)
            )
            row = cur.fetchone()

            if row:
                # 更新灵石
                current_stones = row[0] or 0
                new_stones = current_stones + spirit_stones
                cur.execute(
                    "UPDATE xiuxian_players SET spirit_stones = ? WHERE telegram_id = ?",
                    (new_stones, telegram_id)
                )
            else:
                # 创建新玩家（这种情况应该很少发生）
                cur.execute(
                    """
                    INSERT INTO xiuxian_players (telegram_id, spirit_stones)
                    VALUES (?, ?)
                    """,
                    (telegram_id, spirit_stones)
                )

            con.commit()
        except Exception as e:
            con.rollback()
            raise e
        finally:
            con.close()

    def _record_exchange(
        self,
        telegram_id: int,
        credits_amount: int,
        spirit_stones: int,
        exchange_rate: float
    ) -> None:
        """记录兑换历史

        Args:
            telegram_id: Telegram用户ID
            credits_amount: 消耗积分
            spirit_stones: 获得灵石
            exchange_rate: 兑换比例
        """
        con = self._get_pms_connection()
        cur = con.cursor()

        try:
            # 确保表存在
            cur.execute("""
                CREATE TABLE IF NOT EXISTS xiuxian_exchange_records(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    telegram_id INTEGER NOT NULL,
                    credits_amount INTEGER NOT NULL,
                    spirit_stones_gained INTEGER NOT NULL,
                    exchange_rate REAL NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # 插入记录
            cur.execute(
                """
                INSERT INTO xiuxian_exchange_records
                (telegram_id, credits_amount, spirit_stones_gained, exchange_rate)
                VALUES (?, ?, ?, ?)
                """,
                (telegram_id, credits_amount, spirit_stones, exchange_rate)
            )

            con.commit()
        except Exception as e:
            con.rollback()
            print(f"记录兑换历史失败：{e}")
        finally:
            con.close()

    def get_exchange_history(
        self,
        telegram_id: int,
        limit: int = 10
    ) -> list:
        """获取兑换历史

        Args:
            telegram_id: Telegram用户ID
            limit: 返回记录数量

        Returns:
            兑换记录列表
        """
        con = self._get_pms_connection()
        cur = con.cursor()

        try:
            cur.execute(
                """
                SELECT credits_amount, spirit_stones_gained, exchange_rate, created_at
                FROM xiuxian_exchange_records
                WHERE telegram_id = ?
                ORDER BY created_at DESC
                LIMIT ?
                """,
                (telegram_id, limit)
            )

            rows = cur.fetchall()
            return [dict(row) for row in rows]
        finally:
            con.close()

    def get_daily_exchange_total(self, telegram_id: int) -> int:
        """获取今日已兑换积分总数

        Args:
            telegram_id: Telegram用户ID

        Returns:
            今日已兑换积分总数
        """
        con = self._get_pms_connection()
        cur = con.cursor()

        try:
            today = date.today().isoformat()
            cur.execute(
                """
                SELECT SUM(credits_amount) as total
                FROM xiuxian_exchange_records
                WHERE telegram_id = ?
                AND DATE(created_at) = ?
                """,
                (telegram_id, today)
            )

            row = cur.fetchone()
            return int(row['total'] or 0)
        finally:
            con.close()

    def check_daily_limit(
        self,
        telegram_id: int,
        credits_amount: int,
        daily_limit: int = 10000
    ) -> Tuple[bool, str]:
        """检查每日兑换限制

        Args:
            telegram_id: Telegram用户ID
            credits_amount: 本次兑换数量
            daily_limit: 每日限制

        Returns:
            (can_exchange, message)
        """
        today_total = self.get_daily_exchange_total(telegram_id)
        new_total = today_total + credits_amount

        if new_total > daily_limit:
            remaining = daily_limit - today_total
            return False, f"超过每日兑换限制（{daily_limit}积分），今日剩余：{remaining}积分"

        return True, f"可以兑换，今日已用：{today_total}/{daily_limit}积分"


# 使用示例
if __name__ == "__main__":
    # 初始化服务
    bridge = CreditsBridgeService("/path/to/PMSManageBot/data/data.db")

    # 查询积分
    credits = bridge.get_pms_credits(123456789)
    print(f"当前积分：{credits}")

    # 兑换灵石
    success, message, stones = bridge.exchange_to_spirit_stones(
        telegram_id=123456789,
        credits_amount=1000,
        exchange_rate=0.1,
        xiuxian_db_path="/path/to/xiuxian.db"
    )
    print(f"兑换结果：{message}，获得灵石：{stones}")

    # 查看兑换历史
    history = bridge.get_exchange_history(123456789, limit=5)
    for record in history:
        print(f"兑换：{record['credits_amount']}积分 → {record['spirit_stones_gained']}灵石")
