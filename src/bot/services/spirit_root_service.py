"""灵根生成服务 - 凡人修仙传核心机制"""
import json
import random
from typing import List, Tuple

from sqlalchemy.ext.asyncio import AsyncSession

from bot.models import Player, SpiritRoot, SpiritRootElement


class SpiritRootService:
    """灵根相关服务类"""

    @staticmethod
    async def generate_spirit_root(db: AsyncSession, player: Player) -> SpiritRoot:
        """为玩家生成随机灵根

        Args:
            db: 数据库会话
            player: 玩家对象

        Returns:
            SpiritRoot: 生成的灵根对象
        """
        # 灵根数量概率：1根(5%) 2根(15%) 3根(30%) 4根(40%) 5根(10%)
        rand = random.random()
        if rand < 0.05:
            element_count = 1  # 天灵根 - 极稀有
        elif rand < 0.20:
            element_count = 2  # 双灵根 - 少见
        elif rand < 0.50:
            element_count = 3  # 三灵根 - 常见
        elif rand < 0.90:
            element_count = 4  # 四灵根（伪灵根）- 最常见
        else:
            element_count = 5  # 五灵根 - 杂灵根

        # 随机选择元素
        all_elements = [e.value for e in SpiritRootElement if e.value in ["金", "木", "水", "火", "土"]]
        selected = random.sample(all_elements, element_count)

        # 变异灵根判定（仅1-2根时有机会）
        is_mutant = False
        if element_count <= 2 and random.random() < 0.10:  # 10%概率
            is_mutant = True
            mutant_elements = [e.value for e in SpiritRootElement if e.value in ["风", "雷", "冰", "暗"]]
            selected = [random.choice(mutant_elements)]
            element_count = 1

        # 纯度：天灵根高纯度，伪灵根低纯度
        if element_count == 1:
            purity = random.randint(80, 100)
        elif element_count == 2:
            purity = random.randint(60, 85)
        elif element_count == 3:
            purity = random.randint(40, 65)
        else:
            purity = random.randint(20, 50)

        # 创建灵根对象
        spirit_root = SpiritRoot(
            player_id=player.id,
            elements=json.dumps(selected, ensure_ascii=False),  # 使用JSON格式存储
            purity=purity,
            is_mutant=is_mutant,
        )

        db.add(spirit_root)
        await db.commit()
        await db.refresh(spirit_root)

        return spirit_root

    @staticmethod
    def get_root_description(spirit_root: SpiritRoot) -> str:
        """获取灵根描述文本

        Args:
            spirit_root: 灵根对象

        Returns:
            str: 灵根描述文本
        """
        elements_list = spirit_root.element_list
        element_str = "、".join(elements_list)

        return f"{spirit_root.root_type}({element_str})"

    @staticmethod
    def get_root_comment(spirit_root: SpiritRoot) -> str:
        """根据灵根类型返回评价

        Args:
            spirit_root: 灵根对象

        Returns:
            str: 灵根评价文本
        """
        count = spirit_root.element_count

        if count == 1:
            if spirit_root.is_mutant:
                return "💫 变异灵根！修仙界万年难遇的奇才！未来前途不可限量！"
            else:
                return "🌟 天灵根！修仙界的绝世天才！各大宗门争抢的对象！"
        elif count == 2:
            return "✨ 双灵根！资质上佳，只要勤修苦练，结丹可期！"
        elif count == 3:
            return "⭐ 三灵根。资质中等，筑基有望，但结丹需要大机缘。"
        elif count == 4:
            return "💧 四灵根（伪灵根）。资质平庸，需要加倍努力。韩立就是这种灵根，最终成就惊人！"
        else:
            return "😔 五灵根（杂灵根）。修仙之路极为艰难，需要大毅力大机缘。"

    @staticmethod
    def format_spirit_root_info(spirit_root: SpiritRoot, show_comment: bool = True) -> str:
        """格式化灵根信息显示

        Args:
            spirit_root: 灵根对象
            show_comment: 是否显示评价

        Returns:
            str: 格式化的灵根信息
        """
        elements_list = spirit_root.element_list
        element_str = "、".join(elements_list)

        info = f"""🌈 灵根资质
━━━━━━━━━━━━━━━
✨ 灵根类型: {spirit_root.root_type}
📊 元素组成: {element_str}
💎 纯度: {spirit_root.purity}%
⚡ 修炼速度: {spirit_root.cultivation_speed_multiplier:.2f}x
🚀 突破加成: +{spirit_root.breakthrough_bonus*100:.1f}%
{'🌟 变异灵根！' if spirit_root.is_mutant else ''}
━━━━━━━━━━━━━━━"""

        if show_comment:
            info += f"\n\n{SpiritRootService.get_root_comment(spirit_root)}"

        return info
