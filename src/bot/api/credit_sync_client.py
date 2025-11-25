"""积分同步客户端SDK

供其他项目使用的Python客户端，简化API调用。

使用示例：
    from credit_sync_client import CreditSyncClient

    client = CreditSyncClient(
        base_url="http://your-domain.com",
        api_key="your-api-key",
        secret_key="your-secret-key",
        source="media_bot"
    )

    # 增加积分
    result = client.add_credits(
        telegram_id=123456789,
        amount=100,
        reason="观看视频",
        reference="video_001"
    )

    # 查询余额
    balance = client.get_balance(123456789)
"""
import time
import hmac
import hashlib
from typing import Optional, List, Dict, Any
from dataclasses import dataclass

try:
    import requests
except ImportError:
    raise ImportError("Please install requests: pip install requests")


@dataclass
class SyncResult:
    """同步结果"""
    success: bool
    message: str
    balance: Optional[int] = None
    data: Optional[Dict[str, Any]] = None


class CreditSyncClient:
    """积分同步客户端"""

    def __init__(
        self,
        base_url: str,
        api_key: str,
        secret_key: str,
        source: str = "external_api",
        timeout: int = 30
    ):
        """初始化客户端

        Args:
            base_url: API基础URL
            api_key: API密钥
            secret_key: 用于生成令牌的密钥
            source: 来源项目标识
            timeout: 请求超时时间（秒）
        """
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.secret_key = secret_key
        self.source = source
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            'X-Api-Key': self.api_key,
            'Content-Type': 'application/json'
        })

    def _generate_token(
        self,
        telegram_id: int,
        amount: int,
        timestamp: int
    ) -> str:
        """生成验证令牌"""
        message = f"{telegram_id}:{amount}:{self.source}:{timestamp}"
        return hmac.new(
            self.secret_key.encode(),
            message.encode(),
            hashlib.sha256
        ).hexdigest()

    def _handle_response(self, response: requests.Response) -> SyncResult:
        """处理API响应"""
        try:
            data = response.json()
        except Exception:
            return SyncResult(
                success=False,
                message=f"Invalid response: {response.text}"
            )

        if response.status_code == 200:
            return SyncResult(
                success=data.get('success', False),
                message=data.get('message', ''),
                balance=data.get('data', {}).get('balance'),
                data=data.get('data')
            )
        else:
            return SyncResult(
                success=False,
                message=data.get('detail', f"HTTP {response.status_code}")
            )

    def add_credits(
        self,
        telegram_id: int,
        amount: int,
        reason: str,
        reference: Optional[str] = None
    ) -> SyncResult:
        """增加积分

        Args:
            telegram_id: Telegram用户ID
            amount: 积分数量（正数）
            reason: 原因说明
            reference: 外部引用ID（用于去重）

        Returns:
            同步结果
        """
        if amount <= 0:
            return SyncResult(
                success=False,
                message="积分数量必须大于0"
            )

        timestamp = int(time.time())
        token = self._generate_token(telegram_id, amount, timestamp)

        data = {
            "telegram_id": telegram_id,
            "amount": amount,
            "source": self.source,
            "reason": reason,
            "external_reference": reference,
            "timestamp": timestamp,
            "token": token
        }

        try:
            response = self.session.post(
                f"{self.base_url}/api/credits/sync",
                json=data,
                timeout=self.timeout
            )
            return self._handle_response(response)
        except requests.RequestException as e:
            return SyncResult(
                success=False,
                message=f"请求失败: {str(e)}"
            )

    def deduct_credits(
        self,
        telegram_id: int,
        amount: int,
        reason: str,
        reference: Optional[str] = None
    ) -> SyncResult:
        """扣除积分

        Args:
            telegram_id: Telegram用户ID
            amount: 积分数量（正数）
            reason: 原因说明
            reference: 外部引用ID（用于去重）

        Returns:
            同步结果
        """
        if amount <= 0:
            return SyncResult(
                success=False,
                message="积分数量必须大于0"
            )

        timestamp = int(time.time())
        token = self._generate_token(telegram_id, -amount, timestamp)

        data = {
            "telegram_id": telegram_id,
            "amount": -amount,  # 负数表示扣除
            "source": self.source,
            "reason": reason,
            "external_reference": reference,
            "timestamp": timestamp,
            "token": token
        }

        try:
            response = self.session.post(
                f"{self.base_url}/api/credits/sync",
                json=data,
                timeout=self.timeout
            )
            return self._handle_response(response)
        except requests.RequestException as e:
            return SyncResult(
                success=False,
                message=f"请求失败: {str(e)}"
            )

    def batch_sync(
        self,
        items: List[Dict[str, Any]]
    ) -> SyncResult:
        """批量同步积分

        Args:
            items: 同步项列表，每项包含：
                - telegram_id: int
                - amount: int
                - reason: str
                - external_reference: Optional[str]

        Returns:
            批量处理结果
        """
        timestamp = int(time.time())

        # 生成批量令牌（使用第一个用户的信息）
        if items:
            first_item = items[0]
            token = self._generate_token(
                first_item['telegram_id'],
                first_item['amount'],
                timestamp
            )
        else:
            return SyncResult(
                success=False,
                message="批量同步项列表不能为空"
            )

        data = {
            "source": self.source,
            "items": items,
            "timestamp": timestamp,
            "token": token
        }

        try:
            response = self.session.post(
                f"{self.base_url}/api/credits/sync/batch",
                json=data,
                timeout=self.timeout
            )
            return self._handle_response(response)
        except requests.RequestException as e:
            return SyncResult(
                success=False,
                message=f"请求失败: {str(e)}"
            )

    def get_balance(self, telegram_id: int) -> Optional[Dict[str, Any]]:
        """查询积分余额

        Args:
            telegram_id: Telegram用户ID

        Returns:
            余额信息，失败返回None
        """
        try:
            response = self.session.get(
                f"{self.base_url}/api/credits/balance/{telegram_id}",
                timeout=self.timeout
            )

            if response.status_code == 200:
                return response.json()
            else:
                return None
        except requests.RequestException:
            return None

    def get_records(
        self,
        telegram_id: int,
        limit: int = 20
    ) -> Optional[Dict[str, Any]]:
        """查询积分记录

        Args:
            telegram_id: Telegram用户ID
            limit: 返回记录数量

        Returns:
            记录信息，失败返回None
        """
        try:
            response = self.session.get(
                f"{self.base_url}/api/credits/records/{telegram_id}",
                params={"limit": limit},
                timeout=self.timeout
            )

            if response.status_code == 200:
                return response.json()
            else:
                return None
        except requests.RequestException:
            return None

    def close(self):
        """关闭客户端会话"""
        self.session.close()

    def __enter__(self):
        """上下文管理器入口"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.close()


# 便捷函数
def create_client(
    base_url: str,
    api_key: str,
    secret_key: str,
    source: str = "external_api"
) -> CreditSyncClient:
    """创建客户端实例

    Args:
        base_url: API基础URL
        api_key: API密钥
        secret_key: 令牌密钥
        source: 来源标识

    Returns:
        客户端实例
    """
    return CreditSyncClient(
        base_url=base_url,
        api_key=api_key,
        secret_key=secret_key,
        source=source
    )


# 使用示例
if __name__ == "__main__":
    # 创建客户端
    client = CreditSyncClient(
        base_url="http://localhost:8000",
        api_key="media-bot-api-key-2024",
        secret_key="your-secret-key-here",
        source="media_bot"
    )

    # 示例1：增加积分
    print("=== 增加积分 ===")
    result = client.add_credits(
        telegram_id=123456789,
        amount=100,
        reason="观看视频奖励",
        reference="video_12345"
    )
    print(f"结果: {result.success}")
    print(f"消息: {result.message}")
    print(f"余额: {result.balance}")

    # 示例2：查询余额
    print("\n=== 查询余额 ===")
    balance = client.get_balance(123456789)
    if balance:
        print(f"用户: {balance['nickname']}")
        print(f"积分: {balance['credits']}")
    else:
        print("查询失败")

    # 示例3：查询记录
    print("\n=== 查询记录 ===")
    records = client.get_records(123456789, limit=5)
    if records:
        print(f"当前积分: {records['credits']}")
        print("最近记录:")
        for record in records['records']:
            print(f"  {record['change']:+d} - {record['reason']}")
    else:
        print("查询失败")

    # 示例4：批量同步
    print("\n=== 批量同步 ===")
    batch_items = [
        {
            "telegram_id": 123456789,
            "amount": 50,
            "reason": "每日任务",
            "external_reference": "daily_task_001"
        },
        {
            "telegram_id": 987654321,
            "amount": 100,
            "reason": "活动奖励",
            "external_reference": "event_002"
        }
    ]
    batch_result = client.batch_sync(batch_items)
    print(f"结果: {batch_result.success}")
    print(f"消息: {batch_result.message}")
    if batch_result.data:
        print(f"成功: {batch_result.data['success']}")
        print(f"失败: {batch_result.data['failed']}")

    # 关闭客户端
    client.close()

    # 或使用上下文管理器
    print("\n=== 使用上下文管理器 ===")
    with create_client(
        base_url="http://localhost:8000",
        api_key="media-bot-api-key-2024",
        secret_key="your-secret-key-here",
        source="media_bot"
    ) as client:
        result = client.add_credits(
            telegram_id=123456789,
            amount=50,
            reason="测试"
        )
        print(f"结果: {result.success}")
