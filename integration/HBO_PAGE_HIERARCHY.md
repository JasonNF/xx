# PMSManageBot 完整页面层级结构分析

## 📊 页面层级总览

```
PMSManageBot WebApp
├── 🏠 主页 (Home) - 新增一级页面
│   ├── Hero Banner
│   ├── 快速操作卡片
│   ├── 数据概览卡片
│   └── 继续游戏区域
│
├── 👤 我的 (Profile) - 整合原 UserInfo 页面
│   ├── 个人信息卡片
│   ├── 账户信息
│   ├── **快捷操作区** (整合原扇形菜单4功能)
│   │   ├── 🎫 兑换邀请码 → Dialog
│   │   ├── 🎟️  生成邀请码 → Dialog
│   │   ├── 🔗 绑定账户 → Dialog
│   │   └── 🛣️  绑定线路 → Dialog
│   ├── 服务管理 (Emby/Plex)
│   │   ├── Emby 服务卡片
│   │   │   ├── 绑定状态
│   │   │   ├── 当前线路
│   │   │   ├── EmbyLineSelector → Dialog (二级)
│   │   │   └── 解绑功能
│   │   └── Plex 服务卡片
│   │       ├── 绑定状态
│   │       ├── PlexLineSelector → Dialog (二级)
│   │       └── 解绑功能
│   ├── Premium 功能
│   │   ├── PremiumUnlockDialog → Dialog (二级)
│   │   └── 流量统计
│   ├── 我的邀请
│   │   └── InviteCodeDialog → Dialog (二级)
│   └── 捐赠支持
│       └── DonationDialog → Dialog (二级)
│
├── 🎮 娱乐 (Entertainment) - 整合原 Activities 页面
│   ├── Tab 导航:
│   │   ├── [修仙世界] Tab
│   │   │   ├── Xiuxian Game 主界面
│   │   │   │   ├── 角色状态卡片
│   │   │   │   ├── 修炼系统
│   │   │   │   ├── 战斗系统
│   │   │   │   ├── 兑换系统
│   │   │   │   └── 排行榜
│   │   │   └── 修仙详细页面 (可能的三级页面)
│   │   │
│   │   ├── [互动游戏] Tab
│   │   │   ├── 🎡 幸运大转盘
│   │   │   │   └── LuckyWheel → Dialog (二级)
│   │   │   │       └── WheelAdminPanel (管理员)
│   │   │   ├── 🃏 21点游戏
│   │   │   │   └── Blackjack → Dialog (二级)
│   │   │   │       └── BlackjackAdminPanel (管理员)
│   │   │   └── ⚽ 赛事竞猜
│   │   │       └── MatchPredictionGame → Fullscreen Dialog (二级)
│   │   │           └── MatchPredictionAdminPanel (管理员)
│   │   │
│   │   └── [竞拍活动] Tab
│   │       ├── 竞拍列表卡片
│   │       ├── 竞拍详情 → Dialog (二级)
│   │       ├── 出价弹窗 → Dialog (三级)
│   │       └── AuctionAdminPanel (管理员)
│   │
│   └── 活动状态 Snackbar
│
├── 🏆 排行 (Rankings) - 优化原 Rankings 页面
│   ├── Tab 导航:
│   │   ├── [积分榜] Tab
│   │   │   └── 积分排行列表
│   │   ├── [捐赠榜] Tab
│   │   │   └── 捐赠排行列表
│   │   ├── [观看时长榜] Tab
│   │   │   ├── Emby/Plex 数据源切换
│   │   │   ├── 观看时长排行列表
│   │   │   └── 等级说明 Dialog (二级)
│   │   ├── [流量榜] Tab
│   │   │   └── 流量排行列表
│   │   └── [更多] 下拉菜单
│   │       ├── 战力榜 (修仙)
│   │       └── 境界榜 (修仙)
│   │
│   └── 刷新按钮
│
└── ⚙️ 设置 (Settings) - 整合原 Management 页面 (仅管理员)
    ├── Tab 导航:
    │   ├── [概览] Tab
    │   │   └── 系统统计数据卡片
    │   │
    │   ├── [系统设置项] Tab
    │   │   ├── 服务注册控制
    │   │   │   ├── Plex 注册开关
    │   │   │   └── Emby 注册开关
    │   │   ├── 高级线路控制
    │   │   │   ├── Premium 开关
    │   │   │   ├── Premium 解锁开关
    │   │   │   └── 免费高级线路选择
    │   │   └── 系统管理
    │   │       ├── 捐赠管理 → DonationDialog (二级)
    │   │       ├── 邀请码管理 → AdminInviteCodeDialog (二级)
    │   │       ├── 标签管理 → TagManagementDialog (二级)
    │   │       ├── 线路管理 → LineManagementDialog (二级)
    │   │       ├── 流量统计 → LineTrafficStatsPanel (二级)
    │   │       ├── 切换历史 → LineSwitchHistoryDialog (二级)
    │   │       ├── TG换绑 → TgBindingDialog (二级)
    │   │       ├── 特权用户 → PrivilegedUserDialog (二级)
    │   │       ├── 积分转移 → CreditsTransferDialog (二级)
    │   │       └── NSFW管理 → NsfwDialog (二级)
    │   │
    │   ├── [活动管理] Tab
    │   │   ├── WheelAdminPanel (幸运转盘配置)
    │   │   │   ├── 奖品编辑
    │   │   │   └── RandomnessConfigDialog (三级)
    │   │   ├── AuctionAdminPanel (竞拍活动配置)
    │   │   ├── BlackjackAdminPanel (21点配置)
    │   │   └── MatchPredictionAdminPanel (赛事竞猜配置)
    │   │
    │   └── [主题配置] Tab
    │       └── ThemeConfigPanel
    │           ├── 主题色选择
    │           ├── 强调色选择
    │           └── 背景色选择
    │
    └── 权限检查提示
```

