from aiogram import types, Dispatcher
from aiogram.filters import Text
from aiogram.filters.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
import keyboards as kb
from database import db_sqlite as db
from create_bot import bot
import callback_factories as cf


async def orgs_menu(update: types.Update) -> None:
    try:
        if type(update) == types.Message:
            await update.delete()
        else:
            await update.message.delete()
    finally:
        await bot.send_message(update.from_user.id,
                               'В этом разделе вы можете найти информацию о представленных в боте приютах и волонтерских объединениях.',
                               reply_markup=await kb.kb_orgs('description'))


async def org_info(call: types.CallbackQuery, callback_data: cf.InfoCallbackFactory) -> None:
    '''Отправляет информацию из БД в чат о конкретной организации или о видах помощи для неё'''
    try:
        await call.message.delete()
    finally:
        if callback_data.action == 'description':
            keyboard = await kb.kb_org_socials(row_id=callback_data.value, user_id=call.from_user.id)
            await bot.send_photo(chat_id=call.from_user.id,
                                 photo=db.get_org_info(data_type='logo', row_id=callback_data.value),
                                 caption=db.get_org_info(data_type=callback_data.action, row_id=callback_data.value),
                                 reply_markup=keyboard)
        else:
            keyboard = await kb.kb_help_org(action=callback_data.action, row_id=callback_data.value,
                                            user_id=call.from_user.id)
            await bot.send_message(chat_id=call.from_user.id,
                                   text=db.get_org_info(data_type=callback_data.action, row_id=callback_data.value),
                                   reply_markup=keyboard)


class FSMEdit(StatesGroup):
    org_photo = State()
    org_descr = State()


async def org_info_edit_menu(call: types.CallbackQuery, state: FSMContext) -> None:
    '''Меню выбора, что редактировать, текст или фото'''
    _, rowid, status = call.data.split('|')
    if status == 'menu':
        kb_edit = await kb.kb_edit_org(rowid)
        msg = f'''<b>Что редактируем?</b>\n<i>Описание не может быть более 900 символов (сейчас {'описание отсутствует' if not call.message.caption else len(call.message.caption)}).</i>\n\n<code>{'Пожалуйста, добавьте описание.' if not call.message.caption else call.message.caption}</code>'''
        await bot.edit_message_caption(caption=msg, chat_id=call.message.chat.id, message_id=call.message.message_id,
                                       reply_markup=kb_edit)
    elif status == 'photo':
        await bot.edit_message_caption(
            caption='<b>Загрузите новую фотографию.</b>\n<i>Для отмены редактирования нажмите на кнопку ниже.</i>',
            chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=kb.kb_cancel_edit)
        await state.set_state(FSMEdit.org_photo)
    else:
        text = '<b>Введите новый текст.</b>\n<i>Для отмены редактирования нажмите на кнопку ниже.</i>'
        if call.message.caption:
            await bot.edit_message_caption(caption=text, chat_id=call.message.chat.id,
                                           message_id=call.message.message_id, reply_markup=kb.kb_cancel_edit)
        else:
            await bot.edit_message_text(text=text, chat_id=call.message.chat.id,
                                        message_id=call.message.message_id, reply_markup=kb.kb_cancel_edit)
        await state.set_state(FSMEdit.org_descr)
    await state.storage.set_data(bot, key=state.key, data={'row_id': rowid, 'data_type': status})


async def org_info_edit_photo(message: types.Message, state: FSMContext):
    try:
        photo_id = message.photo[0].file_id
        row_id = await state.storage.get_data(bot, key=state.key)
        db.set_org_info(data_type='logo', row_id=row_id['row_id'], value=photo_id)
        await message.answer('<b>Фотография успешно загружена.</b>', reply_markup=kb.main_buttons_kb)
        await state.clear()
    except(IndexError, TypeError):
        await message.answer('<b>Вы отправили не фотографию.</b>\n<i>Попробуйте снова.</i>',
                             reply_markup=kb.kb_cancel_edit)


async def org_info_edit_description(message: types.Message, state: FSMContext):
    try:
        if message.text is not None:
            data = await state.storage.get_data(bot, key=state.key)
            max_len = 900 if data['data_type'] == 'description' else 4000
            if len(message.html_text) <= max_len:
                db.set_org_info(data_type=data['data_type'], row_id=data['row_id'], value=message.html_text)
                await message.answer('<b>Описание изменено.</b>', reply_markup=kb.main_buttons_kb)
                await state.clear()
            else:
                await message.answer(
                    f'<b>Слишком длинное описание.</b>\n<i>Из-за ограничений Telegram, в тексте должно быть не более <b>{max_len}</b> символов. Ваш текст содержит <b>{len(message.html_text)}</b>. Введите более короткий текст.</i>',
                    reply_markup=kb.kb_cancel_edit)
        else:
            await message.answer(
                f'<b>Вы отправили не текст.</b>\n<i>Для изменения описания, необходимо отправить только текст, длина может составлять не более 900 символов. Попробуйте ещё раз или отмените редактирование.</i>',
                reply_markup=kb.kb_cancel_edit)
    except Exception as e:
        print(e)
        await message.answer(
            '<b>Произошла ошибка.</b>\n<i>Отмените редактирование или измените текст и попробуйте снова.</i>',
            reply_markup=kb.kb_cancel_edit)


def register_handlers(dp: Dispatcher):
    dp.message.register(orgs_menu, Text(text=kb.main_buttons_text[2]))
    dp.message.register(org_info_edit_photo, FSMEdit.org_photo)
    dp.message.register(org_info_edit_description, FSMEdit.org_descr)
    dp.callback_query.register(orgs_menu, lambda call: call.data == 'orgs')
    dp.callback_query.register(org_info_edit_menu, lambda call: call.data.startswith('orgedit'))
    dp.callback_query.register(org_info, cf.InfoCallbackFactory.filter())
