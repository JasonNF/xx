# HBO 风格设计系统 - PMSManageBot WebApp

## 📐 设计哲学

HBO Max 的设计理念：**沉浸式、奢华、高端**
- 深色主题营造电影院般的沉浸感
- 紫色渐变彰显品牌独特性
- 金色点缀传递高级感和奖励感
- 流畅动画提升交互体验

---

## 🎨 颜色系统

### 主色调 (Primary Colors)

```scss
// 紫色系 - 品牌主色
$purple-light: #9D4EDD;      // 浅紫 - Hover状态
$purple-primary: #7B2CBF;    // 主紫 - 主要元素
$purple-deep: #5A189A;       // 深紫 - 深色变体
$purple-darkest: #10002B;    // 极深紫 - 背景色

// 渐变定义
$gradient-primary: linear-gradient(135deg, #7B2CBF 0%, #5A189A 100%);
$gradient-primary-hover: linear-gradient(135deg, #9D4EDD 0%, #7B2CBF 100%);
$gradient-hero: linear-gradient(180deg, #10002B 0%, #5A189A 50%, #7B2CBF 100%);
```

### 强调色 (Accent Colors)

```scss
// 金色 - 积分、奖励、VIP
$gold: #FFD60A;
$gold-dark: #FFC300;
$gold-light: #FFEA00;

// 青色 - 灵石、成功、确认
$cyan: #06FFA5;
$cyan-dark: #00E68A;
$cyan-light: #7FFFD4;

// 粉红 - 消耗、警告、强调
$pink: #FF006E;
$pink-dark: #D90050;
$pink-light: #FF4D94;

// 橙色 - Emby品牌色
$orange: #FF9800;
$orange-dark: #F57C00;

// 蓝色 - Plex品牌色、竞拍
$blue: #2196F3;
$blue-dark: #1976D2;

// 绿色 - 成功、在线
$green: #4CAF50;
$green-dark: #388E3C;
```

### 中性色 (Neutral Colors)

```scss
// 背景色
$bg-black: #000000;          // 纯黑背景
$bg-dark: #0A0A0A;           // 深灰背景
$bg-purple-dark: #1A0033;    // 深紫背景
$bg-card: #1E1E1E;           // 卡片背景
$bg-elevated: #2A2A2A;       // 提升背景

// 文字色
$text-primary: #FFFFFF;      // 主要文字
$text-secondary: rgba(255, 255, 255, 0.7);  // 次要文字
$text-disabled: rgba(255, 255, 255, 0.4);   // 禁用文字

// 边框色
$border-subtle: rgba(255, 255, 255, 0.1);
$border-medium: rgba(255, 255, 255, 0.2);
$border-strong: rgba(255, 255, 255, 0.3);

// 半透明覆盖
$overlay-light: rgba(0, 0, 0, 0.3);
$overlay-medium: rgba(0, 0, 0, 0.6);
$overlay-heavy: rgba(0, 0, 0, 0.8);
```

### 语义色 (Semantic Colors)

```scss
// 成功
$success: #06FFA5;
$success-bg: rgba(6, 255, 165, 0.1);

// 警告
$warning: #FFD60A;
$warning-bg: rgba(255, 214, 10, 0.1);

// 错误
$error: #FF006E;
$error-bg: rgba(255, 0, 110, 0.1);

// 信息
$info: #2196F3;
$info-bg: rgba(33, 150, 243, 0.1);
```

---

## 🔤 字体系统

### 字体族

```scss
$font-family-sans: 'PingFang SC', 'Helvetica Neue', Helvetica, 'Microsoft YaHei', Arial, sans-serif;
$font-family-mono: 'Menlo', 'Monaco', 'Courier New', monospace;
```

### 字号体系

```scss
// 标题
$font-size-h1: 32px;   // 页面主标题
$font-size-h2: 28px;   // 区块标题
$font-size-h3: 24px;   // 卡片标题
$font-size-h4: 20px;   // 小标题
$font-size-h5: 18px;   // 辅助标题
$font-size-h6: 16px;   // 最小标题

// 正文
$font-size-body-large: 16px;
$font-size-body: 14px;
$font-size-body-small: 12px;

// 辅助文字
$font-size-caption: 12px;
$font-size-overline: 10px;
```

### 字重

