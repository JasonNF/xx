"""完整功法体系初始化脚本 - 43种功法"""
import asyncio
import sys
import json
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from bot.models.database import init_db, AsyncSessionLocal
from bot.models.player import CultivationMethod, RealmType
from sqlalchemy import select


async def create_mortal_methods():
    """创建人级功法（6种）"""
    async with AsyncSessionLocal() as session:
        methods = [
            # ========== 人级功法（6种） ==========
            {
                "name": "长春功",
                "description": "最普通的炼气期功法，易学难精，适合所有修士入门",
                "grade": "人级下品",
                "method_type": "通用",
                "cultivation_speed_bonus": 1.0,
                "attack_bonus": 0,
                "defense_bonus": 0,
                "hp_bonus": 0,
                "spiritual_power_bonus": 0,
                "required_realm": RealmType.QI_REFINING,
                "required_level": 1,
                "learning_cost": 0,  # 免费赠送
            },
            {
                "name": "铁布衫",
                "description": "外门基础体修功法，强化肉身防御",
                "grade": "人级下品",
                "method_type": "体修",
                "cultivation_speed_bonus": 0.9,
                "attack_bonus": 0,
                "defense_bonus": 10,
                "hp_bonus": 50,
                "spiritual_power_bonus": 0,
                "required_realm": RealmType.QI_REFINING,
                "required_level": 1,
                "learning_cost": 500,
            },
            {
                "name": "御剑基础",
                "description": "剑修入门功法，初窥御剑之道",
                "grade": "人级中品",
                "method_type": "剑修",
                "cultivation_speed_bonus": 0.95,
                "attack_bonus": 15,
                "defense_bonus": 0,
                "hp_bonus": 0,
                "spiritual_power_bonus": 0,
                "required_realm": RealmType.QI_REFINING,
                "required_level": 1,
                "learning_cost": 1000,
            },
            {
                "name": "五行诀",
                "description": "基础法修功法，调和五行灵气",
                "grade": "人级中品",
                "method_type": "法修",
                "cultivation_speed_bonus": 1.0,
                "attack_bonus": 0,
                "defense_bonus": 0,
                "hp_bonus": 0,
                "spiritual_power_bonus": 30,
                "required_realm": RealmType.QI_REFINING,
                "required_level": 1,
                "learning_cost": 1000,
            },
            {
                "name": "金刚功",
                "description": "进阶体修功法，如金刚般坚不可摧",
                "grade": "人级上品",
                "method_type": "体修",
                "cultivation_speed_bonus": 1.0,
                "attack_bonus": 0,
                "defense_bonus": 20,
                "hp_bonus": 100,
                "spiritual_power_bonus": 0,
                "required_realm": RealmType.QI_REFINING,
                "required_level": 3,
                "learning_cost": 3000,
            },
            {
                "name": "玄心诀",
                "description": "心法类通用功法，讲究心境修炼",
                "grade": "人级上品",
                "method_type": "通用",
                "cultivation_speed_bonus": 1.2,
                "attack_bonus": 3,
                "defense_bonus": 3,
                "hp_bonus": 30,
                "spiritual_power_bonus": 20,
                "required_realm": RealmType.QI_REFINING,
                "required_level": 5,
                "learning_cost": 5000,
            },
        ]

        for method_data in methods:
            method = CultivationMethod(**method_data)
            session.add(method)

        await session.commit()
        print(f"✅ 创建了 {len(methods)} 种人级功法")