---

## 📁 文件映射表

### 一级页面 (Views)

| 新架构名称 | 组件名称 | 文件路径 | 说明 |
|-----------|---------|---------|------|
| 🏠 主页 | `Home.vue` | `src/views/Home.vue` | **新建** - Dashboard 概览页 |
| 👤 我的 | `UserInfo.vue` | `src/views/UserInfo.vue` | **优化** - 整合快捷操作 |
| 🎮 娱乐 | `Activities.vue` | `src/views/Activities.vue` | **优化** - 添加修仙Tab |
| 🏆 排行 | `Rankings.vue` | `src/views/Rankings.vue` | **优化** - 添加修仙榜 |
| ⚙️ 设置 | `Management.vue` | `src/views/Management.vue` | **重命名** - Settings.vue |

### 二级页面/对话框 (Components - Dialogs)

| 类别 | 组件名称 | 文件路径 | 触发位置 | 用途 |
|------|---------|---------|---------|------|
| **快捷操作** | `RedeemCodeDialog.vue` | `src/components/RedeemCodeDialog.vue` | 我的 → 快捷操作 | 兑换邀请码 |
| **快捷操作** | `InviteCodeDialog.vue` | `src/components/InviteCodeDialog.vue` | 我的 → 快捷操作 | 生成邀请码 |
| **快捷操作** | `BindAccountDialog.vue` | `src/components/BindAccountDialog.vue` | 我的 → 快捷操作 | 绑定媒体账户 |
| **快捷操作** | `BindLineDialog.vue` | `src/components/BindLineDialog.vue` | 我的 → 快捷操作 | 绑定线路 |
| **服务管理** | `EmbyLineSelector.vue` | `src/components/EmbyLineSelector.vue` | 我的 → Emby服务 | Emby线路选择 |
| **服务管理** | `PlexLineSelector.vue` | `src/components/PlexLineSelector.vue` | 我的 → Plex服务 | Plex线路选择 |
| **Premium** | `PremiumUnlockDialog.vue` | `src/components/PremiumUnlockDialog.vue` | 我的 → Premium | 高级线路解锁 |
| **捐赠** | `DonationDialog.vue` | `src/components/DonationDialog.vue` | 我的 → 捐赠支持 | 捐赠记录 |
| **游戏活动** | `LuckyWheel.vue` | `src/components/LuckyWheel.vue` | 娱乐 → 幸运转盘 | 幸运大转盘游戏 |
| **游戏活动** | `Blackjack.vue` | `src/components/Blackjack.vue` | 娱乐 → 21点 | 21点游戏 |
| **游戏活动** | `MatchPredictionGame.vue` | `src/components/MatchPredictionGame.vue` | 娱乐 → 赛事竞猜 | 赛事竞猜游戏 |
| **修仙游戏** | `Xiuxian.vue` | `src/views/Xiuxian.vue` | **新建** - 娱乐 → 修仙世界 | 修仙游戏主页面 |
| **管理员** | `AdminInviteCodeDialog.vue` | `src/components/AdminInviteCodeDialog.vue` | 设置 → 邀请码管理 | 管理员生成邀请码 |
| **管理员** | `LineManagementDialog.vue` | `src/components/LineManagementDialog.vue` | 设置 → 线路管理 | 线路CRUD管理 |
| **管理员** | `TagManagementDialog.vue` | `src/components/TagManagementDialog.vue` | 设置 → 标签管理 | 线路标签管理 |
| **管理员** | `TgBindingDialog.vue` | `src/components/TgBindingDialog.vue` | 设置 → TG换绑 | Telegram账号换绑 |
| **管理员** | `PrivilegedUserDialog.vue` | `src/components/PrivilegedUserDialog.vue` | 设置 → 特权用户 | 特权用户管理 |
| **管理员** | `CreditsTransferDialog.vue` | `src/components/CreditsTransferDialog.vue` | 设置 → 积分转移 | 积分转移操作 |
| **管理员** | `NsfwDialog.vue` | `src/components/NsfwDialog.vue` | 设置 → NSFW管理 | NSFW内容管理 |
| **管理员** | `LineTrafficStatsPanel.vue` | `src/components/LineTrafficStatsPanel.vue` | 设置 → 流量统计 | 线路流量统计 |
| **管理员** | `LineSwitchHistoryDialog.vue` | `src/components/LineSwitchHistoryDialog.vue` | 设置 → 切换历史 | 线路切换历史 |

