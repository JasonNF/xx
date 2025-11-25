"""境界突破修为需求配置"""
from typing import Dict, Tuple
from bot.models.player import RealmType


class RealmConfig:
    """境界配置类"""

    # 炼气期每层突破所需修为 (1-13层)
    QI_REFINING_EXP = {
        1: 10000,      # 0 → 10,000
        2: 15000,      # 10,000 → 25,000
        3: 22500,      # 25,000 → 47,500
        4: 33750,      # 47,500 → 81,250
        5: 50625,      # 81,250 → 131,875
        6: 75938,      # 131,875 → 207,813
        7: 113906,     # 207,813 → 321,719
        8: 170859,     # 321,719 → 492,578
        9: 256289,     # 492,578 → 748,867
        10: 384434,    # 748,867 → 1,133,301
        11: 576650,    # 1,133,301 → 1,709,951
        12: 864975,    # 1,709,951 → 2,574,926
        13: 1297463,   # 2,574,926 → 3,872,389 (炼气期圆满)
    }

    # 筑基期三阶段所需修为
    FOUNDATION_EXP = {
        0: 2000000,    # 初期: 3,872,389 → 5,872,389
        1: 5000000,    # 中期: 5,872,389 → 10,872,389
        2: 10000000,   # 后期: 10,872,389 → 20,872,389 (筑基圆满)
    }

    # 结丹期三阶段所需修为
    CORE_FORMATION_EXP = {
        0: 25000000,   # 初期: 20,872,389 → 45,872,389
        1: 40000000,   # 中期: 45,872,389 → 85,872,389
        2: 60000000,   # 后期: 85,872,389 → 145,872,389 (结丹圆满)
    }

    # 元婴期三阶段所需修为
    NASCENT_SOUL_EXP = {
        0: 100000000,  # 初期: 145,872,389 → 245,872,389
        1: 150000000,  # 中期: 245,872,389 → 395,872,389
        2: 250000000,  # 后期: 395,872,389 → 645,872,389 (元婴圆满)
    }

    # 化神期三阶段所需修为 (人界巅峰)
    # 已优化：降低10倍，避免后期修炼时间过长
    DEITY_TRANSFORMATION_EXP = {
        0: 50000000,   # 初期: 645,872,389 → 695,872,389 (50M)
        1: 80000000,   # 中期: 695,872,389 → 775,872,389 (80M)
        2: 120000000,  # 后期: 775,872,389 → 895,872,389 (120M，化神圆满)
    }

    @staticmethod
    def get_next_realm_exp(realm: RealmType, realm_level: int) -> int:
        """获取当前境界下一级所需修为

        Args:
            realm: 当前大境界
            realm_level: 当前小等级 (炼气期1-13，其他0-2)

        Returns:
            突破到下一级所需的修为值
        """
        if realm == RealmType.MORTAL:
            return RealmConfig.QI_REFINING_EXP[1]  # 凡人→炼气1层

        elif realm == RealmType.QI_REFINING:
            if realm_level >= 13:
                return RealmConfig.FOUNDATION_EXP[0]  # 炼气13→筑基初期
            return RealmConfig.QI_REFINING_EXP.get(realm_level + 1, 0)

        elif realm == RealmType.FOUNDATION:
            if realm_level >= 2:
                return RealmConfig.CORE_FORMATION_EXP[0]  # 筑基后期→结丹初期
            return RealmConfig.FOUNDATION_EXP.get(realm_level + 1, 0)

        elif realm == RealmType.CORE_FORMATION:
            if realm_level >= 2:
                return RealmConfig.NASCENT_SOUL_EXP[0]  # 结丹后期→元婴初期
            return RealmConfig.CORE_FORMATION_EXP.get(realm_level + 1, 0)

        elif realm == RealmType.NASCENT_SOUL:
            if realm_level >= 2:
                return RealmConfig.DEITY_TRANSFORMATION_EXP[0]  # 元婴后期→化神初期
            return RealmConfig.NASCENT_SOUL_EXP.get(realm_level + 1, 0)

        elif realm == RealmType.DEITY_TRANSFORMATION:
            if realm_level >= 2:
                return 0  # 化神后期圆满，无法再突破(需飞升)
            return RealmConfig.DEITY_TRANSFORMATION_EXP.get(realm_level + 1, 0)

        return 0

    @staticmethod
    def get_next_realm_info(realm: RealmType, realm_level: int) -> Tuple[RealmType, int]:
        """获取突破后的境界信息

        Args:
            realm: 当前大境界
            realm_level: 当前小等级

        Returns:
            (下一个大境界, 下一个小等级)
        """
        if realm == RealmType.MORTAL:
            return (RealmType.QI_REFINING, 1)

        elif realm == RealmType.QI_REFINING:
            if realm_level >= 13:
                return (RealmType.FOUNDATION, 0)  # 筑基初期
            return (RealmType.QI_REFINING, realm_level + 1)

        elif realm == RealmType.FOUNDATION:
            if realm_level >= 2:
                return (RealmType.CORE_FORMATION, 0)
            return (RealmType.FOUNDATION, realm_level + 1)

        elif realm == RealmType.CORE_FORMATION:
            if realm_level >= 2:
                return (RealmType.NASCENT_SOUL, 0)
            return (RealmType.CORE_FORMATION, realm_level + 1)

        elif realm == RealmType.NASCENT_SOUL:
            if realm_level >= 2:
                return (RealmType.DEITY_TRANSFORMATION, 0)
            return (RealmType.NASCENT_SOUL, realm_level + 1)

        elif realm == RealmType.DEITY_TRANSFORMATION:
            if realm_level >= 2:
                return (RealmType.DEITY_TRANSFORMATION, 2)  # 已是巅峰
            return (RealmType.DEITY_TRANSFORMATION, realm_level + 1)

        return (realm, realm_level)

    @staticmethod
    def get_cumulative_exp(realm: RealmType, realm_level: int) -> int:
        """获取当前境界的累计总修为 (用于对比计算)

        Args:
            realm: 当前大境界
            realm_level: 当前小等级

        Returns:
            从凡人修炼到当前境界所需的总修为
        """
        total = 0

        # 计算炼气期
        if realm.value in ["炼气期", "筑基期", "结丹期", "元婴期", "化神期"]:
            for level in range(1, 14):
                total += RealmConfig.QI_REFINING_EXP[level]

        if realm == RealmType.QI_REFINING:
            for level in range(1, realm_level + 1):
                total += RealmConfig.QI_REFINING_EXP[level]
            return total

        # 计算筑基期
        if realm.value in ["筑基期", "结丹期", "元婴期", "化神期"]:
            for stage in range(3):
                total += RealmConfig.FOUNDATION_EXP[stage]

        if realm == RealmType.FOUNDATION:
            for stage in range(realm_level + 1):
                total += RealmConfig.FOUNDATION_EXP[stage]
            return total

        # 计算结丹期
        if realm.value in ["结丹期", "元婴期", "化神期"]:
            for stage in range(3):
                total += RealmConfig.CORE_FORMATION_EXP[stage]

        if realm == RealmType.CORE_FORMATION:
            for stage in range(realm_level + 1):
                total += RealmConfig.CORE_FORMATION_EXP[stage]
            return total

        # 计算元婴期
        if realm.value in ["元婴期", "化神期"]:
            for stage in range(3):
                total += RealmConfig.NASCENT_SOUL_EXP[stage]

        if realm == RealmType.NASCENT_SOUL:
            for stage in range(realm_level + 1):
                total += RealmConfig.NASCENT_SOUL_EXP[stage]
            return total

        # 计算化神期
        if realm == RealmType.DEITY_TRANSFORMATION:
            for stage in range(3):
                total += RealmConfig.DEITY_TRANSFORMATION_EXP[stage]
            for stage in range(realm_level + 1):
                total += RealmConfig.DEITY_TRANSFORMATION_EXP[stage]
            return total

        return 0

    @staticmethod
    def get_breakthrough_base_chance(realm: RealmType, realm_level: int) -> float:
        """获取突破基础成功率

        Args:
            realm: 当前大境界
            realm_level: 当前小等级

        Returns:
            基础突破成功率 (0.0-1.0)
        """
        # 炼气期突破较容易
        if realm == RealmType.QI_REFINING:
            if realm_level < 7:
                return 0.85  # 炼气前期 85%
            elif realm_level < 13:
                return 0.75  # 炼气后期 75%
            else:
                return 0.60  # 炼气→筑基 60%

        # 筑基期及以上越来越难
        breakthrough_chances = {
            RealmType.FOUNDATION: {
                0: 0.70,  # 筑基初期→中期 70%
                1: 0.60,  # 筑基中期→后期 60%
                2: 0.50,  # 筑基后期→结丹 50%
            },
            RealmType.CORE_FORMATION: {
                0: 0.45,  # 结丹初期→中期 45%
                1: 0.40,  # 结丹中期→后期 40%
                2: 0.30,  # 结丹后期→元婴 30% (天劫)
            },
            RealmType.NASCENT_SOUL: {
                0: 0.25,  # 元婴初期→中期 25%
                1: 0.20,  # 元婴中期→后期 20%
                2: 0.15,  # 元婴后期→化神 15% (心魔劫)
            },
            RealmType.DEITY_TRANSFORMATION: {
                0: 0.15,  # 化神初期→中期 15%
                1: 0.10,  # 化神中期→后期 10%
                2: 0.05,  # 化神后期→飞升 5% (飞升劫，极难)
            },
        }

        return breakthrough_chances.get(realm, {}).get(realm_level, 0.7)