async def create_yellow_methods():
    """创建黄级功法（8种）"""
    async with AsyncSessionLocal() as session:
        methods = [
            # ========== 黄级功法（8种） ==========
            {
                "name": "青木长生诀",
                "description": "木属性功法，蕴含生机，可加速伤势恢复",
                "grade": "黄级下品",
                "method_type": "法修",
                "cultivation_speed_bonus": 1.3,
                "attack_bonus": 0,
                "defense_bonus": 0,
                "hp_bonus": 50,
                "spiritual_power_bonus": 50,
                "required_realm": RealmType.QI_REFINING,
                "required_level": 7,
                "learning_cost": 8000,
                "required_spirit_root": json.dumps(["木"]),
            },
            {
                "name": "烈火诀",
                "description": "火属性功法，法术威力强大，攻击犀利",
                "grade": "黄级下品",
                "method_type": "法修",
                "cultivation_speed_bonus": 1.3,
                "attack_bonus": 10,
                "defense_bonus": 0,
                "hp_bonus": 0,
                "spiritual_power_bonus": 50,
                "required_realm": RealmType.QI_REFINING,
                "required_level": 7,
                "learning_cost": 8000,
                "required_spirit_root": json.dumps(["火"]),
            },
            {
                "name": "厚土诀",
                "description": "土属性功法，防御坚固如山岳",
                "grade": "黄级中品",
                "method_type": "体修",
                "cultivation_speed_bonus": 1.2,
                "attack_bonus": 0,
                "defense_bonus": 35,
                "hp_bonus": 200,
                "spiritual_power_bonus": 0,
                "required_realm": RealmType.QI_REFINING,
                "required_level": 9,
                "learning_cost": 12000,
                "required_spirit_root": json.dumps(["土"]),
            },
            {
                "name": "疾风诀",
                "description": "风属性功法，身轻如燕，速度惊人",
                "grade": "黄级中品",
                "method_type": "通用",
                "cultivation_speed_bonus": 1.4,
                "attack_bonus": 5,
                "defense_bonus": 0,
                "hp_bonus": 0,
                "spiritual_power_bonus": 30,
                "required_realm": RealmType.QI_REFINING,
                "required_level": 9,
                "learning_cost": 12000,
                "required_spirit_root": json.dumps(["风"]),
            },
            {
                "name": "寒冰诀",
                "description": "水属性功法，寒气逼人，可冻结敌人",
                "grade": "黄级中品",
                "method_type": "法修",
                "cultivation_speed_bonus": 1.35,
                "attack_bonus": 8,
                "defense_bonus": 5,
                "hp_bonus": 0,
                "spiritual_power_bonus": 60,
                "required_realm": RealmType.QI_REFINING,
                "required_level": 10,
                "learning_cost": 15000,
                "required_spirit_root": json.dumps(["水"]),
            },
            {
                "name": "流云剑诀",
                "description": "剑修功法，剑光如流云，轻灵飘逸",
                "grade": "黄级上品",
                "method_type": "剑修",
                "cultivation_speed_bonus": 1.3,
                "attack_bonus": 40,
                "defense_bonus": 0,
                "hp_bonus": 0,
                "spiritual_power_bonus": 30,
                "required_realm": RealmType.QI_REFINING,
                "required_level": 11,
                "learning_cost": 20000,
                "required_spirit_root": json.dumps(["金"]),
            },
            {
                "name": "紫霞功",
                "description": "名门正派功法，气息纯正，全面提升",
                "grade": "黄级上品",
                "method_type": "通用",
                "cultivation_speed_bonus": 1.5,
                "attack_bonus": 8,
                "defense_bonus": 8,
                "hp_bonus": 80,
                "spiritual_power_bonus": 50,
                "required_realm": RealmType.QI_REFINING,
                "required_level": 12,
                "learning_cost": 25000,
            },
            {
                "name": "北斗七星诀",
                "description": "观星悟道的法修功法，可借星辰之力",
                "grade": "黄级上品",
                "method_type": "法修",
                "cultivation_speed_bonus": 1.4,
                "attack_bonus": 0,
                "defense_bonus": 0,
                "hp_bonus": 0,
                "spiritual_power_bonus": 80,
                "required_realm": RealmType.FOUNDATION,
                "required_level": 1,
                "learning_cost": 25000,
            },
        ]

        for method_data in methods:
            method = CultivationMethod(**method_data)
            session.add(method)

        await session.commit()
        print(f"✅ 创建了 {len(methods)} 种黄级功法")


