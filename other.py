from aiogram.fsm.context import FSMContext
from aiogram import Dispatcher, types
from config_reader import config
from create_bot import bot
import keyboards as kb


async def is_admin(update: types.Update | types.Message | types.CallbackQuery) -> bool | None:
    '''Принимает апдейт, если отправитель находится в админах группы, возвращает True, иначе отправляет сообщение'''
    admins = [item.user.id for item in await bot.get_chat_administrators(config.chat_id)]
    if update.from_user.id in admins:
        return True
    await bot.send_message(update.from_user.id, '<b>🚫 У вас нет доступа.</b>\nОбратитесь к администратору.',
                           reply_markup=await kb.main_buttons(is_admin=await is_admin_silent(userid=update.from_user.id)))


async def is_admin_silent(userid: int) -> bool:
    '''Принимает id пользователя и проверяет, находится ли пользователь в админах группы'''
    admins = [item.user.id for item in await bot.get_chat_administrators(config.chat_id)]
    return userid in admins


async def hide_message(update: types.Update) -> None:
    '''Обработчик кнопки скрыть/удалить в сообщениях'''
    try:
        await update.message.delete()
    except Exception as e:
        print(e) # !!!
        await update.answer('Бот не может скрыть сообщение, так как ему более 48 часов, но вы можете удалить его самостоятельно.',
                            reply_markup=await kb.main_buttons(is_admin=await is_admin_silent(userid=update.from_user.id)))


async def cancel_edit(call: types.CallbackQuery, state: FSMContext):
    '''Функция(хэндлер) для выхода из машины состояний'''
    try:
        await call.message.delete()
    finally:
        await state.clear()
        await call.message.answer('<b>Редактирование отменено.</b>\nИзменения не сохранены.', reply_markup=await kb.main_buttons(is_admin=await is_admin_silent(userid=call.from_user.id)))
        await call.answer()


async def in_dev(call: types.CallbackQuery):
    "Функция(хендлер)-заглушка для временно не работающих разделов"
    await call.answer(text='Раздел временно недоступен', show_alert=True)


async def other_text(message: types.Message):  # Удаляет всё что поступает со ввода и не соответствует тексту меню
    await message.delete()
    if is_admin_silent(userid=message.from_user.id):
        pass# тут - функция для поиска по именам
    else:
        await bot.send_message(message.from_user.id, 'Для работы с ботом воспользуйтесь кнопками.', reply_markup=await kb.main_buttons(is_admin=False))


def register_handlers(dp: Dispatcher):
    dp.callback_query.register(hide_message, lambda call: call.data == 'hide')
    dp.callback_query.register(in_dev, lambda call: call.data == 'in_dev')
    dp.callback_query.register(cancel_edit, lambda call: call.data == 'cancelFSM')
    dp.message.register(other_text)