```scss
$font-weight-light: 300;
$font-weight-regular: 400;
$font-weight-medium: 500;
$font-weight-semibold: 600;
$font-weight-bold: 700;
$font-weight-extrabold: 800;
```

### 行高

```scss
$line-height-tight: 1.2;
$line-height-normal: 1.5;
$line-height-relaxed: 1.75;
$line-height-loose: 2;
```

---

## 📏 间距系统

### 基础间距单位

```scss
$spacing-unit: 8px;

// 间距尺寸
$spacing-0: 0;
$spacing-1: 4px;    // 0.5 unit
$spacing-2: 8px;    // 1 unit
$spacing-3: 12px;   // 1.5 units
$spacing-4: 16px;   // 2 units
$spacing-5: 20px;   // 2.5 units
$spacing-6: 24px;   // 3 units
$spacing-8: 32px;   // 4 units
$spacing-10: 40px;  // 5 units
$spacing-12: 48px;  // 6 units
$spacing-16: 64px;  // 8 units
$spacing-20: 80px;  // 10 units
```

### 组件内间距 (Padding)

```scss
// 卡片内边距
$card-padding-sm: $spacing-4;     // 16px
$card-padding-md: $spacing-6;     // 24px
$card-padding-lg: $spacing-8;     // 32px

// 按钮内边距
$btn-padding-x-sm: $spacing-3;    // 12px
$btn-padding-y-sm: $spacing-2;    // 8px
$btn-padding-x-md: $spacing-4;    // 16px
$btn-padding-y-md: $spacing-3;    // 12px
$btn-padding-x-lg: $spacing-6;    // 24px
$btn-padding-y-lg: $spacing-4;    // 16px
```

---

## 🎭 阴影系统

```scss
// 卡片阴影
$shadow-sm: 0 2px 8px rgba(0, 0, 0, 0.1);
$shadow-md: 0 8px 16px rgba(0, 0, 0, 0.15);
$shadow-lg: 0 12px 24px rgba(0, 0, 0, 0.2);
$shadow-xl: 0 20px 40px rgba(0, 0, 0, 0.25);
$shadow-2xl: 0 24px 48px rgba(0, 0, 0, 0.3);

// 紫色光晕阴影
$shadow-purple-glow: 0 0 20px rgba(123, 44, 191, 0.4);
$shadow-purple-glow-strong: 0 0 30px rgba(123, 44, 191, 0.6);

// 金色光晕阴影
$shadow-gold-glow: 0 0 20px rgba(255, 214, 10, 0.4);
```

---

## 🔲 圆角系统

```scss
$border-radius-sm: 8px;
$border-radius-md: 12px;
$border-radius-lg: 16px;
$border-radius-xl: 20px;
$border-radius-2xl: 24px;
$border-radius-full: 9999px;  // 完全圆形
```

---

## ⚡ 动画系统

### 过渡时间

```scss
$transition-fast: 150ms;
$transition-base: 250ms;
$transition-slow: 350ms;
$transition-slower: 500ms;
```

### 缓动函数

```scss
$ease-in-out: cubic-bezier(0.4, 0, 0.2, 1);
$ease-out: cubic-bezier(0, 0, 0.2, 1);
$ease-in: cubic-bezier(0.4, 0, 1, 1);
$ease-bounce: cubic-bezier(0.68, -0.55, 0.265, 1.55);
```

### 通用过渡

```scss
$transition-all: all $transition-base $ease-in-out;
$transition-transform: transform $transition-base $ease-in-out;
$transition-opacity: opacity $transition-base $ease-in-out;
$transition-color: color $transition-base $ease-in-out;
$transition-background: background $transition-base $ease-in-out;
```

---

## 🧩 组件规范

### 1. 按钮 (Button)

#### 主要按钮 (Primary)

```scss
.btn-primary {
  background: $gradient-primary;
  color: $gold;
  border: none;
  border-radius: $border-radius-lg;
  padding: $btn-padding-y-md $btn-padding-x-md;
  font-weight: $font-weight-semibold;
  box-shadow: $shadow-md;
  transition: $transition-all;

  &:hover {
    background: $gradient-primary-hover;
    transform: translateY(-2px);
    box-shadow: $shadow-lg;
  }

  &:active {
    transform: translateY(0);
  }

  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
    transform: none;
  }
}
```

