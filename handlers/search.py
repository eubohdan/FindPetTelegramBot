from aiogram import types, Dispatcher
from aiogram.filters import Text
from aiogram.fsm.context import FSMContext

import other
from create_bot import bot
from database import db_sqlite as db
import callback_factories as cf
import keyboards as kb
from handlers.admin import FSMAddPet


async def search_menu(update: types.Update) -> None:
    try:
        if type(update) == types.Message:
            await update.delete()
        else:
            await update.message.delete()
    finally:
        await bot.send_message(chat_id=update.from_user.id, text='Кого хотите посмотреть?',
                               reply_markup=await kb.kb_search_menu())


async def choice_pet(call: types.CallbackQuery, callback_data: cf.SearchCallbackFactory, state: FSMContext) -> None:
    '''Пагинация животных'''
    if callback_data.action == 'scrolling':
        pets_list = await db.pets_list(pet_type=callback_data.pet_type)
        if pets_list:
            pet = await db.short_post(pets_list[callback_data.page % len(pets_list)])
            msg = f'''<b>{pet['name']}</b>\nПол: <b>{pet['sex']}</b>\nВозраст: <b>{pet['age']}</b>'''
            try:
                await call.message.delete()
            finally:
                await bot.send_photo(chat_id=call.from_user.id, photo=pet['photo'], caption=msg,
                                     reply_markup=await kb.scrolling_kb(page=callback_data.page % len(pets_list),
                                                                        pages=len(pets_list),
                                                                        pet_type=callback_data.pet_type))
        else:
            text = 'Результаты не найдены, выберите другой раздел'
            if call.message.text != text:
                await bot.edit_message_text(text, call.message.chat.id, call.message.message_id,
                                            reply_markup=await kb.kb_search_menu())
            else:
                await bot.answer_callback_query(callback_query_id=call.id)
    elif callback_data.action == 'pointer':
        await call.answer()
    elif callback_data.action == 'post':
        pets_list = await db.pets_list(pet_type=callback_data.pet_type)
        pet = await db.long_post(pets_list[callback_data.page % len(pets_list)])
        msg = f"<b>{pet['name']}</b>\nПол: <b>{pet['sex']}</b>\nВозраст: <b>{pet['age']}</b>\nСтерилизация: <b>{pet['sterilized']}</b>\nНаходится: <b>{pet['place']}</b>\n\n{pet['description']}"
        await bot.edit_message_caption(call.message.chat.id, call.message.message_id, caption=msg,
                                       reply_markup=await kb.pet_choosed_kb(pet_type=callback_data.pet_type,
                                                                            page=callback_data.page,
                                                                            is_admin=await other.is_admin_silent(
                                                                                userid=call.from_user.id)))
    elif callback_data.action == 'sure':
        msg = '<b>Подтвердите заявку</b>\nПри подтверждении данные Вашего профиля будут переданы куратору питомца.'
        try:
            await bot.edit_message_caption(call.message.chat.id, call.message.message_id, caption=msg,
                                           reply_markup=await kb.pet_choosed_sure(pet_type=callback_data.pet_type,
                                                                                  page=callback_data.page))
        except:
            # вынести в отдельную функцию?
            await call.message.answer('Сообщение устарело, начните сначала', reply_markup=types.InlineKeyboardMarkup(
                inline_keyboard=[types.InlineKeyboardButton(text='Начать сначала', callback_data='search')]))
    elif callback_data.action == 'request':
        pets_list = await db.pets_list(pet_type=callback_data.pet_type)
        pet = await db.long_post(pets_list[callback_data.page % len(pets_list)])
        try:
            chat_info = await bot.get_chat(call.from_user.id)
            if not chat_info.has_private_forwards:
                kb_write = types.InlineKeyboardMarkup(inline_keyboard=[
                    [types.InlineKeyboardButton(text='Связаться с пользователем', url=call.from_user.url)]])
                await bot.send_photo(chat_id=pet['admin'], photo=pet['photo'],
                                     caption=f"<b>Оставлена заявка на питомца {pet['name']}!\nИмя:</b>{call.message.chat.full_name}\n<b>Username:</b> {call.message.chat.username}",
                                     reply_markup=kb_write)
                await bot.edit_message_caption(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                               caption=f"<b>Спасибо! Ваша заявка передана волонтеру, а {pet['name']} с нетерпением ждёт встречи с Вами!</b>\nПожалуйста, проверьте настройки приватности, чтобы волонтёр смог с вами связаться.\nВ случае, если в ближайшее время этого не произойдёт, просим Вас связаться в дневное время с куратором самостоятельно:\n{pet['curator']}")
            else:
                await bot.edit_message_caption(call.message.chat.id, call.message.message_id,
                                               caption=f"В связи с установленными у Вас настройками приватности, бот не может передать волонтеру сведения о Вашем аккаунте. Просим Вас связаться с волонтёром самостоятельно:\n<b>{pet['curator']}</b>.")
        except Exception as error:
            print(error)
            await bot.edit_message_caption(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                           caption=f"По техническим причинам бот не может связаться с этим волонтером, но вы можете связаться с ним самостоятельно:\n{pet['curator']}")
    elif callback_data.action == 'delete_sure':
        if await other.is_admin(call):
            await bot.edit_message_caption(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                           caption=f"<b>Вы уверены?</b>\nУдаление отменить нельзя.",
                                           reply_markup=await kb.pet_delete_sure(pet_type=callback_data.pet_type,
                                                                                 page=callback_data.page))
    elif callback_data.action == 'delete':
        if await other.is_admin(call):
            pets_list = await db.pets_list(pet_type=callback_data.pet_type)
            pet = await db.short_post(row_id=pets_list[callback_data.page])
            image_link = pet['photo']
            msg = '<b>Запись удалена.</b>' if await db.delete_post(
                image_link) else '<b>Произошла ошибка.</b>\n<i>Попробуйте позже либо сообщите администратору.</i>'
            await bot.edit_message_caption(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                           caption=msg,
                                           reply_markup=await kb.pet_was_deleted(pet_type=callback_data.pet_type,
                                                                                 page=callback_data.page))
    elif callback_data.action == 'edit':
        if await other.is_admin(call):
            if not callback_data.additional:
                split_msg = call.message.html_text.split('\n\n')
                await bot.edit_message_caption(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                               caption=f"<b>Что необходимо изменить?</b>\n\n{split_msg[0]}\n\n<code>{split_msg[1]}</code>",
                                               reply_markup=await kb.what_to_edit(pet_type=callback_data.pet_type,
                                                                                  page=callback_data.page))
            else:
                pets_list = await db.pets_list(pet_type=callback_data.pet_type)
                row_id = pets_list[callback_data.page]
                await state.set_state(FSMAddPet.edit)
                await call.message.delete()
                first_msg = await call.message.answer('<b>Чтобы отменить редактирование, нажмите кнопку ниже</b>',
                                                      reply_markup=kb.kb_cancel_edit)
                texts_and_replies = {'img': ['Загрузите новую фотографию.', types.ReplyKeyboardRemove()],
                                     'description': ['Введите новое описание.', types.ReplyKeyboardRemove()],
                                     'age': ['Введите новый возраст.', types.ReplyKeyboardRemove()],
                                     'sterilized': ['Укажите, стерилизовано ли животное.', kb.pet_bool_kb],
                                     'place': ['Укажите новое место.', await kb.pet_place_kb()],
                                     'curator': ['Укажите новые данные куратора.', types.ReplyKeyboardRemove()],
                                     'needs_temp_keeping': ['Укажите, нужна ли животному передержка.', kb.pet_bool_kb]}
                msg = await call.message.answer_photo(photo=call.message.photo[0].file_id, caption=texts_and_replies[callback_data.additional][0],
                                                      reply_markup=texts_and_replies[callback_data.additional][1])
                await state.update_data(first_msg=first_msg.message_id, msg=msg.message_id, content_type=callback_data.additional, row_id=row_id, pet_type=callback_data.pet_type, page=callback_data.page, photo=call.message.photo[0].file_id)


def register_handlers(dp: Dispatcher):
    dp.message.register(search_menu, Text(text=kb.main_buttons_text[0]))
    dp.callback_query.register(search_menu, lambda call: call.data == 'search')
    dp.callback_query.register(choice_pet, cf.SearchCallbackFactory.filter())
