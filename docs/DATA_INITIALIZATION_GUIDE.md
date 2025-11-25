# 数据初始化指南

## 📋 概述

本指南说明了凡人修仙传游戏的所有数据初始化脚本及其运行顺序。

---

## 🗂️ 初始化脚本列表

| 脚本名称 | 功能 | 数据量 | 依赖 | 状态 |
|---------|------|--------|------|------|
| `init_mortal_data.py` | 基础游戏数据 | 门派、技能、物品、怪物、秘境、任务 | 无 | ✅ 完成 |
| `init_cultivation_methods.py` | 功法系统 | 43种功法 | 无 | ✅ 完成 |
| `init_equipment_system.py` | 装备系统 | 67件装备 | 无 | ✅ 完成 |
| `init_credit_shop_cultivation.py` | 积分商城-功法 | 6种天级功法 | 功法系统 | ✅ 完成 |
| `init_credit_shop_equipment.py` | 积分商城-装备 | 24件神品装备 | 装备系统 | ✅ 完成 |
| `init_alchemy_system.py` | 炼丹系统 | 16种材料、36种丹药、36种丹方 | 基础数据 | ✅ 完成 |
| `init_talisman_system.py` | 符箓系统 | 10种材料、30种符箓 | 基础数据 | ✅ 完成 |
| `init_refinery_system.py` | 炼器系统 | 炼器配方 | - | ⏳ 待开发 |

---

## 🚀 完整初始化流程

### 方案一：完整初始化（推荐）

如果是第一次初始化或需要重置所有数据：

```bash
cd /Users/zc/EC-AI/xiuxian-game

# 1. 初始化基础数据（门派、技能、物品、怪物、秘境、任务）
python3 scripts/init_mortal_data.py

# 2. 初始化功法系统（43种功法）
python3 scripts/init_cultivation_methods.py

# 3. 初始化装备系统（67件装备）
python3 scripts/init_equipment_system.py

# 4. 将天级功法添加到积分商城
python3 scripts/init_credit_shop_cultivation.py

# 5. 将神品装备添加到积分商城
python3 scripts/init_credit_shop_equipment.py

# 6. 初始化炼丹系统（16种材料、36种丹药、36种丹方）
python3 scripts/init_alchemy_system.py

# 7. 初始化符箓系统（10种材料、30种符箓）
python3 scripts/init_talisman_system.py

# 8. 初始化炼器系统（待开发）
# python3 scripts/init_refinery_system.py
```

### 方案二：分模块初始化

如果只需要初始化特定模块：

#### 仅初始化功法系统
```bash
python3 scripts/init_cultivation_methods.py
python3 scripts/init_credit_shop_cultivation.py
```

#### 仅初始化装备系统
```bash
python3 scripts/init_equipment_system.py
python3 scripts/init_credit_shop_equipment.py
```

#### 仅初始化炼丹系统
```bash
python3 scripts/init_alchemy_system.py
```

#### 仅初始化符箓系统
```bash
python3 scripts/init_talisman_system.py
```

---

## 📊 各脚本详细说明

### 1. init_mortal_data.py

**功能**：初始化基础游戏数据

**创建内容**：
- ✅ 10+个门派（天南七派、魔道六宗）
- ✅ 90+个基础法术技能
- ✅ 9种基础物品（丹药、法器、灵药）
- ✅ 基础怪物数据
- ✅ 秘境数据
- ✅ 主线任务数据

**注意事项**：
- 此脚本会初始化数据库表结构
- 功法创建已移除（统一使用 `init_cultivation_methods.py`）

---

### 2. init_cultivation_methods.py

**功能**：初始化完整功法体系

**创建内容**：
- ✅ 人级功法：6种（基础入门）
- ✅ 黄级功法：8种（进阶修炼）
- ✅ 玄级功法：10种（中级修炼）
- ✅ 地级功法：8种（高级修炼）
- ✅ 天级功法：6种（顶级修炼，积分商城）
- ✅ 神级功法：5种（特殊获取）

**设计文档**：`CULTIVATION_METHOD_SYSTEM_DESIGN.md`

**修炼速度加成范围**：1.0x - 3.5x

---

### 3. init_equipment_system.py

**功能**：初始化完整装备体系

