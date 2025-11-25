# 修仙游戏 WebApp 集成指南

## 📋 概述

为 PMSManageBot WebApp 添加修仙游戏面板，用户可以通过网页进行：
- 查看角色状态
- 开始/完成修炼
- 战斗挑战怪物
- 积分兑换灵石
- 查看排行榜

---

## 🎮 功能预览

### 角色面板
- 显示境界、修为、灵石、生命值
- 显示攻击、防御、战力
- 显示悟性、根骨资质
- 每日签到功能

### 修炼系统
- 选择 2/4/8/12 小时修炼
- 实时显示修炼进度
- 倒计时显示剩余时间
- 收取修为
- 境界突破

### 战斗系统
- 怪物列表展示
- BOSS 特殊标记
- 显示怪物属性和奖励
- 战斗冷却提示

### 兑换系统
- 积分兑换灵石
- 快捷金额按钮
- 实时显示兑换比例

### 排行榜
- 战力排行榜
- 境界排行榜
- 前三名特殊标记

---

## 🚀 集成步骤

### 步骤1: 添加后端 API 路由

将 `webapp_xiuxian_router.py` 复制到服务器：

```bash
# 上传文件
scp /Users/zc/EC-AI/xiuxian-game/integration/webapp_xiuxian_router.py user@server:/tmp/

# SSH 登录服务器
ssh user@server
cd /path/to/PMSManageBot

# 复制到路由目录
cp /tmp/webapp_xiuxian_router.py src/app/webapp/routers/xiuxian.py
```

### 步骤2: 注册路由到主应用

编辑 `src/app/webapp/__init__.py`：

```python
# 添加导入
from app.webapp.routers import xiuxian

# 在 create_app() 函数中注册路由
def create_app():
    app = FastAPI(...)

    # ... 其他路由 ...

    # 注册修仙路由
    app.include_router(xiuxian.router)

    return app
```

### 步骤3: 添加前端 Vue 组件

将 `webapp_Xiuxian.vue` 复制到服务器：

```bash
scp /Users/zc/EC-AI/xiuxian-game/integration/webapp_Xiuxian.vue user@server:/tmp/

# 在服务器上
cd /path/to/PMSManageBot
cp /tmp/webapp_Xiuxian.vue webapp-frontend/src/views/Xiuxian.vue
```

### 步骤4: 添加路由配置

编辑 `webapp-frontend/src/router/index.js`：

```javascript
// 添加导入
import Xiuxian from '../views/Xiuxian.vue'

const routes = [
  // ... 现有路由 ...
  {
    path: '/xiuxian',
    name: 'xiuxian',
    component: Xiuxian
  }
]
```

### 步骤5: 添加底部导航菜单

编辑 `webapp-frontend/src/components/BottomMenu.vue`：

```vue
<template>
  <v-bottom-navigation v-model="value" grow>
    <!-- 现有菜单项 -->
    <v-btn value="user-info" to="/user-info">
      <v-icon>mdi-account</v-icon>
      <span>个人</span>
    </v-btn>

    <v-btn value="activities" to="/activities">
      <v-icon>mdi-star</v-icon>
      <span>活动</span>
    </v-btn>

    <!-- 新增：修仙菜单 -->
    <v-btn value="xiuxian" to="/xiuxian">
      <v-icon>mdi-meditation</v-icon>
      <span>修仙</span>
    </v-btn>

    <v-btn value="rankings" to="/rankings">
      <v-icon>mdi-trophy</v-icon>
      <span>排行</span>
    </v-btn>

    <v-btn value="management" to="/management">
      <v-icon>mdi-cog</v-icon>
      <span>管理</span>
    </v-btn>
  </v-bottom-navigation>
</template>
```

### 步骤6: 重新构建前端

```bash
cd webapp-frontend

# 安装依赖（如果需要）
npm install

# 构建生产版本
npm run build

# 复制构建文件到后端静态目录
cp -r dist/* ../static/
```

### 步骤7: 重启服务

```bash
# 重启后端
sudo systemctl restart pmsmanagebot

# 或使用 Docker
docker-compose restart webapp
```

