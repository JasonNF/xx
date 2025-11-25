"""主程序入口"""
import asyncio
import logging
from datetime import datetime

from telegram.ext import Application

from bot.config import settings
from bot.models import init_db, close_db
from bot.handlers import (
    start, cultivation, spirit_root, realm, skill, quest, battle,
    inventory, shop, sect, ranking, signin, rename,
    cultivation_method, alchemy, lifespan, refinery, market, core_quality,
    divine_sense, spirit_beast, formation, talisman, cave_dwelling, adventure, achievement, sect_war, arena, world_boss, credit_shop,
    sect_elder, sect_ranking
)

# 配置日志
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)


async def post_init(application: Application) -> None:
    """应用初始化后的回调"""
    logger.info("初始化数据库...")
    await init_db()
    logger.info("数据库初始化完成")

    # 启动调度器
    from bot.scheduler import start_scheduler
    start_scheduler()
    logger.info("调度器已启动")

    # TODO: 初始化Redis连接

    logger.info("Bot 启动成功！")


async def post_shutdown(application: Application) -> None:
    """应用关闭前的回调"""
    # 停止调度器
    from bot.scheduler import stop_scheduler
    stop_scheduler()
    logger.info("调度器已停止")

    logger.info("关闭数据库连接...")
    await close_db()
    logger.info("数据库连接已关闭")


def main():
    """主函数"""
    logger.info(f"正在启动 {settings.GAME_NAME} v{settings.GAME_VERSION}...")

    # 创建应用
    application = (
        Application.builder()
        .token(settings.BOT_TOKEN)
        .post_init(post_init)
        .post_shutdown(post_shutdown)
        .build()
    )

    # 注册处理器
    logger.info("注册命令处理器...")
    start.register_handlers(application)
    cultivation.register_handlers(application)
    spirit_root.register_handlers(application)
    realm.register_handlers(application)
    skill.register_handlers(application)
    quest.register_handlers(application)
    battle.register_handlers(application)
    inventory.register_handlers(application)
    shop.register_handlers(application)
    sect.register_handlers(application)
    sect_elder.register_handlers(application)
    sect_ranking.register_handlers(application)
    ranking.register_handlers(application)
    signin.register_handlers(application)
    rename.register_handlers(application)
    cultivation_method.register_handlers(application)
    alchemy.register_handlers(application)
    lifespan.register_handlers(application)
    refinery.register_handlers(application)
    market.register_handlers(application)
    core_quality.register_handlers(application)
    divine_sense.register_handlers(application)
    spirit_beast.register_handlers(application)
    formation.register_handlers(application)
    talisman.register_handlers(application)
    cave_dwelling.register_handlers(application)
    adventure.register_handlers(application)
    achievement.register_handlers(application)
    sect_war.register_handlers(application)
    arena.register_handlers(application)
    world_boss.register_handlers(application)
    credit_shop.register_handlers(application)

    logger.info("所有处理器注册完成")

    # 启动Bot
    logger.info("启动 Bot...")
    application.run_polling(
        allowed_updates=["message", "callback_query"],
        drop_pending_updates=True,
    )


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("收到退出信号，正在关闭...")
    except Exception as e:
        logger.error(f"运行出错: {e}", exc_info=True)