#### 次要按钮 (Secondary)

```scss
.btn-secondary {
  background: transparent;
  color: $purple-primary;
  border: 2px solid $purple-primary;
  border-radius: $border-radius-lg;
  padding: $btn-padding-y-md $btn-padding-x-md;
  font-weight: $font-weight-semibold;
  transition: $transition-all;

  &:hover {
    background: rgba(123, 44, 191, 0.1);
    border-color: $purple-light;
    color: $purple-light;
  }
}
```

#### 文本按钮 (Text)

```scss
.btn-text {
  background: transparent;
  color: $purple-primary;
  border: none;
  padding: $btn-padding-y-sm $btn-padding-x-sm;
  font-weight: $font-weight-medium;
  transition: $transition-color;

  &:hover {
    color: $purple-light;
    background: rgba(123, 44, 191, 0.05);
  }
}
```

### 2. 卡片 (Card)

#### 基础卡片

```scss
.card {
  background: $bg-card;
  border-radius: $border-radius-xl;
  padding: $card-padding-md;
  box-shadow: $shadow-lg;
  backdrop-filter: blur(10px);
  border: 1px solid $border-subtle;
  transition: $transition-all;

  &:hover {
    transform: translateY(-4px);
    box-shadow: $shadow-2xl;
  }
}
```

#### 渐变卡片

```scss
.card-gradient {
  background: $gradient-primary;
  color: $text-primary;
  border-radius: $border-radius-xl;
  padding: $card-padding-md;
  box-shadow: $shadow-purple-glow;
  position: relative;
  overflow: hidden;

  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: linear-gradient(135deg, transparent 0%, rgba(255, 255, 255, 0.1) 100%);
    pointer-events: none;
  }
}
```

#### 玻璃态卡片

```scss
.card-glass {
  background: rgba(30, 30, 30, 0.6);
  backdrop-filter: blur(20px);
  border: 1px solid $border-subtle;
  border-radius: $border-radius-xl;
  padding: $card-padding-md;
  box-shadow: $shadow-lg;
}
```

### 3. Tab 导航

```scss
.tabs {
  background: transparent;
  border-bottom: 2px solid $border-subtle;

  .tab-item {
    color: $text-secondary;
    font-weight: $font-weight-medium;
    padding: $spacing-4 $spacing-6;
    transition: $transition-color;
    position: relative;

    &::after {
      content: '';
      position: absolute;
      bottom: -2px;
      left: 0;
      right: 0;
      height: 3px;
      background: $gradient-primary;
      transform: scaleX(0);
      transition: transform $transition-base $ease-out;
    }

    &:hover {
      color: $text-primary;
    }

    &.active {
      color: $text-primary;

      &::after {
        transform: scaleX(1);
      }
    }
  }
}
```

### 4. 对话框 (Dialog)

```scss
.dialog {
  background: $bg-card;
  border-radius: $border-radius-2xl;
  box-shadow: $shadow-2xl;
  overflow: hidden;
  max-width: 600px;

  .dialog-header {
    background: $gradient-primary;
    color: $text-primary;
    padding: $spacing-6;
    display: flex;
    align-items: center;
    justify-content: space-between;

    .dialog-title {
      font-size: $font-size-h4;
      font-weight: $font-weight-bold;
      display: flex;
      align-items: center;
      gap: $spacing-3;
    }

    .dialog-close {
      color: $text-primary;
      opacity: 0.8;
      transition: $transition-opacity;

      &:hover {
        opacity: 1;
      }
    }
  }

  .dialog-content {
    padding: $spacing-8;
    max-height: 70vh;
    overflow-y: auto;

    // 自定义滚动条
    &::-webkit-scrollbar {
      width: 8px;
    }

    &::-webkit-scrollbar-track {
      background: $bg-dark;
      border-radius: $border-radius-full;
    }

    &::-webkit-scrollbar-thumb {
      background: $purple-primary;
      border-radius: $border-radius-full;

      &:hover {
        background: $purple-light;
      }
    }
  }

  .dialog-actions {
    padding: $spacing-6;
    border-top: 1px solid $border-subtle;
    display: flex;
    gap: $spacing-4;
    justify-content: flex-end;
  }
}
```

### 5. 列表项 (List Item)

