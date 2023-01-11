from aiogram import types, Dispatcher
from aiogram.filters import Text
from create_bot import bot
from database import db_sqlite as db
import callback_factories as cf
import keyboards as kb


async def search_menu(update: types.Update) -> None:
    try:
        if type(update) == types.Message:
            await update.delete()
        else:
            await update.message.delete()
    finally:
        await bot.send_message(chat_id=update.from_user.id, text='Кого хотите посмотреть?', reply_markup= await kb.kb_search_menu())


async def make_long_post() -> str:
    pass


async def choice_pet(call: types.CallbackQuery, callback_data: cf.SearchCallbackFactory) -> None:
    '''Пагинация животных'''
    if callback_data.action == 'scrolling':
        row_id = await db.pets_list(pet_type=callback_data.pet_type)[callback_data.page]
        pet = await db.short_post(row_id)
        msg = f'''<b>{pet[1]}</b>\nПол: <b>{pet[2]}<\b>\nВозраст: <b>{pet[3]}<\b>'''
        bot.send_photo(chat_id=call.from_user.id, photo=pet[0], caption=msg, reply_markup=kb.scrolling_kb(row_id=row_id))





def register_handlers(dp: Dispatcher):
    dp.message.register(search_menu, Text(text=kb.main_buttons_text[0]))
