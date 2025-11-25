"""积分商城 - 四象套装初始化脚本"""
import asyncio
import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from bot.models.database import init_db, AsyncSessionLocal
from bot.models.item import Item, EquipmentQuality
from bot.models.credit_shop import CreditShopItem, CreditShopCategory
from sqlalchemy import select


async def add_divine_equipment_to_credit_shop():
    """将所有神品（四象套装）装备添加到积分商城"""
    async with AsyncSessionLocal() as session:
        # 查询所有神品装备
        result = await session.execute(
            select(Item).where(Item.quality == EquipmentQuality.DIVINE)
        )
        divine_items = result.scalars().all()

        if not divine_items:
            print("❌ 未找到神品装备！请先运行 init_equipment_system.py")
            return

        print(f"✅ 找到 {len(divine_items)} 件神品装备")
        print("\n开始添加到积分商城...\n")

        # 定义四象套装的积分价格（根据装备槽位和价值）
        credit_prices = {
            # 武器最贵
            "青龙战剑": 20000,
            "朱雀焚天剑": 24000,
            "玄武镇海刀": 22000,
            "白虎斩魂剑": 23000,

            # 身体部位次贵
            "青龙战甲": 18000,
            "朱雀火羽甲": 19000,
            "玄武重甲": 20000,
            "白虎战甲": 19000,

            # 头部
            "青龙战盔": 16000,
            "朱雀烈焰盔": 17000,
            "玄武铁盔": 18000,
            "白虎战盔": 17000,

            # 腿部
            "青龙护腿": 14000,
            "朱雀炎腿": 15000,
            "玄武护腿": 16000,
            "白虎护腿": 15000,

            # 脚部
            "青龙战靴": 14000,
            "朱雀灵靴": 15000,
            "玄武战靴": 15000,
            "白虎战靴": 15000,

            # 饰品最贵（套装核心）
            "青龙玉佩": 20000,
            "朱雀炎珠": 22000,
            "玄武龟印": 24000,
            "白虎令": 22000,
        }

        # 套装标签
        set_tags = {
            "青龙": "攻击型,暴击,速度",
            "朱雀": "爆发型,暴击伤害,火系",
            "玄武": "防御型,生存,坦克",
            "白虎": "平衡型,全能,稳定",
        }

        # 套装图标
        set_icons = {
            "青龙": "🐉",
            "朱雀": "🔥",
            "玄武": "🛡️",
            "白虎": "⚔️",
        }

        added_count = 0
        for item in divine_items:
            # 检查是否已经存在
            existing = await session.execute(
                select(CreditShopItem).where(CreditShopItem.item_id == item.id)
            )
            if existing.scalar_one_or_none():
                print(f"⏭️  跳过：{item.name}（已存在）")
                continue

            # 确定套装类型
            set_name = None
            for s in ["青龙", "朱雀", "玄武", "白虎"]:
                if s in item.name:
                    set_name = s
                    break

            if not set_name:
                print(f"⚠️  跳过：{item.name}（无法识别套装类型）")
                continue

            # 获取积分价格
            credit_price = credit_prices.get(item.name, 15000)  # 默认15000积分

            # 创建商城商品
            shop_item = CreditShopItem(
                name=item.name,
                description=f"{item.description}\n\n🔮 {set_name}套装部件，收集完整套装可激活强大效果！",
                category=CreditShopCategory.TREASURE,
                item_id=item.id,
                credit_price=credit_price,
                total_stock=-1,  # 无限库存
                remaining_stock=-1,
                sold_count=0,
                purchase_limit_per_player=1,  # 每人限购1件
                daily_purchase_limit=-1,  # 不限制每日购买
                required_level=15,  # 需要15级
                required_vip_level=0,  # 不需要VIP
                discount_rate=1.0,  # 无折扣
                icon=set_icons[set_name],
                tags=set_tags[set_name],
                is_active=True,
                is_featured=True,  # 设为精选商品
                sort_order=100,  # 较高排序优先级
            )

            session.add(shop_item)
            added_count += 1
            print(f"✅ 添加：{item.name} - {credit_price}积分 - {set_icons[set_name]} {set_name}套装")

        await session.commit()
        print(f"\n🎉 成功添加 {added_count} 件神品装备到积分商城！")


async def show_credit_shop_summary():
    """显示积分商城商品摘要"""
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(CreditShopItem).where(
                CreditShopItem.category == CreditShopCategory.TREASURE
            ).order_by(CreditShopItem.credit_price.desc())
        )
        items = result.scalars().all()

        print("\n" + "=" * 60)
        print("📊 积分商城 - 四象套装一览")
        print("=" * 60)

        # 按套装分组
        sets = {"青龙": [], "朱雀": [], "玄武": [], "白虎": []}

        for item in items:
            for set_name in sets.keys():
                if set_name in item.name:
                    sets[set_name].append(item)
                    break

        for set_name, set_items in sets.items():
            if not set_items:
                continue

            total_credits = sum(item.credit_price for item in set_items)
            print(f"\n{set_items[0].icon} **{set_name}套装** ({len(set_items)}件) - 总价：{total_credits:,}积分")
            print("━" * 60)
            for item in set_items:
                print(f"  • {item.name:<12} - {item.credit_price:>6,}积分")

        print("\n" + "=" * 60)
        print("💡 提示：")
        print("  • 所有四象套装装备需要15级以上才能购买")
        print("  • 每件装备每人限购1件")
        print("  • 收集完整套装可激活2/4/6件套装效果")
        print("=" * 60 + "\n")


async def main():
    """主函数"""
    print("=" * 60)
    print("🏪 积分商城 - 四象套装初始化")
    print("=" * 60)

    print("\n📦 开始添加神品装备到积分商城...\n")

    await add_divine_equipment_to_credit_shop()
    await show_credit_shop_summary()

    print("\n💡 下一步：")
    print("1. 启动游戏测试积分商城")
    print("2. 使用 /积分商城 命令查看可兑换装备")
    print("3. 使用 /我的积分 命令查看当前积分\n")


if __name__ == "__main__":
    asyncio.run(main())