**创建内容**：
- ✅ 凡品装备：15件（基础装备）
- ✅ 仙品装备：28件（进阶装备）
- ✅ 神品装备：24件（四象套装）

**装备槽位**：武器、副手、头部、身体、腿部、脚部、饰品（7个槽位）

**设计文档**：`EQUIPMENT_SYSTEM_DESIGN.md`

**注意事项**：
- 神品装备不设置 `buy_price`（通过积分商城获取）
- 支持套装效果（2/4/6件套）

---

### 4. init_credit_shop_cultivation.py

**功能**：将天级功法添加到积分商城

**创建内容**：6种天级功法的商城条目

**积分价格**：
- 大衍诀：50,000积分
- 混沌剑经：60,000积分
- 不死不灭功：70,000积分
- 星辰变：80,000积分
- 吞天魔功：100,000积分
- 造化金章：120,000积分

**购买限制**：每人每种限购1次

**依赖**：必须先运行 `init_cultivation_methods.py`

---

### 5. init_credit_shop_equipment.py

**功能**：将神品装备（四象套装）添加到积分商城

**创建内容**：24件神品装备的商城条目

**积分价格范围**：
- 武器：20,000-24,000积分
- 身体：18,000-20,000积分
- 头部：16,000-18,000积分
- 腿部/脚部：14,000-16,000积分
- 饰品：20,000-24,000积分

**购买限制**：每人每件限购1次

**依赖**：必须先运行 `init_equipment_system.py`

---

### 6. init_alchemy_system.py

**功能**：初始化完整炼丹系统

**创建内容**：
- ✅ 16种炼丹材料（基础灵草4种，中级灵药5种，高级灵物5种，顶级仙药2种）
- ✅ 36种丹药物品（凡品8种，灵品10种，宝品8种，仙品6种，神品4种）
- ✅ 36种丹方配方（对应36种丹药的炼制配方）

**设计文档**：`ALCHEMY_SYSTEM_DESIGN.md`

**材料类型**：
- 基础灵草：青灵草、碧心花、紫云芝、金线藤
- 中级灵药：玉随芝（已有）、赤火果、寒冰莲、金刚果、九幽草
- 高级灵物：天灵果、紫髓晶、龙血草、凤羽花、星月露
- 顶级仙药：血参精、化神花

**丹药分级**：
- 凡品丹药（8种）：回春丹、聚灵丹、炼气丹、凝气丹、强体丹、清心丹、疾速丹、防御丹
- 灵品丹药（10种）：筑基丹、大回春丹、大聚灵丹、增元丹、火灵丹、冰魄丹、破障丹、金身丹、疗毒丹、灵智丹
- 宝品丹药（8种）：凝金丹、返魂丹、金丹培元丹、龙虎丹、破瓶丹、五行丹、紫髓丹、固元丹
- 仙品丹药（6种）：破婴丹、元婴培元丹、涅槃丹、化婴丹、续命丹、神通丹
- 神品丹药（4种）：化神丹、化神培元丹、天劫丹、大还丹

**炼丹机制**：
- 炼丹等级系统（1-22级）
- 成功率计算（基础成功率 + 等级加成 + 功法加成）
- 经验成长（炼制成功获得经验，提升炼丹等级）
- 材料消耗（不同品级丹药需要不同材料组合）

**注意事项**：
- 部分丹药已在 `init_mortal_data.py` 中创建（筑基丹、凝金丹、回春丹、聚灵丹）
- 玉随芝材料已在基础数据中创建
- 脚本会自动跳过已存在的物品和丹方

---

### 7. init_talisman_system.py

**功能**：初始化完整符箓系统

**创建内容**：
- ✅ 10种符箓材料（符纸4种，墨料3种，特殊材料3种）
- ✅ 30种符箓配方（下品12种，中品10种，上品6种，极品2种）

**设计文档**：`TALISMAN_SYSTEM_DESIGN.md`

**符箓分类**：
- 攻击符：10种（火球符、冰锥符、金雷竹符、五雷符等）
- 防御符：6种（金光符、护体符、金刚符、金刚不坏符等）
- 治疗符：4种（回春符、聚灵符、大回春符、续命符）
- 遁符：4种（轻身符、遁地符、五行遁符、血影遁符）
- 辅助符：6种（探灵符、隐身符、破禁符、神识增幅符等）