async def create_mystic_methods():
    """创建玄级功法（10种）"""
    async with AsyncSessionLocal() as session:
        methods = [
            # ========== 玄级功法（10种） ==========
            {
                "name": "天罡剑诀",
                "description": "剑修高阶功法，剑气纵横三千里",
                "grade": "玄级下品",
                "method_type": "剑修",
                "cultivation_speed_bonus": 1.5,
                "attack_bonus": 60,
                "defense_bonus": 0,
                "hp_bonus": 0,
                "spiritual_power_bonus": 60,
                "required_realm": RealmType.FOUNDATION,
                "required_level": 1,
                "learning_cost": 50000,
                "required_spirit_root": json.dumps(["金"]),
            },
            {
                "name": "不灭金身",
                "description": "体修顶级功法，肉身不灭不坏",
                "grade": "玄级下品",
                "method_type": "体修",
                "cultivation_speed_bonus": 1.4,
                "attack_bonus": 0,
                "defense_bonus": 50,
                "hp_bonus": 400,
                "spiritual_power_bonus": 0,
                "required_realm": RealmType.FOUNDATION,
                "required_level": 1,
                "learning_cost": 50000,
                "required_spirit_root": json.dumps(["土"]),
            },
            {
                "name": "九天玄雷诀",
                "description": "雷属性顶级功法，召唤九天神雷",
                "grade": "玄级中品",
                "method_type": "法修",
                "cultivation_speed_bonus": 1.6,
                "attack_bonus": 30,
                "defense_bonus": 0,
                "hp_bonus": 0,
                "spiritual_power_bonus": 120,
                "required_realm": RealmType.FOUNDATION,
                "required_level": 5,
                "learning_cost": 80000,
                "required_spirit_root": json.dumps(["风", "金"]),
            },
            {
                "name": "碧海潮生诀",
                "description": "水属性顶级功法，如大海般浩瀚",
                "grade": "玄级中品",
                "method_type": "法修",
                "cultivation_speed_bonus": 1.6,
                "attack_bonus": 20,
                "defense_bonus": 15,
                "hp_bonus": 100,
                "spiritual_power_bonus": 120,
                "required_realm": RealmType.FOUNDATION,
                "required_level": 5,
                "learning_cost": 80000,
                "required_spirit_root": json.dumps(["水"]),
            },
            {
                "name": "赤焰真诀",
                "description": "火土双属性功法，威力惊人",
                "grade": "玄级中品",
                "method_type": "法修",
                "cultivation_speed_bonus": 1.65,
                "attack_bonus": 35,
                "defense_bonus": 10,
                "hp_bonus": 50,
                "spiritual_power_bonus": 130,
                "required_realm": RealmType.FOUNDATION,
                "required_level": 8,
                "learning_cost": 100000,
                "required_spirit_root": json.dumps(["火", "土"]),
            },
            {
                "name": "太极玄清道",
                "description": "道家至高心法，阴阳调和，天人合一",
                "grade": "玄级上品",
                "method_type": "通用",
                "cultivation_speed_bonus": 1.8,
                "attack_bonus": 15,
                "defense_bonus": 15,
                "hp_bonus": 150,
                "spiritual_power_bonus": 100,
                "required_realm": RealmType.FOUNDATION,
                "required_level": 10,
                "learning_cost": 120000,
            },
            {
                "name": "飞虹剑诀",
                "description": "传说中的剑诀，剑光如虹贯日",
                "grade": "玄级上品",
                "method_type": "剑修",
                "cultivation_speed_bonus": 1.7,
                "attack_bonus": 80,
                "defense_bonus": 0,
                "hp_bonus": 0,
                "spiritual_power_bonus": 100,
                "required_realm": RealmType.CORE_FORMATION,
                "required_level": 1,
                "learning_cost": 150000,
                "required_spirit_root": json.dumps(["金"]),
            },
            {
                "name": "玄武真功",
                "description": "玄武神兽传承，防御无双，可反弹伤害",
                "grade": "玄级上品",
                "method_type": "体修",
                "cultivation_speed_bonus": 1.6,
                "attack_bonus": 10,
                "defense_bonus": 70,
                "hp_bonus": 600,
                "spiritual_power_bonus": 0,
                "required_realm": RealmType.CORE_FORMATION,
                "required_level": 1,
                "learning_cost": 150000,
                "required_spirit_root": json.dumps(["水", "土"]),
            },
            {
                "name": "青莲剑歌",
                "description": "青莲剑仙传承，剑意如莲花绽放",
                "grade": "玄级上品",
                "method_type": "剑修",
                "cultivation_speed_bonus": 1.75,
                "attack_bonus": 85,
                "defense_bonus": 0,
                "hp_bonus": 0,
                "spiritual_power_bonus": 110,
                "required_realm": RealmType.CORE_FORMATION,
                "required_level": 1,
                "learning_cost": 180000,
                "required_spirit_root": json.dumps(["木", "金"]),
            },
            {
                "name": "五行轮转诀",
                "description": "五行俱全者专修，五行循环生生不息",
                "grade": "玄级上品",
                "method_type": "法修",
                "cultivation_speed_bonus": 1.8,
                "attack_bonus": 20,
                "defense_bonus": 20,
                "hp_bonus": 100,
                "spiritual_power_bonus": 150,
                "required_realm": RealmType.CORE_FORMATION,
                "required_level": 1,
                "learning_cost": 200000,
                "required_spirit_root": json.dumps(["金", "木", "水", "火", "土"]),
            },
        ]

        for method_data in methods:
            method = CultivationMethod(**method_data)
            session.add(method)

        await session.commit()
        print(f"✅ 创建了 {len(methods)} 种玄级功法")


