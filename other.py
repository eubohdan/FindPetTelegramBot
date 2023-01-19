from aiogram.fsm.context import FSMContext
from aiogram import Dispatcher, types
from config_reader import config
from create_bot import bot
from database.db_sqlite import pets_names_list
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
    if message.text: #await is_admin_silent(userid=message.from_user.id):
        request = message.text.lower().strip()
        if len(request) >= 3:
            names = await pets_names_list()
            result_list = []
            for pet in names:
                if request in pet[0]:
                    result_list.append(pet)
            if result_list:
                if len(result_list) == 1:
                    await message.answer_photo(photo=result_list[0][2], caption=f'По вашему запросу найден только один питомец по имени <b>{result_list[0][0].capitalize()}</b>.', reply_markup=await kb.name_search_one_result(result_list=result_list))
                elif len(result_list) < 10:
                    msg = '\n'.join([f'{i + 1}. <i>{x[0].capitalize()}</i>' for i, x in enumerate(result_list)])
                    await message.answer_media_group(media=[types.InputMediaPhoto(media=item[2], caption=item[0].capitalize()) for item in result_list])
                    await message.answer(text='<b>Результаты поиска:</b>\n\n' + msg, reply_markup=await kb.name_search_results(result_list=result_list), disable_notification=True)
                else:
                    await message.answer(text='<b>Слишком много результатов поиска.</b>\n<i>Попробуйте задать другой запрос или воспользуйтесь каталогом.</i>', reply_markup=await kb.main_buttons(is_admin=await is_admin_silent(message.from_user.id)))
            else:
                await message.answer('<b>Питомцев с таким именем не найдено.</b>\n<i>Может, получится найти через каталог?</i>', reply_markup=await kb.main_buttons(is_admin=True))
        else:
            await message.answer('<b>Чтобы воспользоваться поиском, введите не менее трех букв.</b>\n <i>Либо же воспользуйтесь каталогом.</i>', reply_markup=await kb.main_buttons(is_admin=True))
    # else:
    #     await bot.send_message(message.from_user.id, 'Для работы с ботом воспользуйтесь кнопками.', reply_markup=await kb.main_buttons(is_admin=False))


def register_handlers(dp: Dispatcher):
    dp.callback_query.register(hide_message, lambda call: call.data == 'hide')
    dp.callback_query.register(in_dev, lambda call: call.data == 'in_dev')
    dp.callback_query.register(cancel_edit, lambda call: call.data == 'cancelFSM')
    dp.message.register(other_text)

