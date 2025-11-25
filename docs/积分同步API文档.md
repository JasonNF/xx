# 积分同步API文档

## 概述

本API提供跨项目积分同步功能，支持多个项目间的积分打通和统一管理。

**版本**: v1.0
**基础URL**: `http://your-domain.com/api/credits`

---

## 认证方式

所有API请求需要在HTTP Header中提供API密钥：

```
X-Api-Key: your-api-key-here
```

**有效的API密钥**：
- `xiuxian-api-key-2024` - 修仙游戏项目
- `media-bot-api-key-2024` - 媒体机器人项目

---

## 安全机制

### 1. 令牌验证
每次同步请求需要携带验证令牌，令牌生成算法：

```python
import hmac
import hashlib

message = f"{telegram_id}:{amount}:{source}:{timestamp}"
token = hmac.new(
    SECRET_KEY.encode(),
    message.encode(),
    hashlib.sha256
).hexdigest()
```

### 2. 时间戳验证
- 请求时间戳与服务器时间差不超过5分钟
- 防止重放攻击

### 3. 去重机制
- 通过 `external_reference` 字段防止重复同步
- 相同引用ID的请求只会处理一次

---

## API端点

### 1. 同步积分（单笔）

**端点**: `POST /api/credits/sync`

**描述**: 单笔积分同步，支持增加或扣除。

**请求体**:
```json
{
  "telegram_id": 123456789,
  "amount": 100,
  "source": "media_bot",
  "reason": "观看视频奖励",
  "external_reference": "video_12345",
  "timestamp": 1234567890,
  "token": "abc123def456..."
}
```

**字段说明**:
| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| telegram_id | int | 是 | Telegram用户ID |
| amount | int | 是 | 积分数量（正数增加，负数扣除） |
| source | string | 是 | 来源项目（xiuxian_game, media_bot, external_api, admin） |
| reason | string | 是 | 变动原因 |
| external_reference | string | 否 | 外部引用ID（用于去重） |
| timestamp | int | 是 | 请求时间戳（Unix时间） |
| token | string | 是 | 验证令牌 |

**响应示例**:
```json
{
  "success": true,
  "message": "同步成功：增加 100 积分",
  "data": {
    "balance": 1500
  }
}
```

**错误响应**:
```json
{
  "success": false,
  "message": "同步验证失败：无效的令牌",
  "data": null
}
```

---

### 2. 批量同步积分

**端点**: `POST /api/credits/sync/batch`

**描述**: 批量同步多个用户的积分。

**请求体**:
```json
{
  "source": "media_bot",
  "items": [
    {
      "telegram_id": 123456789,
      "amount": 50,
      "reason": "每日任务完成",
      "external_reference": "task_001"
    },
    {
      "telegram_id": 987654321,
      "amount": 100,
      "reason": "活动奖励",
      "external_reference": "event_002"
    }
  ],
  "timestamp": 1234567890,
  "token": "batch_token_here"
}
```

**响应示例**:
```json
{
  "success": true,
  "message": "处理完成：成功 2，失败 0",
  "data": {
    "total": 2,
    "success": 2,
    "failed": 0,
    "details": [
      {
        "telegram_id": 123456789,
        "success": true,
        "message": "同步成功：增加 50 积分",
        "balance": 1050
      },
      {
        "telegram_id": 987654321,
        "success": true,
        "message": "同步成功：增加 100 积分",
        "balance": 2100
      }
    ]
  }
}
```

---

### 3. 查询积分余额

**端点**: `GET /api/credits/balance/{telegram_id}`

**描述**: 查询指定用户的当前积分余额。

**参数**:
- `telegram_id` (路径参数): Telegram用户ID

**响应示例**:
```json
{
  "telegram_id": 123456789,
  "credits": 1500,
  "nickname": "逍遥散人",
  "sync_time": "2024-01-20T15:30:00"
}
```

---

### 4. 查询积分记录

**端点**: `GET /api/credits/records/{telegram_id}?limit=20`

**描述**: 查询指定用户的积分变动记录。

**参数**:
- `telegram_id` (路径参数): Telegram用户ID
- `limit` (查询参数，可选): 返回记录数量，默认20

**响应示例**:
```json
{
  "telegram_id": 123456789,
  "credits": 1500,
  "records": [
    {
      "id": 1001,
      "change": 100,
      "type": "活动奖励",
      "reason": "[media_bot] 观看视频奖励 [REF:video_12345]",
      "created_at": "2024-01-20T15:30:00"
    },
    {
      "id": 1000,
      "change": -50,
      "type": "商城兑换",
      "reason": "[xiuxian_game] 兑换：回春丹",
      "created_at": "2024-01-20T14:20:00"
    }
  ]
}
```

---

### 5. 生成同步令牌

**端点**: `POST /api/credits/token/generate`

**描述**: 生成用于同步的验证令牌。

**请求参数**:
```json
{
  "telegram_id": 123456789,
  "amount": 100,
  "source": "media_bot"
}
```

**响应示例**:
```json
{
  "success": true,
  "message": "令牌生成成功",
  "data": {
    "telegram_id": 123456789,
    "amount": 100,
    "source": "media_bot",
    "reason": "令牌生成",
    "external_reference": null,
    "timestamp": 1234567890,
    "token": "abc123def456..."
  }
}
```

---

