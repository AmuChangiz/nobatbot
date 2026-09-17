import asyncio
import logging
from typing import TYPE_CHECKING

from app.db.session import get_session_factory
from app.services import BroadcastService

if TYPE_CHECKING:
    from app.bot.bale_compat import Bot

logger = logging.getLogger(__name__)


class BroadcastWorker:
    @staticmethod
    async def run(
        bot: "Bot",
        message_text: str,
        admin_bale_user_id: int,
        admin_db_id: int | None,
    ) -> tuple[int, int]:
        session_factory = get_session_factory()
        async with session_factory() as session:
            broadcast_id = await BroadcastService.create_record(
                session, admin_id=admin_db_id, message_text=message_text
            )
            user_ids = await BroadcastService.get_all_user_bale_ids(session)
            await session.commit()

        sent = 0
        failed = 0
        for bale_user_id in user_ids:
            try:
                await bot.send_message(bale_user_id, message_text)
                sent += 1
            except Exception:
                failed += 1
                logger.warning("Broadcast failed for user %d", bale_user_id)
            if sent % 25 == 0:
                await asyncio.sleep(1)

        async with session_factory() as session:
            await BroadcastService.update_counts(session, broadcast_id, sent, failed)
            await session.commit()

        logger.info("Broadcast complete: sent=%d failed=%d", sent, failed)

        try:
            from app.bot.texts import fa as t

            await bot.send_message(
                admin_bale_user_id,
                t.BROADCAST_DONE.format(sent=sent, failed=failed),
            )
        except Exception:
            logger.exception("Failed to notify admin about broadcast completion")

        return sent, failed

    @staticmethod
    def schedule(
        bot: "Bot",
        message_text: str,
        admin_bale_user_id: int,
        admin_db_id: int | None,
    ) -> asyncio.Task:
        return asyncio.create_task(
            BroadcastWorker.run(bot, message_text, admin_bale_user_id, admin_db_id),
            name="broadcast_worker",
        )
