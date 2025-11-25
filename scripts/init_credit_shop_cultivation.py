"""积分商城 - 天级功法初始化脚本"""
import asyncio
import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from bot.models.database import init_db, AsyncSessionLocal
from bot.models.player import CultivationMethod
from bot.models.credit_shop import CreditShopItem, CreditShopCategory
from sqlalchemy import select


async def add_heaven_methods_to_credit_shop():
    """将所有天级功法添加到积分商城"""
    async with AsyncSessionLocal() as session:
        # 查询所有天级功法
        result = await session.execute(
            select(CultivationMethod).where(CultivationMethod.grade.like("天级%"))
        )
        heaven_methods = result.scalars().all()

        if not heaven_methods:
            print("❌ 未找到天级功法！请先运行 init_cultivation_methods.py")
            return

        print(f"✅ 找到 {len(heaven_methods)} 种天级功法")
        print("\n开始添加到积分商城...\n")

        # 定义天级功法的积分价格
        credit_prices = {
            "大衍诀": 50000,
            "混沌剑经": 60000,
            "不死不灭功": 70000,
            "星辰变": 80000,
            "吞天魔功": 100000,
            "造化金章": 120000,
        }

        # 功法类型标签
        type_tags = {
            "法修": "法修,灵力,法术伤害",
            "剑修": "剑修,攻击,暴击",
            "体修": "体修,防御,生存",
            "通用": "通用,全能,平衡",
            "特殊": "特殊,独特,稀有",
        }

        # 功法图标
        type_icons = {
            "法修": "🔮",
            "剑修": "⚔️",
            "体修": "🛡️",
            "通用": "✨",
            "特殊": "🌟",
        }

        added_count = 0
        for method in heaven_methods:
            # 检查是否已经存在
            existing = await session.execute(
                select(CreditShopItem).where(CreditShopItem.cultivation_method_id == method.id)
            )
            if existing.scalar_one_or_none():
                print(f"⏭️  跳过：{method.name}（已存在）")
                continue

            # 获取积分价格
            credit_price = credit_prices.get(method.name, 50000)  # 默认50000积分

            # 确定需求等级（基于境界要求）
            required_level = 15  # 天级功法最低15级
            if method.required_realm:
                realm_level_map = {
                    "炼气期": 1,
                    "筑基期": 7,
                    "金丹期": 13,
                    "元婴期": 18,
                    "化神期": 22,
                }
                for realm_name, level in realm_level_map.items():
                    if method.required_realm.name.startswith(realm_name[:2]):
                        required_level = level
                        break

            # 创建商城商品
            shop_item = CreditShopItem(
                name=method.name,
                description=f"{method.description}\n\n💫 天级功法，修炼速度加成：{method.cultivation_speed_bonus}x",
                category=CreditShopCategory.CULTIVATION_METHOD,
                cultivation_method_id=method.id,
                credit_price=credit_price,
                total_stock=-1,  # 无限库存
                remaining_stock=-1,
                sold_count=0,
                purchase_limit_per_player=1,  # 每人限购1次
                daily_purchase_limit=-1,  # 不限制每日购买
                required_level=required_level,
                required_vip_level=0,  # 不需要VIP
                discount_rate=1.0,  # 无折扣
                icon=type_icons.get(method.method_type, "📖"),
                tags=type_tags.get(method.method_type, "功法,修炼"),
                is_active=True,
                is_featured=True,  # 设为精选商品
                sort_order=200,  # 高优先级排序
            )

            session.add(shop_item)
            added_count += 1
            print(f"✅ 添加：{method.name} - {credit_price:,}积分 - {type_icons.get(method.method_type, '📖')} {method.method_type}")

        await session.commit()
        print(f"\n🎉 成功添加 {added_count} 种天级功法到积分商城！")


async def show_credit_shop_summary():
    """显示积分商城功法摘要"""
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(CreditShopItem).where(
                CreditShopItem.category == CreditShopCategory.CULTIVATION_METHOD
            ).order_by(CreditShopItem.credit_price.asc())
        )
        items = result.scalars().all()

        print("\n" + "=" * 60)
        print("📊 积分商城 - 天级功法一览")
        print("=" * 60)

        if not items:
            print("\n⚠️  商城中暂无功法")
            return

        # 按类型分组
        types = {}
        for item in items:
            # 获取关联的功法信息
            method_result = await session.execute(
                select(CultivationMethod).where(CultivationMethod.id == item.cultivation_method_id)
            )
            method = method_result.scalar_one_or_none()
            if method:
                method_type = method.method_type
                if method_type not in types:
                    types[method_type] = []
                types[method_type].append((item, method))

        for method_type, items_list in types.items():
            total_credits = sum(item[0].credit_price for item in items_list)
            print(f"\n{items_list[0][0].icon} **{method_type}功法** ({len(items_list)}种) - 总价：{total_credits:,}积分")
            print("━" * 60)
            for item, method in items_list:
                print(f"  • {item.name:<15} - {item.credit_price:>7,}积分 | 速度加成：{method.cultivation_speed_bonus}x")

        print("\n" + "=" * 60)
        print("💡 提示：")
        print("  • 所有天级功法需要达到相应境界和等级才能购买")
        print("  • 每种功法每人限购1次")
        print("  • 修炼天级功法可获得极高的修炼速度加成")
        print("  • 神级功法通过特殊途径获取（任务、活动等）")
        print("=" * 60 + "\n")


async def main():
    """主函数"""
    print("=" * 60)
    print("🏪 积分商城 - 天级功法初始化")
    print("=" * 60)

    print("\n📦 开始添加天级功法到积分商城...\n")

    await add_heaven_methods_to_credit_shop()
    await show_credit_shop_summary()

    print("\n💡 下一步：")
    print("1. 启动游戏测试积分商城功法兑换")
    print("2. 使用 /积分商城 命令查看可兑换功法")
    print("3. 使用 /我的积分 命令查看当前积分")
    print("4. 使用 /功法 命令查看已学习的功法\n")


if __name__ == "__main__":
    asyncio.run(main())