### 三级页面/嵌套对话框 (Nested Dialogs)

| 组件名称 | 文件路径 | 父级组件 | 用途 |
|---------|---------|---------|------|
| `RandomnessConfigDialog.vue` | `src/components/RandomnessConfigDialog.vue` | WheelAdminPanel | 转盘随机性配置 |
| **出价弹窗** (内嵌在 Activities) | `Activities.vue` 内部 | 竞拍详情Dialog | 竞拍出价 |

### 管理员面板组件 (Admin Panels)

| 组件名称 | 文件路径 | 集成位置 | 用途 |
|---------|---------|---------|------|
| `WheelAdminPanel.vue` | `src/components/WheelAdminPanel.vue` | 设置 → 活动管理 Tab | 幸运转盘管理 |
| `AuctionAdminPanel.vue` | `src/components/AuctionAdminPanel.vue` | 设置 → 活动管理 Tab | 竞拍活动管理 |
| `BlackjackAdminPanel.vue` | `src/components/BlackjackAdminPanel.vue` | 设置 → 活动管理 Tab | 21点游戏管理 |
| `MatchPredictionAdminPanel.vue` | `src/components/MatchPredictionAdminPanel.vue` | 设置 → 活动管理 Tab | 赛事竞猜管理 |
| `ThemeConfigPanel.vue` | `src/components/ThemeConfigPanel.vue` | 设置 → 主题配置 Tab | 主题颜色配置 |

### 导航组件 (Navigation)

| 组件名称 | 文件路径 | 说明 |
|---------|---------|------|
| `BottomMenu.vue` | `src/components/BottomMenu.vue` | **优化** - 移除＋号，5个按钮 |

---

## 🎨 需要优化的组件清单

### ✅ 需要创建的新组件

1. **Home.vue** - 主页Dashboard
   - Hero Banner with gradient background
   - Quick Actions grid
   - Stats overview cards
   - Continue playing section
   - HBO style cards & colors

### 🔧 需要重度优化的组件 (HBO风格改造)

1. **UserInfo.vue** → Profile
   - 添加快捷操作区 (4个原扇形菜单功能)
   - HBO风格卡片
   - 渐变背景
   - 改进信息布局

2. **Activities.vue** → Entertainment
   - 添加修仙游戏Tab
   - Tab导航HBO风格
   - 卡片渐变效果
   - 改进活动卡片样式

3. **Rankings.vue**
   - Tab导航HBO风格
   - 金牌🥇、银牌🥈、铜牌🥉视觉增强
   - 添加修仙排行榜选项
   - 排行榜卡片渐变

4. **Management.vue** → Settings.vue (重命名)
   - HBO风格Tab导航
   - 管理卡片渐变背景
   - 改进开关控件样式
   - 统一管理员面板风格

