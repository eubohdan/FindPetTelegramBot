from aiogram import Dispatcher, types
from aiogram.filters import Command

from other import is_admin
from create_bot import bot
import keyboards as kb


async def command_start_handler(message: types.Message):
    await message.delete()
    await bot.send_message(message.from_user.id, f"{['Доброй ночи', 'Доброе утро', 'Добрый день', 'Добрый вечер'][(message.date.hour + 3) % 24 // 6]}, <b>{message.from_user.first_name}!</b>\nВоспользуйтесь кнопками ниже.", reply_markup=kb.main_buttons_kb)


async def command_help_handler(message: types.Message):
    await message.delete()
    await bot.send_message(message.from_user.id, "Если Вы нашли какие-либо ошибки, у Вас возникли предложения либо дополнения, либо же у Вас имеются предложения сотрудничества, нажмите на кнопку ниже.", reply_markup=kb.kb_about_me)


async def set_commands_handler(message: types.Message):
    await message.delete()
    if await is_admin(message):
        await bot.set_my_commands(commands=[types.BotCommand(command="start", description="Перезапуск"), types.BotCommand(command="help", description="О боте")])
        await bot.set_my_commands(commands=[types.BotCommand(command="add", description="Добавить животное")], scope=types.BotCommandScopeAllChatAdministrators(type='all_chat_administrators'))
        await bot.send_message(message.from_user.id, '<b>Список команд успешно обновлён.</b>')


async def add_new_pet_handler(message: types.Message) -> None:
    await message.delete()
    if await is_admin(message):
        # Добавить начало машины состояний или вынести в конструктор клавы
        await bot.send_message(message.from_user.id, '<b>Загрузите фотографию питомца.</b>\n<u>Рекомендуется</u> загружать горизонтальное фото.')


def register_handlers(dp: Dispatcher):
    dp.message.register(command_start_handler, Command(commands=["start"]))
    dp.message.register(command_help_handler, Command(commands=["help"]))
    dp.message.register(set_commands_handler, Command(commands=["commands"]))
    dp.message.register(add_new_pet_handler, Command(commands=["add"]))
