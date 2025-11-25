"""测试灵根生成概率分布"""
import asyncio
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

from bot.services.spirit_root_service import SpiritRootService
from bot.models import Player, SpiritRoot
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker


async def test_probability():
    """测试10000次灵根生成，统计概率分布"""

    # 创建临时内存数据库
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)

    # 创建表结构
    from bot.models.database import Base
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # 创建会话
    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    # 统计字典
    stats = {
        1: 0,  # 天灵根/异灵根
        2: 0,  # 双灵根
        3: 0,  # 三灵根
        4: 0,  # 伪灵根
        5: 0,  # 杂灵根
    }

    mutant_count = 0
    purity_sum = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}

    total = 10000

    print("🔮 开始测试灵根生成概率...")
    print(f"📊 测试次数: {total:,}")
    print()

    async with async_session() as session:
        for i in range(total):
            # 创建临时玩家
            player = Player(
                telegram_id=i,
                username=f"test_{i}",
                first_name=f"测试{i}",
                nickname=f"测试{i}",
            )
            session.add(player)
            await session.flush()

            # 生成灵根
            spirit_root = await SpiritRootService.generate_spirit_root(session, player)

            # 统计
            element_count = spirit_root.element_count
            stats[element_count] += 1
            purity_sum[element_count] += spirit_root.purity

            if spirit_root.is_mutant:
                mutant_count += 1

            # 清理（避免内存累积）
            if i % 1000 == 0 and i > 0:
                await session.commit()
                print(f"  已完成 {i:,} 次...")

    print()
    print("=" * 60)
    print("📊 灵根生成概率统计结果")
    print("=" * 60)
    print()

    # 显示结果
    type_names = {
        1: "天灵根/异灵根",
        2: "双灵根",
        3: "三灵根",
        4: "伪灵根（四灵根）",
        5: "杂灵根（五灵根）",
    }

    expected = {
        1: 5.0,
        2: 15.0,
        3: 30.0,
        4: 40.0,
        5: 10.0,
    }

    print("灵根类型 | 期望概率 | 实际数量 | 实际概率 | 平均纯度 | 偏差")
    print("-" * 80)

    for count in sorted(stats.keys()):
        actual_count = stats[count]
        actual_prob = (actual_count / total) * 100
        avg_purity = purity_sum[count] / actual_count if actual_count > 0 else 0
        deviation = actual_prob - expected[count]
        deviation_str = f"{deviation:+.2f}%"

        print(f"{type_names[count]:12} | {expected[count]:6.1f}% | {actual_count:8,} | "
              f"{actual_prob:7.2f}% | {avg_purity:7.1f}% | {deviation_str:>8}")

    print("-" * 80)
    print()

    # 变异灵根统计
    mutant_prob = (mutant_count / total) * 100
    print(f"💫 变异灵根统计:")
    print(f"   实际数量: {mutant_count:,}")
    print(f"   实际概率: {mutant_prob:.3f}%")
    print(f"   期望概率: 0.5% (天灵根5% × 变异率10%)")
    print()

    # 分析结果
    print("=" * 60)
    print("📈 分析结论")
    print("=" * 60)
    print()

    # 检查偏差
    max_deviation = max(abs((stats[i] / total) * 100 - expected[i]) for i in stats.keys())
    if max_deviation < 1.0:
        print("✅ 概率分布正常，最大偏差 < 1%")
    elif max_deviation < 2.0:
        print("✅ 概率分布可接受，最大偏差 < 2%")
    else:
        print(f"⚠️  概率分布异常，最大偏差 {max_deviation:.2f}%")

    print()

    # 玩家体验分析
    good_roots = stats[1] + stats[2]  # 天灵根 + 双灵根
    medium_roots = stats[3]  # 三灵根
    bad_roots = stats[4] + stats[5]  # 伪灵根 + 杂灵根

    print(f"🌟 优质灵根（天/双）: {good_roots:,} ({(good_roots/total)*100:.1f}%)")
    print(f"⭐ 普通灵根（三）:   {medium_roots:,} ({(medium_roots/total)*100:.1f}%)")
    print(f"💧 劣质灵根（伪/杂）: {bad_roots:,} ({(bad_roots/total)*100:.1f}%)")
    print()

    if bad_roots / total > 0.4:
        print("⚠️  注意: 超过40%的玩家会获得劣质灵根，可能影响游戏体验")

    print()


if __name__ == "__main__":
    asyncio.run(test_probability())