async def create_earth_methods():
    """创建地级功法（8种）"""
    async with AsyncSessionLocal() as session:
        methods = [
            # ========== 地级功法（8种） ==========
            {
                "name": "青元剑诀",
                "description": "玄剑门镇派绝学，可修炼至化神期，剑修顶级功法",
                "grade": "地级上品",
                "method_type": "剑修",
                "cultivation_speed_bonus": 1.9,
                "attack_bonus": 100,
                "defense_bonus": 0,
                "hp_bonus": 0,
                "spiritual_power_bonus": 150,
                "required_realm": RealmType.CORE_FORMATION,
                "required_level": 1,
                "learning_cost": 300000,
                "required_spirit_root": json.dumps(["金"]),
            },
            {
                "name": "龙象般若功",
                "description": "佛门至高体修功法，龙象之力，力拔山兮",
                "grade": "地级下品",
                "method_type": "体修",
                "cultivation_speed_bonus": 1.8,
                "attack_bonus": 50,
                "defense_bonus": 90,
                "hp_bonus": 800,
                "spiritual_power_bonus": 0,
                "required_realm": RealmType.CORE_FORMATION,
                "required_level": 1,
                "learning_cost": 250000,
            },
            {
                "name": "九转玄功",
                "description": "上古体修绝学，九转之后金身不坏",
                "grade": "地级中品",
                "method_type": "体修",
                "cultivation_speed_bonus": 1.9,
                "attack_bonus": 30,
                "defense_bonus": 100,
                "hp_bonus": 1000,
                "spiritual_power_bonus": 50,
                "required_realm": RealmType.CORE_FORMATION,
                "required_level": 5,
                "learning_cost": 400000,
            },
            {
                "name": "焚天煮海诀",
                "description": "法修至高绝学，五行法术登峰造极",
                "grade": "地级中品",
                "method_type": "法修",
                "cultivation_speed_bonus": 2.0,
                "attack_bonus": 40,
                "defense_bonus": 20,
                "hp_bonus": 200,
                "spiritual_power_bonus": 200,
                "required_realm": RealmType.CORE_FORMATION,
                "required_level": 5,
                "learning_cost": 400000,
            },
            {
                "name": "万剑归宗",
                "description": "剑修至高奥义，万剑听令，诛仙灭魔",
                "grade": "地级上品",
                "method_type": "剑修",
                "cultivation_speed_bonus": 2.1,
                "attack_bonus": 120,
                "defense_bonus": 10,
                "hp_bonus": 100,
                "spiritual_power_bonus": 180,
                "required_realm": RealmType.NASCENT_SOUL,
                "required_level": 1,
                "learning_cost": 500000,
                "required_spirit_root": json.dumps(["金"]),
            },
            {
                "name": "混元功",
                "description": "混元一气，天地同寿，全面提升的至高心法",
                "grade": "地级上品",
                "method_type": "通用",
                "cultivation_speed_bonus": 2.2,
                "attack_bonus": 50,
                "defense_bonus": 50,
                "hp_bonus": 400,
                "spiritual_power_bonus": 200,
                "required_realm": RealmType.NASCENT_SOUL,
                "required_level": 1,
                "learning_cost": 600000,
            },
            {
                "name": "神通变化诀",
                "description": "修炼神通之法，可习得各种大神通",
                "grade": "地级上品",
                "method_type": "法修",
                "cultivation_speed_bonus": 2.1,
                "attack_bonus": 60,
                "defense_bonus": 30,
                "hp_bonus": 300,
                "spiritual_power_bonus": 250,
                "required_realm": RealmType.NASCENT_SOUL,
                "required_level": 5,
                "learning_cost": 600000,
            },
            {
                "name": "北冥神功",
                "description": "魔道功法，可吸取他人修为，极端危险",
                "grade": "地级上品",
                "method_type": "特殊",
                "cultivation_speed_bonus": 2.0,
                "attack_bonus": 80,
                "defense_bonus": 0,
                "hp_bonus": 0,
                "spiritual_power_bonus": 300,
                "required_realm": RealmType.NASCENT_SOUL,
                "required_level": 1,
                "learning_cost": 800000,
            },
        ]

        for method_data in methods:
            method = CultivationMethod(**method_data)
            session.add(method)

        await session.commit()
        print(f"✅ 创建了 {len(methods)} 种地级功法")