```scss
.list-item {
  background: $bg-card;
  border-radius: $border-radius-lg;
  padding: $spacing-4;
  margin-bottom: $spacing-3;
  transition: $transition-all;
  display: flex;
  align-items: center;
  gap: $spacing-4;

  &:hover {
    background: rgba(123, 44, 191, 0.1);
    transform: translateX(4px);
  }

  &.active {
    background: $gradient-primary;
    box-shadow: $shadow-purple-glow;
  }

  // 前三名特殊样式
  &.rank-1 {
    background: linear-gradient(135deg, rgba(255, 214, 10, 0.2) 0%, rgba(255, 195, 0, 0.1) 100%);
    border: 2px solid $gold;
  }

  &.rank-2 {
    background: rgba(192, 192, 192, 0.1);
    border: 2px solid #C0C0C0;
  }

  &.rank-3 {
    background: rgba(205, 127, 50, 0.1);
    border: 2px solid #CD7F32;
  }
}
```

### 6. 输入框 (Input)

```scss
.input {
  background: $bg-elevated;
  border: 2px solid $border-medium;
  border-radius: $border-radius-md;
  padding: $spacing-3 $spacing-4;
  color: $text-primary;
  font-size: $font-size-body;
  transition: $transition-all;

  &:focus {
    outline: none;
    border-color: $purple-primary;
    box-shadow: $shadow-purple-glow;
  }

  &::placeholder {
    color: $text-disabled;
  }

  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
}
```

### 7. 徽章 (Badge/Chip)

```scss
.chip {
  display: inline-flex;
  align-items: center;
  gap: $spacing-2;
  padding: $spacing-1 $spacing-3;
  border-radius: $border-radius-full;
  font-size: $font-size-body-small;
  font-weight: $font-weight-medium;

  // 成功徽章
  &.chip-success {
    background: $success-bg;
    color: $success;
    border: 1px solid $success;
  }

  // 警告徽章
  &.chip-warning {
    background: $warning-bg;
    color: $warning;
    border: 1px solid $warning;
  }

  // 错误徽章
  &.chip-error {
    background: $error-bg;
    color: $error;
    border: 1px solid $error;
  }

  // 信息徽章
  &.chip-info {
    background: $info-bg;
    color: $info;
    border: 1px solid $info;
  }
}
```

### 8. 进度条 (Progress Bar)

```scss
.progress {
  background: $bg-dark;
  border-radius: $border-radius-full;
  height: 8px;
  overflow: hidden;
  position: relative;

  .progress-bar {
    background: $gradient-primary;
    height: 100%;
    border-radius: $border-radius-full;
    transition: width $transition-slow $ease-out;
    position: relative;

    &::after {
      content: '';
      position: absolute;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
      background: linear-gradient(90deg, transparent 0%, rgba(255, 255, 255, 0.3) 50%, transparent 100%);
      animation: shimmer 2s infinite;
    }
  }
}

@keyframes shimmer {
  0% {
    transform: translateX(-100%);
  }
  100% {
    transform: translateX(100%);
  }
}
```

### 9. 通知 (Snackbar/Toast)

```scss
.snackbar {
  background: $bg-elevated;
  color: $text-primary;
  border-radius: $border-radius-lg;
  padding: $spacing-4 $spacing-6;
  box-shadow: $shadow-xl;
  display: flex;
  align-items: center;
  gap: $spacing-4;
  min-width: 300px;

  &.snackbar-success {
    border-left: 4px solid $success;
  }

  &.snackbar-warning {
    border-left: 4px solid $warning;
  }

  &.snackbar-error {
    border-left: 4px solid $error;
  }

  &.snackbar-info {
    border-left: 4px solid $info;
  }
}
```

### 10. 底部导航 (Bottom Navigation)