**符箓材料体系**：
- 符纸类：白符纸(10灵石)、黄符纸(100)、玉符纸(1000)、仙符纸(10000)
- 墨料类：朱砂(5灵石)、精制朱砂(50)、天雷沙(500)
- 特殊材料：金雷竹粉末(5000)、五行灵粉(2000)、研磨工具(1000)

**制符等级系统**：1-23级，从学徒到符道仙人

**原著还原**：
- 金雷竹符：韩立在血色禁地的保命之宝
- 血影遁符：韩立的终极逃命符箓
- 五行遁符：原著中经典的瞬移符箓

**注意事项**：
- 符箓为一次性消耗品，使用后消失
- 部分材料可能需要灵药研磨获得（如金雷竹粉末）
- 脚本会自动跳过已存在的物品和配方

---

## ⚠️ 重要提示

### 数据冲突处理

1. **功法系统已整合**
   - ❌ 不要使用 `init_mortal_data.py` 中的旧功法数据（已移除）
   - ✅ 统一使用 `init_cultivation_methods.py`（43种完整功法）

2. **装备系统独立**
   - `init_mortal_data.py` 只创建少量基础物品（丹药、材料）
   - 完整装备系统使用 `init_equipment_system.py`（67件装备）

3. **积分商城依赖**
   - 积分商城脚本必须在对应的数据脚本之后运行
   - 否则会因为找不到物品ID而失败

### 运行顺序规则

✅ **正确顺序**：
```
init_mortal_data.py
  ↓
init_cultivation_methods.py → init_credit_shop_cultivation.py
  ↓
init_equipment_system.py → init_credit_shop_equipment.py
```

❌ **错误顺序**：
```
init_credit_shop_cultivation.py → init_cultivation_methods.py  # 会失败！
```

---

## 🔧 故障排除

### 问题1：枚举值不匹配错误

**错误信息**：`AttributeError: 'EquipmentSlot' object has no attribute 'HEAD'`

**解决方案**：
- 检查 `src/bot/models/item.py` 中的 `EquipmentSlot` 枚举定义
- 应包含：WEAPON, OFF_HAND, HEAD, BODY, LEGS, FEET, ACCESSORY

### 问题2：外键约束失败

**错误信息**：`FOREIGN KEY constraint failed`

**解决方案**：
- 检查脚本运行顺序
- 确保依赖的数据已先创建

### 问题3：重复数据错误

**错误信息**：`UNIQUE constraint failed`

**解决方案**：
- 清空数据库重新初始化
- 或跳过已存在的数据（脚本中已有检查逻辑）

---

## 📝 开发状态

### ✅ 已完成（P0）
- [x] 基础数据初始化
- [x] 功法系统（43种）
- [x] 装备系统（67件）
- [x] 积分商城整合
- [x] 枚举不匹配Bug修复
- [x] 功法系统整合
- [x] 炼丹系统初始化（16种材料、36种丹药、36种丹方）
- [x] 符箓系统初始化（10种材料、30种符箓）

### ⏳ 待开发（P1）
- [ ] 炼器系统初始化（炼器配方）

### 🔮 未来扩展（P2）
- [ ] 法术技能扩充（50+种技能）
- [ ] 怪物数据丰富（100+种怪物）
- [ ] 秘境关卡扩展
- [ ] 任务链完善

---

## 📚 相关文档

- `MORTAL_CULTIVATION_DESIGN.md` - 凡人修仙总体设计
- `CULTIVATION_METHOD_SYSTEM_DESIGN.md` - 功法系统设计（43种）
- `EQUIPMENT_SYSTEM_DESIGN.md` - 装备系统设计（67件）
- `EQUIPMENT_ENHANCEMENT_GUIDE.md` - 装备强化系统
- `ALCHEMY_SYSTEM_DESIGN.md` - 炼丹系统设计（36种丹药、36种丹方）
- `TALISMAN_SYSTEM_DESIGN.md` - 符箓系统设计（30种符箓）
- `积分商城系统说明.md` - 积分商城机制
- `数值平衡性设计文档.md` - 游戏数值平衡

---

**文档创建日期**: 2025-01-25
**最后更新**: 2025-01-25
**状态**: ✅ P1阶段-符箓系统完成，进入P1后续开发