async def create_heaven_methods():
    """创建天级功法（6种）- 积分商城"""
    async with AsyncSessionLocal() as session:
        methods = [
            # ========== 天级功法（6种）- 积分商城 ==========
            {
                "name": "大衍诀",
                "description": "推演天机的神秘功法，传说可预知未来，洞察天道",
                "grade": "天级",
                "method_type": "法修",
                "cultivation_speed_bonus": 2.3,
                "attack_bonus": 50,
                "defense_bonus": 50,
                "hp_bonus": 500,
                "spiritual_power_bonus": 300,
                "required_realm": RealmType.NASCENT_SOUL,
                "required_level": 1,
                "learning_cost": 0,  # 不在商店出售，仅积分商城
            },
            {
                "name": "混沌剑经",
                "description": "开天辟地之剑意，混沌初开，一剑破万法",
                "grade": "天级下品",
                "method_type": "剑修",
                "cultivation_speed_bonus": 2.4,
                "attack_bonus": 150,
                "defense_bonus": 20,
                "hp_bonus": 200,
                "spiritual_power_bonus": 250,
                "required_realm": RealmType.NASCENT_SOUL,
                "required_level": 8,
                "learning_cost": 0,
            },
            {
                "name": "不死不灭功",
                "description": "传说中的不死神功，肉身不灭，元神不朽",
                "grade": "天级中品",
                "method_type": "体修",
                "cultivation_speed_bonus": 2.3,
                "attack_bonus": 50,
                "defense_bonus": 150,
                "hp_bonus": 2000,
                "spiritual_power_bonus": 100,
                "required_realm": RealmType.NASCENT_SOUL,
                "required_level": 8,
                "learning_cost": 0,
            },
            {
                "name": "星辰变",
                "description": "吸收星辰之力，与天地同寿，与日月同辉",
                "grade": "天级中品",
                "method_type": "通用",
                "cultivation_speed_bonus": 2.5,
                "attack_bonus": 80,
                "defense_bonus": 80,
                "hp_bonus": 800,
                "spiritual_power_bonus": 300,
                "required_realm": RealmType.DEITY_TRANSFORMATION,
                "required_level": 1,
                "learning_cost": 0,
            },
            {
                "name": "吞天魔功",
                "description": "魔道至高绝学，吞噬万物，化为己用，霸道无比",
                "grade": "天级上品",
                "method_type": "特殊",
                "cultivation_speed_bonus": 2.6,
                "attack_bonus": 120,
                "defense_bonus": 40,
                "hp_bonus": 600,
                "spiritual_power_bonus": 400,
                "required_realm": RealmType.DEITY_TRANSFORMATION,
                "required_level": 1,
                "learning_cost": 0,
            },
            {
                "name": "造化金章",
                "description": "生死造化，夺天地之造化，掌生死之权柄",
                "grade": "天级上品",
                "method_type": "通用",
                "cultivation_speed_bonus": 2.6,
                "attack_bonus": 90,
                "defense_bonus": 90,
                "hp_bonus": 1000,
                "spiritual_power_bonus": 350,
                "required_realm": RealmType.DEITY_TRANSFORMATION,
                "required_level": 1,
                "learning_cost": 0,
            },
        ]

        for method_data in methods:
            method = CultivationMethod(**method_data)
            session.add(method)

        await session.commit()
        print(f"✅ 创建了 {len(methods)} 种天级功法（积分商城专属）")