---

## 📂 文件结构

集成后的文件结构：

```
PMSManageBot/
├── src/app/webapp/
│   ├── routers/
│   │   ├── xiuxian.py          # 新增：修仙 API 路由
│   │   ├── user.py
│   │   └── ...
│   └── __init__.py              # 已修改：注册修仙路由
│
└── webapp-frontend/
    ├── src/
    │   ├── views/
    │   │   ├── Xiuxian.vue      # 新增：修仙游戏面板
    │   │   ├── UserInfo.vue
    │   │   └── ...
    │   ├── components/
    │   │   └── BottomMenu.vue   # 已修改：添加修仙菜单
    │   └── router/
    │       └── index.js         # 已修改：添加修仙路由
    └── ...
```

---

## 🔌 API 端点说明

### 玩家相关

#### `GET /api/xiuxian/player/info`
获取玩家信息

**响应**:
```json
{
  "id": 1,
  "telegram_id": 123456789,
  "name": "道友",
  "realm": "练气",
  "realm_level": 5,
  "cultivation_exp": 3500,
  "spirit_stones": 2000,
  "hp": 100,
  "max_hp": 100,
  "attack": 10,
  "defense": 10,
  "comprehension": 12,
  "root_bone": 14,
  "is_cultivating": false
}
```

#### `POST /api/xiuxian/player/create`
创建玩家

### 修炼相关

#### `POST /api/xiuxian/cultivate/start?hours=4`
开始修炼

**参数**:
- `hours`: 修炼时长 (2/4/8/12)

#### `POST /api/xiuxian/cultivate/finish`
完成修炼

**响应**:
```json
{
  "message": "修炼完成",
  "exp_gained": 1200,
  "total_exp": 4700,
  "event": "顿悟"
}
```

### 突破相关

#### `POST /api/xiuxian/breakthrough`
境界突破

**响应**:
```json
{
  "success": true,
  "message": "突破成功！练气5层 → 练气6层",
  "new_realm": "练气",
  "new_level": 6
}
```

### 战斗相关

#### `GET /api/xiuxian/monsters`
获取怪物列表

#### `POST /api/xiuxian/battle/{monster_id}`
战斗

**响应**:
```json
{
  "success": true,
  "message": "战胜 野狼",
  "exp_gained": 100,
  "stones_gained": 50
}
```

### 签到相关

#### `POST /api/xiuxian/sign`
每日签到

### 兑换相关

#### `POST /api/xiuxian/exchange?credits_amount=1000`
积分兑换灵石

**参数**:
- `credits_amount`: 兑换积分数量

### 排行榜相关

#### `GET /api/xiuxian/rankings/power`
战力排行榜

#### `GET /api/xiuxian/rankings/realm`
境界排行榜

---

## 🎨 UI 设计说明

### 顶部标签导航
- 角色面板
- 修炼
- 历练
- 兑换
- 排行榜

### 颜色方案
- 主色调: Primary (蓝色)
- 成功: Success (绿色) - 用于灵石
- 警告: Warning (橙色) - 用于战力
- 错误: Error (红色) - 用于 BOSS
- 信息: Info (蓝色) - 用于提示

### 响应式设计
- 桌面端: 3列卡片布局
- 平板: 2列卡片布局
- 手机: 1列卡片布局

---

## 🔧 配置调整

### 修改 API 基础路径

如果您的 API 不在 `/api` 路径下，编辑 `Xiuxian.vue`：

```javascript
// 在 methods 中的 axios 调用修改路径
axios.get('/your-api-path/xiuxian/player/info')
```

或者使用 axios 全局配置：

```javascript
// main.js
import axios from 'axios'
axios.defaults.baseURL = '/your-api-path'
```

### 自定义主题色

编辑 `webapp-frontend/src/plugins/vuetify.js`：

```javascript
export default new Vuetify({
  theme: {
    themes: {
      light: {
        primary: '#1976D2',  // 修改主色调
        success: '#4CAF50',
        warning: '#FF9800',
        error: '#F44336',
      },
    },
  },
})
```