5. **BottomMenu.vue**
   - 移除中间＋号按钮
   - 5个按钮均匀分布
   - HBO风格图标和颜色
   - Active状态渐变效果

### 💅 需要中度优化的组件 (样式统一)

所有Dialog组件需要统一HBO风格:

**快捷操作类:**
- RedeemCodeDialog.vue
- InviteCodeDialog.vue
- BindAccountDialog.vue
- BindLineDialog.vue

**服务管理类:**
- EmbyLineSelector.vue
- PlexLineSelector.vue
- PremiumUnlockDialog.vue
- DonationDialog.vue

**游戏活动类:**
- LuckyWheel.vue
- Blackjack.vue
- MatchPredictionGame.vue

**管理员类:**
- AdminInviteCodeDialog.vue
- LineManagementDialog.vue
- TagManagementDialog.vue
- TgBindingDialog.vue
- PrivilegedUserDialog.vue
- CreditsTransferDialog.vue
- NsfwDialog.vue
- LineTrafficStatsPanel.vue
- LineSwitchHistoryDialog.vue
- RandomnessConfigDialog.vue

**管理员面板类:**
- WheelAdminPanel.vue
- AuctionAdminPanel.vue
- BlackjackAdminPanel.vue
- MatchPredictionAdminPanel.vue
- ThemeConfigPanel.vue

---

## 📐 优化优先级

### Phase 1: 核心架构 (最高优先级)
1. ✅ 创建 HBO 设计系统文档
2. ✅ 实现全局主题配置 (Vuetify theme)
3. ✅ 优化 BottomMenu.vue (移除＋号)
4. ✅ 创建 Home.vue 主页

### Phase 2: 一级页面优化
5. ✅ 优化 UserInfo.vue (添加快捷操作)
6. ✅ 优化 Activities.vue (添加修仙Tab)
7. ✅ 优化 Rankings.vue (HBO风格)
8. ✅ 重命名并优化 Management.vue → Settings.vue

### Phase 3: 二级对话框优化
9. ✅ 优化所有快捷操作对话框 (4个)
10. ✅ 优化所有服务管理对话框 (4个)
11. ✅ 优化所有游戏活动组件 (3个)
12. ✅ 创建 Xiuxian.vue 修仙游戏页面

### Phase 4: 管理员组件优化
13. ✅ 优化所有管理员对话框 (9个)
14. ✅ 优化所有管理员面板 (5个)

### Phase 5: 最终测试与调优
15. ✅ 响应式布局测试 (移动端/平板/桌面)
16. ✅ 颜色一致性检查
17. ✅ 动画效果完善
18. ✅ 性能优化

---

## 🎯 HBO 设计要求总结

### 颜色规范
```scss
// 主色调 Primary
$purple-primary: #7B2CBF;
$purple-deep: #5A189A;
$purple-darkest: #10002B;

// 强调色 Accent
$gold: #FFD60A;  // 积分、奖励
$cyan: #06FFA5;  // 灵石、成功
$pink: #FF006E;  // 消耗、警告

// 背景色
$bg-black: #000000;
$bg-purple: #1A0033;
$bg-purple-transparent: rgba(123, 44, 191, 0.1);
```

### 通用组件样式要求

1. **卡片 (v-card)**
   - 圆角: `border-radius: 20px`
   - 渐变背景: `linear-gradient(135deg, #7B2CBF 0%, #5A189A 100%)`
   - 阴影: `box-shadow: 0 20px 40px rgba(0, 0, 0, 0.2)`
   - 毛玻璃效果: `backdrop-filter: blur(10px)`

2. **按钮 (v-btn)**
   - 主要按钮: 紫色渐变 + 金色文字
   - 次要按钮: 描边 + 紫色文字
   - Hover效果: `transform: translateY(-2px)` + 阴影加深

3. **Tab导航 (v-tabs)**
   - Active Tab: 紫色渐变下划线
   - 图标 + 文字组合
   - 紫色系配色

4. **对话框 (v-dialog)**
   - 标题栏: 紫色渐变背景 + 白色文字
   - 内容区: 深色背景 + 紫色点缀
   - 圆角边框

5. **列表项 (v-list-item)**
   - Hover: 紫色半透明背景
   - Active: 紫色渐变边框
   - 前三名特殊样式: 金牌🥇、银牌🥈、铜牌🥉

---

**页面层级分析完成！** ✅