async def create_special_methods():
    """创建特殊功法（5种）- 限定获取"""
    async with AsyncSessionLocal() as session:
        methods = [
            # ========== 特殊功法（5种）- 限定获取 ==========
            {
                "name": "青竹玄心诀",
                "description": "韩立所创功法，融合修仙界诸多绝学，辅助炼丹效果极佳",
                "grade": "神级",
                "method_type": "通用",
                "cultivation_speed_bonus": 3.0,
                "attack_bonus": 100,
                "defense_bonus": 100,
                "hp_bonus": 1500,
                "spiritual_power_bonus": 500,
                "required_realm": RealmType.DEITY_TRANSFORMATION,
                "required_level": 5,
                "learning_cost": 0,  # 任务获取
            },
            {
                "name": "天星双圣功",
                "description": "合欢宗至高双修功法，双人修炼速度翻倍",
                "grade": "神级",
                "method_type": "双修",
                "cultivation_speed_bonus": 2.8,
                "attack_bonus": 80,
                "defense_bonus": 80,
                "hp_bonus": 1000,
                "spiritual_power_bonus": 400,
                "required_realm": RealmType.NASCENT_SOUL,
                "required_level": 10,
                "learning_cost": 0,  # 秘境获取
            },
            {
                "name": "大圣真魔功",
                "description": "魔道六宗联手所创，修炼者魔性大增，战力惊人",
                "grade": "神级",
                "method_type": "魔修",
                "cultivation_speed_bonus": 2.9,
                "attack_bonus": 200,
                "defense_bonus": 50,
                "hp_bonus": 800,
                "spiritual_power_bonus": 350,
                "required_realm": RealmType.NASCENT_SOUL,
                "required_level": 10,
                "learning_cost": 0,  # 魔道传承
            },
            {
                "name": "梵圣真魔功",
                "description": "佛魔双修的禁忌功法，可在佛魔两种状态间转换",
                "grade": "神级",
                "method_type": "特殊",
                "cultivation_speed_bonus": 3.0,
                "attack_bonus": 150,
                "defense_bonus": 120,
                "hp_bonus": 1200,
                "spiritual_power_bonus": 450,
                "required_realm": RealmType.DEITY_TRANSFORMATION,
                "required_level": 10,
                "learning_cost": 0,  # 隐藏任务
            },
            {
                "name": "时空真解",
                "description": "掌握时空之力的究极功法，可减缓时间流速",
                "grade": "神级",
                "method_type": "法修",
                "cultivation_speed_bonus": 3.5,
                "attack_bonus": 120,
                "defense_bonus": 100,
                "hp_bonus": 1000,
                "spiritual_power_bonus": 500,
                "required_realm": RealmType.DEITY_TRANSFORMATION,
                "required_level": 15,
                "learning_cost": 0,  # 限时活动
            },
        ]

        for method_data in methods:
            method = CultivationMethod(**method_data)
            session.add(method)

        await session.commit()
        print(f"✅ 创建了 {len(methods)} 种特殊功法（限定获取）")


async def show_summary():
    """显示功法统计摘要"""
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(CultivationMethod))
        all_methods = result.scalars().all()

        print("\n" + "=" * 60)
        print("📊 功法体系统计")
        print("=" * 60)

        # 按品级统计
        grade_count = {}
        for method in all_methods:
            grade = method.grade.split("级")[0] + "级" if "级" in method.grade else method.grade
            grade_count[grade] = grade_count.get(grade, 0) + 1

        print("\n📖 按品级统计：")
        for grade, count in sorted(grade_count.items()):
            print(f"  • {grade}：{count} 种")

        # 按类型统计
        type_count = {}
        for method in all_methods:
            type_count[method.method_type] = type_count.get(method.method_type, 0) + 1

        print("\n🎯 按类型统计：")
        for method_type, count in sorted(type_count.items()):
            print(f"  • {method_type}：{count} 种")

        print(f"\n✅ 功法总数：{len(all_methods)} 种")
        print("=" * 60 + "\n")


async def main():
    """主函数"""
    print("=" * 60)
    print("📖 完整功法体系初始化")
    print("=" * 60)

    print("\n📚 开始创建功法数据...\n")

    await create_mortal_methods()      # 6种人级
    await create_yellow_methods()      # 8种黄级
    await create_mystic_methods()      # 10种玄级
    await create_earth_methods()       # 8种地级
    await create_heaven_methods()      # 6种天级
    await create_special_methods()     # 5种特殊

    await show_summary()

    print("\n💡 下一步：")
    print("1. 运行 init_credit_shop_cultivation.py 将天级功法添加到积分商城")
    print("2. 使用 /功法 命令查看可学功法")
    print("3. 使用 /修炼功法 <功法名> 学习功法\n")


if __name__ == "__main__":
    asyncio.run(main())
