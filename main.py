import logging
from aiogram import Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from create_bot import bot
from database import db_sqlite
from handlers import search, info, orgs, commands, admin
import other

dp = Dispatcher(storage=MemoryStorage())
logger = logging.getLogger(__name__)


def main() -> None:
    print('[INFO] The bot has been launched.')
    db_sqlite.start_db()
    dp.run_polling(bot)
    print('[INFO] The polling was stopped.')


commands.register_handlers(dp)
other.register_handlers(dp)
search.register_handlers(dp)
orgs.register_handlers(dp) #важно чтобы info был после orgs
info.register_handlers(dp)


if __name__ == "__main__":
    main()