```scss
.bottom-nav {
  background: rgba(10, 10, 10, 0.95);
  backdrop-filter: blur(20px);
  border-top: 1px solid $border-subtle;
  padding: $spacing-3 0;
  display: flex;
  justify-content: space-around;
  align-items: center;
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  z-index: 1000;

  .nav-item {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: $spacing-1;
    padding: $spacing-2;
    color: $text-secondary;
    transition: $transition-color;
    cursor: pointer;
    position: relative;

    .nav-icon {
      font-size: 24px;
      transition: $transition-transform;
    }

    .nav-label {
      font-size: $font-size-caption;
      font-weight: $font-weight-medium;
    }

    &::before {
      content: '';
      position: absolute;
      top: -$spacing-3;
      left: 50%;
      transform: translateX(-50%) scaleX(0);
      width: 40px;
      height: 3px;
      background: $gradient-primary;
      border-radius: $border-radius-full;
      transition: transform $transition-base $ease-out;
    }

    &:hover {
      color: $purple-light;

      .nav-icon {
        transform: translateY(-2px);
      }
    }

    &.active {
      color: $text-primary;

      &::before {
        transform: translateX(-50%) scaleX(1);
      }

      .nav-icon {
        color: $purple-primary;
      }
    }
  }
}
```

---

## 📱 响应式断点

```scss
// Vuetify breakpoints
$breakpoint-xs: 0px;      // 手机竖屏
$breakpoint-sm: 600px;    // 手机横屏 / 小平板
$breakpoint-md: 960px;    // 平板
$breakpoint-lg: 1280px;   // 桌面
$breakpoint-xl: 1920px;   // 大屏幕
$breakpoint-xxl: 2560px;  // 超大屏幕

// 媒体查询
@mixin xs-only {
  @media (max-width: #{$breakpoint-sm - 1}) {
    @content;
  }
}

@mixin sm-and-up {
  @media (min-width: $breakpoint-sm) {
    @content;
  }
}

@mixin md-and-up {
  @media (min-width: $breakpoint-md) {
    @content;
  }
}

@mixin lg-and-up {
  @media (min-width: $breakpoint-lg) {
    @content;
  }
}
```

---

## 🎬 特殊效果

### 渐变动画

```scss
@keyframes gradient-shift {
  0% {
    background-position: 0% 50%;
  }
  50% {
    background-position: 100% 50%;
  }
  100% {
    background-position: 0% 50%;
  }
}

.animated-gradient {
  background: linear-gradient(270deg, #7B2CBF, #5A189A, #9D4EDD);
  background-size: 600% 600%;
  animation: gradient-shift 10s ease infinite;
}
```

### 浮动效果

```scss
@keyframes float {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-10px);
  }
}

.floating {
  animation: float 3s ease-in-out infinite;
}
```

### 脉冲效果

```scss
@keyframes pulse {
  0%, 100% {
    opacity: 1;
    transform: scale(1);
  }
  50% {
    opacity: 0.8;
    transform: scale(1.05);
  }
}

.pulsing {
  animation: pulse 2s ease-in-out infinite;
}
```

### 光晕扫描

```scss
@keyframes scan {
  0% {
    box-shadow: 0 0 0 0 rgba(123, 44, 191, 0.7);
  }
  70% {
    box-shadow: 0 0 0 20px rgba(123, 44, 191, 0);
  }
  100% {
    box-shadow: 0 0 0 0 rgba(123, 44, 191, 0);
  }
}

.scan-effect {
  animation: scan 2s infinite;
}
```

---

## ✅ 设计检查清单

### 颜色使用
- [ ] 使用紫色渐变作为主色调
- [ ] 金色用于积分、奖励、VIP
- [ ] 青色用于灵石、成功状态
- [ ] 粉红色用于消耗、警告
- [ ] 保持足够的颜色对比度 (WCAG AA标准)

### 间距一致性
- [ ] 使用 8px 基础间距单位
- [ ] 卡片内边距统一使用定义的尺寸
- [ ] 元素间距保持视觉节奏

### 圆角统一
- [ ] 卡片使用 20px 圆角
- [ ] 按钮使用 16px 圆角
- [ ] 输入框使用 12px 圆角
- [ ] 徽章使用完全圆角

### 阴影层级
- [ ] 卡片使用 shadow-lg
- [ ] 提升元素使用 shadow-xl
- [ ] 浮动元素使用 shadow-2xl
- [ ] 紫色光晕用于强调元素

### 动画流畅性
- [ ] 所有过渡使用定义的时长
- [ ] 使用合适的缓动函数
- [ ] Hover效果平滑
- [ ] 避免过度动画

### 响应式设计
- [ ] 手机端单列布局
- [ ] 平板端双列布局
- [ ] 桌面端三列布局
- [ ] 触摸目标至少 44x44px

---

**HBO 设计系统文档完成！** 🎨✨