### 6. Webhook回调

**端点**: `POST /api/credits/webhook`

**描述**: 接收其他项目的异步通知。

**请求体**:
```json
{
  "event": "credit_earned",
  "telegram_id": 123456789,
  "amount": 50,
  "source": "media_bot",
  "reason": "完成每日任务",
  "timestamp": 1234567890,
  "signature": "webhook_signature_here"
}
```

**支持的事件类型**:
- `credit_earned`: 积分获得
- `credit_spent`: 积分消耗

---

## 使用示例

### Python示例

```python
import requests
import time
import hmac
import hashlib

# 配置
API_BASE_URL = "http://your-domain.com/api/credits"
API_KEY = "media-bot-api-key-2024"
SECRET_KEY = "your-secret-key-here"

# 生成令牌
def generate_token(telegram_id, amount, source, timestamp):
    message = f"{telegram_id}:{amount}:{source}:{timestamp}"
    return hmac.new(
        SECRET_KEY.encode(),
        message.encode(),
        hashlib.sha256
    ).hexdigest()

# 同步积分
def sync_credits(telegram_id, amount, reason, reference=None):
    timestamp = int(time.time())
    token = generate_token(telegram_id, amount, "media_bot", timestamp)

    headers = {
        "X-Api-Key": API_KEY,
        "Content-Type": "application/json"
    }

    data = {
        "telegram_id": telegram_id,
        "amount": amount,
        "source": "media_bot",
        "reason": reason,
        "external_reference": reference,
        "timestamp": timestamp,
        "token": token
    }

    response = requests.post(
        f"{API_BASE_URL}/sync",
        json=data,
        headers=headers
    )

    return response.json()

# 查询余额
def get_balance(telegram_id):
    headers = {"X-Api-Key": API_KEY}

    response = requests.get(
        f"{API_BASE_URL}/balance/{telegram_id}",
        headers=headers
    )

    return response.json()

# 使用示例
if __name__ == "__main__":
    # 同步积分
    result = sync_credits(
        telegram_id=123456789,
        amount=100,
        reason="观看视频奖励",
        reference="video_12345"
    )
    print(f"同步结果: {result}")

    # 查询余额
    balance = get_balance(123456789)
    print(f"当前余额: {balance['credits']}")
```

---

### JavaScript示例

```javascript
const crypto = require('crypto');
const axios = require('axios');

const API_BASE_URL = 'http://your-domain.com/api/credits';
const API_KEY = 'media-bot-api-key-2024';
const SECRET_KEY = 'your-secret-key-here';

// 生成令牌
function generateToken(telegramId, amount, source, timestamp) {
  const message = `${telegramId}:${amount}:${source}:${timestamp}`;
  return crypto
    .createHmac('sha256', SECRET_KEY)
    .update(message)
    .digest('hex');
}

// 同步积分
async function syncCredits(telegramId, amount, reason, reference = null) {
  const timestamp = Math.floor(Date.now() / 1000);
  const token = generateToken(telegramId, amount, 'media_bot', timestamp);

  const response = await axios.post(
    `${API_BASE_URL}/sync`,
    {
      telegram_id: telegramId,
      amount: amount,
      source: 'media_bot',
      reason: reason,
      external_reference: reference,
      timestamp: timestamp,
      token: token
    },
    {
      headers: {
        'X-Api-Key': API_KEY,
        'Content-Type': 'application/json'
      }
    }
  );

  return response.data;
}

// 查询余额
async function getBalance(telegramId) {
  const response = await axios.get(
    `${API_BASE_URL}/balance/${telegramId}`,
    {
      headers: { 'X-Api-Key': API_KEY }
    }
  );

  return response.data;
}

// 使用示例
(async () => {
  try {
    // 同步积分
    const result = await syncCredits(
      123456789,
      100,
      '观看视频奖励',
      'video_12345'
    );
    console.log('同步结果:', result);

    // 查询余额
    const balance = await getBalance(123456789);
    console.log('当前余额:', balance.credits);
  } catch (error) {
    console.error('错误:', error.response?.data || error.message);
  }
})();
```

---

## 错误码

| HTTP状态码 | 说明 |
|-----------|------|
| 200 | 成功 |
| 400 | 请求参数错误 |
| 401 | 未授权（API密钥无效或令牌验证失败） |
| 404 | 用户不存在 |
| 500 | 服务器内部错误 |

---

## 常见问题

### Q1: 如何防止重复同步？
A: 使用 `external_reference` 字段，相同引用ID的请求只会处理一次。

### Q2: 令牌有效期是多久？
A: 令牌有效期为5分钟，超时后需要重新生成。

### Q3: 可以扣除用户积分吗？
A: 可以，将 `amount` 设置为负数即可。但需确保用户积分充足。

### Q4: 批量同步有数量限制吗？
A: 建议每次批量同步不超过100个用户，避免请求超时。

### Q5: 如何获取API密钥？
A: 联系系统管理员申请API密钥。

---

## 更新日志

### v1.0.0 (2024-01-XX)
- ✅ 初始版本发布
- ✅ 支持单笔和批量同步
- ✅ 提供余额和记录查询
- ✅ 实现令牌验证机制
- ✅ 支持Webhook回调

---

**文档版本**: v1.0.0
**最后更新**: 2024-01-XX
**维护者**: 开发团队