---

## ✅ 测试验证

### 1. 测试后端 API

```bash
# 获取玩家信息
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://your-server/api/xiuxian/player/info

# 创建角色
curl -X POST -H "Authorization: Bearer YOUR_TOKEN" \
  http://your-server/api/xiuxian/player/create

# 获取怪物列表
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://your-server/api/xiuxian/monsters
```

### 2. 测试前端界面

1. 访问 `http://your-server/xiuxian`
2. 检查底部导航是否显示"修仙"按钮
3. 点击进入修仙面板
4. 测试各个功能标签页

### 3. 功能测试清单

- [ ] 角色面板正常显示
- [ ] 每日签到功能正常
- [ ] 开始修炼功能正常
- [ ] 修炼倒计时正确
- [ ] 收取修为功能正常
- [ ] 境界突破功能正常
- [ ] 怪物列表正常显示
- [ ] 战斗功能正常
- [ ] 战斗冷却正常
- [ ] 积分兑换功能正常
- [ ] 排行榜正常显示

---

## 🐛 故障排除

### 问题1: API 404 错误

**症状**: 前端调用 API 返回 404

**解决**:
```bash
# 检查路由是否注册
grep "xiuxian" src/app/webapp/__init__.py

# 检查文件是否存在
ls src/app/webapp/routers/xiuxian.py

# 重启服务
sudo systemctl restart pmsmanagebot
```

### 问题2: 前端页面空白

**症状**: 访问 /xiuxian 页面空白

**解决**:
- 检查浏览器控制台错误
- 确认 `Xiuxian.vue` 文件已复制
- 确认路由已正确配置
- 重新构建前端: `npm run build`

### 问题3: 修炼倒计时不更新

**症状**: 修炼进度条不动

**解决**:
- 检查 `cultivation_start_time` 格式
- 确认定时器正常启动
- 检查浏览器控制台错误

### 问题4: 认证失败

**症状**: API 返回 401 Unauthorized

**解决**:
- 确认已登录 WebApp
- 检查 Token 是否过期
- 确认 `get_current_user` 依赖正常

---

## 📈 性能优化建议

### 1. 前端优化

- 使用 Vue 组件懒加载
- 添加 loading 状态提示
- 实现数据缓存机制

### 2. 后端优化

- 添加 Redis 缓存排行榜
- 数据库查询优化（添加索引）
- API 响应数据压缩

### 3. 数据库优化

```sql
-- 添加索引
CREATE INDEX idx_players_telegram_id ON xiuxian_players(telegram_id);
CREATE INDEX idx_exchange_date ON xiuxian_exchange_records(telegram_id, created_at);
CREATE INDEX idx_battle_time ON xiuxian_players(last_battle_time);
```

---

## 🎉 完成！

集成完成后，用户可以：
- ✨ 在网页上查看修仙角色状态
- 🧘 通过网页开始修炼和突破
- ⚔️ 在网页上挑战怪物
- 💎 网页兑换积分到灵石
- 🏆 查看实时排行榜

**与 Telegram Bot 完全同步！** 🔄

---

## 📝 附加说明

### Telegram Bot vs WebApp

| 功能 | Telegram Bot | WebApp |
|------|--------------|--------|
| 创建角色 | ✅ | ✅ |
| 查看状态 | ✅ | ✅ |
| 修炼系统 | ✅ | ✅ |
| 战斗系统 | ✅ | ✅ |
| 签到系统 | ✅ | ✅ |
| 积分兑换 | ✅ | ✅ |
| 排行榜 | ❌ | ✅ |
| 实时倒计时 | ❌ | ✅ |
| 可视化面板 | ❌ | ✅ |

### 数据同步

所有数据存储在同一数据库中，Telegram Bot 和 WebApp 数据完全同步：
- 在 Telegram 修炼，WebApp 可以看到进度
- 在 WebApp 兑换灵石，Telegram 可以使用
- 战斗记录、排行榜实时更新

---

**祝您修仙愉快！** ✨
