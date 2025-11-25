"""
修仙游戏 WebApp API 路由
集成到 PMSManageBot WebApp
"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from datetime import datetime, timedelta
import sqlite3

from app.webapp.auth import get_current_user
from app.webapp.schemas.user import UserAuth

router = APIRouter(prefix="/xiuxian", tags=["xiuxian"])

# 数据库路径
DB_PATH = "./data/data.db"


def get_db():
    """获取数据库连接"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


# ==================== 玩家信息 ====================

@router.get("/player/info")
async def get_player_info(current_user: UserAuth = Depends(get_current_user)):
    """获取玩家信息"""
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        SELECT * FROM xiuxian_players
        WHERE telegram_id = ?
    """, (current_user.tg_id,))

    player = cur.fetchone()
    conn.close()

    if not player:
        raise HTTPException(status_code=404, detail="角色未创建，请先在 Telegram 使用 /灵根测试 创建角色")

    return dict(player)


@router.post("/player/create")
async def create_player(current_user: UserAuth = Depends(get_current_user)):
    """创建玩家（如果不存在）"""
    import random

    conn = get_db()
    cur = conn.cursor()

    # 检查是否已存在
    cur.execute("SELECT id FROM xiuxian_players WHERE telegram_id = ?", (current_user.tg_id,))
    if cur.fetchone():
        conn.close()
        raise HTTPException(status_code=400, detail="角色已存在")

    # 创建角色
    comprehension = random.randint(8, 15)
    root_bone = random.randint(8, 15)

    cur.execute("""
        INSERT INTO xiuxian_players (
            telegram_id, name, comprehension, root_bone, spirit_stones
        ) VALUES (?, ?, ?, ?, 1000)
    """, (current_user.tg_id, current_user.username or f"修士{current_user.tg_id}", comprehension, root_bone))

    conn.commit()
    player_id = cur.lastrowid

    # 获取创建的角色
    cur.execute("SELECT * FROM xiuxian_players WHERE id = ?", (player_id,))
    player = cur.fetchone()
    conn.close()

    return dict(player)


# ==================== 修炼系统 ====================

@router.post("/cultivate/start")
async def start_cultivation(
    hours: int,
    current_user: UserAuth = Depends(get_current_user)
):
    """开始修炼"""
    if hours not in [2, 4, 8, 12]:
        raise HTTPException(status_code=400, detail="修炼时长只能是 2/4/8/12 小时")

    conn = get_db()
    cur = conn.cursor()

    # 获取玩家
    cur.execute("SELECT * FROM xiuxian_players WHERE telegram_id = ?", (current_user.tg_id,))
    player = cur.fetchone()

    if not player:
        conn.close()
        raise HTTPException(status_code=404, detail="角色未创建")

    if player['is_cultivating']:
        conn.close()
        raise HTTPException(status_code=400, detail="正在修炼中")

    # 开始修炼
    start_time = datetime.now()
    cur.execute("""
        UPDATE xiuxian_players
        SET is_cultivating = 1,
            cultivation_start_time = ?,
            cultivation_duration = ?
        WHERE telegram_id = ?
    """, (start_time.isoformat(), hours, current_user.tg_id))

    conn.commit()
    conn.close()

    return {
        "message": "开始修炼",
        "duration_hours": hours,
        "finish_time": (start_time + timedelta(hours=hours)).isoformat()
    }


@router.post("/cultivate/finish")
async def finish_cultivation(current_user: UserAuth = Depends(get_current_user)):
    """完成修炼"""
    import random

    conn = get_db()
    cur = conn.cursor()

    cur.execute("SELECT * FROM xiuxian_players WHERE telegram_id = ?", (current_user.tg_id,))
    player = cur.fetchone()

    if not player:
        conn.close()
        raise HTTPException(status_code=404, detail="角色未创建")

    if not player['is_cultivating']:
        conn.close()
        raise HTTPException(status_code=400, detail="未在修炼中")

    # 检查是否到时间
    start_time = datetime.fromisoformat(player['cultivation_start_time'])
    duration = player['cultivation_duration']
    finish_time = start_time + timedelta(hours=duration)

    if datetime.now() < finish_time:
        remaining = (finish_time - datetime.now()).total_seconds() / 60
        conn.close()
        raise HTTPException(
            status_code=400,
            detail=f"修炼未完成，还需 {int(remaining)} 分钟"
        )

    # 计算修为
    base_rate = 100
    comprehension_bonus = player['comprehension'] / 10
    root_bone_bonus = player['root_bone'] / 10
    cultivation_exp = int(base_rate * duration * (1 + comprehension_bonus + root_bone_bonus))

    # 随机事件
    event = ""
    rand = random.random()
    if rand < 0.1:  # 10% 顿悟
        cultivation_exp = int(cultivation_exp * 1.5)
        event = "顿悟"
    elif rand > 0.95:  # 5% 走火入魔
        cultivation_exp = int(cultivation_exp * 0.7)
        event = "走火入魔"

    # 更新玩家
    new_exp = player['cultivation_exp'] + cultivation_exp
    cur.execute("""
        UPDATE xiuxian_players
        SET is_cultivating = 0,
            cultivation_start_time = NULL,
            cultivation_duration = NULL,
            cultivation_exp = ?
        WHERE telegram_id = ?
    """, (new_exp, current_user.tg_id))

    conn.commit()
    conn.close()

    return {
        "message": "修炼完成",
        "exp_gained": cultivation_exp,
        "total_exp": new_exp,
        "event": event
    }


# ==================== 突破系统 ====================

@router.post("/breakthrough")
async def breakthrough(current_user: UserAuth = Depends(get_current_user)):
    """境界突破"""
    import random

    conn = get_db()
    cur = conn.cursor()

    cur.execute("SELECT * FROM xiuxian_players WHERE telegram_id = ?", (current_user.tg_id,))
    player = cur.fetchone()

    if not player:
        conn.close()
        raise HTTPException(status_code=404, detail="角色未创建")

    # 境界配置
    realms = [
        {"name": "凡人", "max_level": 0, "exp_per_level": 0},
        {"name": "练气", "max_level": 9, "exp_per_level": 1000},
        {"name": "筑基", "max_level": 9, "exp_per_level": 5000},
        {"name": "金丹", "max_level": 9, "exp_per_level": 20000},
        {"name": "元婴", "max_level": 9, "exp_per_level": 50000},
        {"name": "化神", "max_level": 9, "exp_per_level": 100000},
        {"name": "炼虚", "max_level": 9, "exp_per_level": 200000},
        {"name": "合体", "max_level": 9, "exp_per_level": 400000},
        {"name": "大乘", "max_level": 9, "exp_per_level": 800000},
        {"name": "渡劫", "max_level": 9, "exp_per_level": 1600000},
    ]

    current_realm = player['realm']
    current_level = player['realm_level']

    # 找到当前境界
    realm_idx = next((i for i, r in enumerate(realms) if r['name'] == current_realm), 0)

    if realm_idx >= len(realms) - 1 and current_level >= 9:
        conn.close()
        raise HTTPException(status_code=400, detail="已达最高境界")

    # 检查修为是否足够
    if current_level < 9:
        # 境界内突破
        required_exp = realms[realm_idx]['exp_per_level']
    else:
        # 大境界突破
        required_exp = realms[realm_idx + 1]['exp_per_level']

    if player['cultivation_exp'] < required_exp:
        conn.close()
        raise HTTPException(
            status_code=400,
            detail=f"修为不足，需要 {required_exp}，当前 {player['cultivation_exp']}"
        )

    # 计算成功率
    base_chance = 0.70
    comprehension_bonus = player['comprehension'] / 100
    success_rate = min(0.95, base_chance + comprehension_bonus)

    if random.random() < success_rate:
        # 突破成功
        if current_level < 9:
            new_level = current_level + 1
            new_realm = current_realm
        else:
            new_level = 1
            new_realm = realms[realm_idx + 1]['name']

        cur.execute("""
            UPDATE xiuxian_players
            SET realm = ?,
                realm_level = ?,
                cultivation_exp = cultivation_exp - ?
            WHERE telegram_id = ?
        """, (new_realm, new_level, required_exp, current_user.tg_id))

        conn.commit()
        conn.close()

        return {
            "success": True,
            "message": f"突破成功！{current_realm}{current_level}层 → {new_realm}{new_level}层",
            "new_realm": new_realm,
            "new_level": new_level
        }
    else:
        # 突破失败
        lost_exp = int(required_exp * 0.3)
        cur.execute("""
            UPDATE xiuxian_players
            SET cultivation_exp = cultivation_exp - ?
            WHERE telegram_id = ?
        """, (lost_exp, current_user.tg_id))

        conn.commit()
        conn.close()

        return {
            "success": False,
            "message": f"突破失败，损失 {lost_exp} 修为",
            "lost_exp": lost_exp
        }


# ==================== 战斗系统 ====================

@router.get("/monsters")
async def get_monsters(current_user: UserAuth = Depends(get_current_user)):
    """获取怪物列表"""
    conn = get_db()
    cur = conn.cursor()

    cur.execute("SELECT * FROM xiuxian_monsters ORDER BY level")
    monsters = [dict(row) for row in cur.fetchall()]
    conn.close()

    return monsters


@router.post("/battle/{monster_id}")
async def battle_monster(
    monster_id: int,
    current_user: UserAuth = Depends(get_current_user)
):
    """战斗"""
    import random

    conn = get_db()
    cur = conn.cursor()

    # 获取玩家
    cur.execute("SELECT * FROM xiuxian_players WHERE telegram_id = ?", (current_user.tg_id,))
    player = cur.fetchone()

    if not player:
        conn.close()
        raise HTTPException(status_code=404, detail="角色未创建")

    # 检查战斗冷却
    if player['last_battle_time']:
        last_battle = datetime.fromisoformat(player['last_battle_time'])
        cooldown = timedelta(minutes=5)
        if datetime.now() - last_battle < cooldown:
            remaining = (cooldown - (datetime.now() - last_battle)).total_seconds() / 60
            conn.close()
            raise HTTPException(
                status_code=400,
                detail=f"战斗冷却中，还需 {int(remaining)} 分钟"
            )

    # 获取怪物
    cur.execute("SELECT * FROM xiuxian_monsters WHERE id = ?", (monster_id,))
    monster = cur.fetchone()

    if not monster:
        conn.close()
        raise HTTPException(status_code=404, detail="怪物不存在")

    # 计算战力
    player_power = player['attack'] + player['defense'] + player['comprehension'] * 10
    monster_power = monster['attack'] + monster['defense']

    # 战斗
    if random.random() < (player_power / (player_power + monster_power)):
        # 胜利
        exp_gained = monster['exp_reward']
        stones_gained = monster['spirit_stones_reward']

        cur.execute("""
            UPDATE xiuxian_players
            SET cultivation_exp = cultivation_exp + ?,
                spirit_stones = spirit_stones + ?,
                last_battle_time = ?
            WHERE telegram_id = ?
        """, (exp_gained, stones_gained, datetime.now().isoformat(), current_user.tg_id))

        # 记录战斗
        cur.execute("""
            INSERT INTO xiuxian_battle_records (
                player_id, monster_id, result, exp_gained, stones_gained
            ) VALUES (?, ?, 'win', ?, ?)
        """, (player['id'], monster_id, exp_gained, stones_gained))

        conn.commit()
        conn.close()

        return {
            "success": True,
            "message": f"战胜 {monster['name']}",
            "exp_gained": exp_gained,
            "stones_gained": stones_gained
        }
    else:
        # 失败
        hp_lost = int(player['hp'] * 0.2)

        cur.execute("""
            UPDATE xiuxian_players
            SET hp = hp - ?,
                last_battle_time = ?
            WHERE telegram_id = ?
        """, (hp_lost, datetime.now().isoformat(), current_user.tg_id))

        # 记录战斗
        cur.execute("""
            INSERT INTO xiuxian_battle_records (
                player_id, monster_id, result, exp_gained, stones_gained
            ) VALUES (?, ?, 'lose', 0, 0)
        """, (player['id'], monster_id))

        conn.commit()
        conn.close()

        return {
            "success": False,
            "message": f"被 {monster['name']} 击败",
            "hp_lost": hp_lost
        }


# ==================== 签到系统 ====================

@router.post("/sign")
async def daily_sign(current_user: UserAuth = Depends(get_current_user)):
    """每日签到"""
    import random

    conn = get_db()
    cur = conn.cursor()

    cur.execute("SELECT * FROM xiuxian_players WHERE telegram_id = ?", (current_user.tg_id,))
    player = cur.fetchone()

    if not player:
        conn.close()
        raise HTTPException(status_code=404, detail="角色未创建")

    # 检查是否已签到
    if player['last_sign_time']:
        last_sign = datetime.fromisoformat(player['last_sign_time']).date()
        if last_sign == datetime.now().date():
            conn.close()
            raise HTTPException(status_code=400, detail="今日已签到")

    # 签到奖励
    base_reward = 100
    bonus = random.randint(0, 50)
    total_reward = base_reward + bonus

    cur.execute("""
        UPDATE xiuxian_players
        SET spirit_stones = spirit_stones + ?,
            last_sign_time = ?
        WHERE telegram_id = ?
    """, (total_reward, datetime.now().isoformat(), current_user.tg_id))

    conn.commit()
    conn.close()

    return {
        "message": "签到成功",
        "reward": total_reward,
        "base": base_reward,
        "bonus": bonus
    }


# ==================== 积分兑换 ====================

@router.post("/exchange")
async def exchange_credits(
    credits_amount: int,
    current_user: UserAuth = Depends(get_current_user)
):
    """积分兑换灵石"""
    EXCHANGE_RATE = 0.1
    DAILY_LIMIT = 10000
    MIN_EXCHANGE = 100

    if credits_amount < MIN_EXCHANGE:
        raise HTTPException(status_code=400, detail=f"最小兑换 {MIN_EXCHANGE} 积分")

    conn = get_db()
    cur = conn.cursor()

    # 检查用户积分
    cur.execute("SELECT credits FROM user WHERE tg_id = ?", (current_user.tg_id,))
    user = cur.fetchone()

    if not user or user['credits'] < credits_amount:
        conn.close()
        raise HTTPException(status_code=400, detail="积分不足")

    # 检查每日限额
    cur.execute("""
        SELECT COALESCE(SUM(credits_amount), 0) as total
        FROM xiuxian_exchange_records
        WHERE telegram_id = ? AND DATE(created_at) = DATE('now')
    """, (current_user.tg_id,))

    today_total = cur.fetchone()['total']
    if today_total + credits_amount > DAILY_LIMIT:
        conn.close()
        raise HTTPException(
            status_code=400,
            detail=f"超过每日限额，今日已兑换 {today_total}/{DAILY_LIMIT}"
        )

    # 计算灵石
    spirit_stones = int(credits_amount * EXCHANGE_RATE)

    # 扣除积分
    cur.execute("""
        UPDATE user SET credits = credits - ? WHERE tg_id = ?
    """, (credits_amount, current_user.tg_id))

    # 增加灵石
    cur.execute("""
        UPDATE xiuxian_players
        SET spirit_stones = spirit_stones + ?
        WHERE telegram_id = ?
    """, (spirit_stones, current_user.tg_id))

    # 记录兑换
    cur.execute("""
        INSERT INTO xiuxian_exchange_records (
            telegram_id, credits_amount, spirit_stones_gained, exchange_rate
        ) VALUES (?, ?, ?, ?)
    """, (current_user.tg_id, credits_amount, spirit_stones, EXCHANGE_RATE))

    conn.commit()
    conn.close()

    return {
        "message": "兑换成功",
        "credits_used": credits_amount,
        "stones_gained": spirit_stones
    }


# ==================== 排行榜 ====================

@router.get("/rankings/power")
async def get_power_rankings(limit: int = 50):
    """战力排行榜"""
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        SELECT
            name,
            realm,
            realm_level,
            cultivation_exp,
            (attack + defense + comprehension * 10) as power
        FROM xiuxian_players
        ORDER BY power DESC
        LIMIT ?
    """, (limit,))

    rankings = [dict(row) for row in cur.fetchall()]
    conn.close()

    return rankings


@router.get("/rankings/realm")
async def get_realm_rankings(limit: int = 50):
    """境界排行榜"""
    conn = get_db()
    cur = conn.cursor()

    # 境界排序
    realm_order = {
        "凡人": 0, "练气": 1, "筑基": 2, "金丹": 3, "元婴": 4,
        "化神": 5, "炼虚": 6, "合体": 7, "大乘": 8, "渡劫": 9
    }

    cur.execute("""
        SELECT name, realm, realm_level, cultivation_exp
        FROM xiuxian_players
        ORDER BY
            CASE realm
                WHEN '渡劫' THEN 9
                WHEN '大乘' THEN 8
                WHEN '合体' THEN 7
                WHEN '炼虚' THEN 6
                WHEN '化神' THEN 5
                WHEN '元婴' THEN 4
                WHEN '金丹' THEN 3
                WHEN '筑基' THEN 2
                WHEN '练气' THEN 1
                ELSE 0
            END DESC,
            realm_level DESC,
            cultivation_exp DESC
        LIMIT ?
    """, (limit,))

    rankings = [dict(row) for row in cur.fetchall()]
    conn.close()

    return rankings
