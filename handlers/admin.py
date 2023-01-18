from aiogram.filters import Text
from aiogram import types, Dispatcher

from create_bot import bot
import keyboards as kb
from other import is_admin
from database import db_sqlite as db
from aiogram.fsm.context import FSMContext
from aiogram.filters.state import State, StatesGroup


class FSMAddPet(StatesGroup):
    photo = State()
    name = State()
    type = State()
    sex = State()
    age = State()
    sterilized = State()
    place = State()
    needs_temp_keeping = State()
    description = State()
    curator = State()


async def admin_add_pets_start(message: types.Message, state: FSMContext):
    if await is_admin(update=message):
        await state.set_state(FSMAddPet.photo)
        await bot.send_message(message.from_user.id, 'Вы находитесь в меню добавления питомца.\n<b>Чтобы отменить добавление <u>на любом этапе</u>, нажмите кнопку ниже</b>', reply_markup=kb.kb_cancel_edit)
        msg = await bot.send_message(message.from_user.id,
                               'Этап 1/10 ❎☑☑☑☑☑☑☑☑☑\n<b>Загрузите фото питомца.</b>. <i>Рекомендуется загружать горизонтальные фото.</i>')
        await state.update_data(msg=msg.message_id)

# async def prev(call: types.CallbackQuery, state: FSMContext):
#     if await is_admin(update=call):
#         await FSMAddPet.previous() if FSMAddPet.previous is not None else state.clear()
#         await call.message.delete()


async def admin_add_pets_photo(message: types.Message, state: FSMContext):
    data = await state.get_data()
    await bot.delete_message(chat_id=message.from_user.id, message_id=data['msg'])
    await message.delete()
    if await is_admin(update=message):
        if message.photo:
            await state.set_state(FSMAddPet.name)
            msg = await message.answer_photo(photo=message.photo[0].file_id, caption='Этап 2/10 ✅❎☑☑☑☑☑☑☑☑\n<b>Введите имя питомца.</b>')
            await state.update_data(photo=message.photo[0].file_id, msg=msg)
        else:
            msg = await bot.send_message(message.from_user.id, 'Вы загрузили не фотографию, попробуйте снова.')
        await state.update_data(msg=msg.message_id)


async def admin_add_pets_name(message: types.Message, state: FSMContext):
    data = await state.get_data()
    await bot.delete_message(chat_id=message.from_user.id, message_id=data['msg'])
    await message.delete()
    if await is_admin(update=message):
        if message.text and message.text.isalpha():
            await state.update_data(name=message.text.capitalize())
            await state.set_state(FSMAddPet.type)
            msg = await message.answer('Этап 3/10 ✅✅❎☑☑☑☑☑☑☑\n<b>Укажите тип животного.</b>', reply_markup=kb.pet_type_kb)
        else:
            msg = await message.answer('<b>Имя может состоять только из букв.</b>\n<i>Попробуйте снова.</i>')
        await state.update_data(msg=msg.message_id)


async def admin_add_pets_type(message: types.Message, state: FSMContext):
    data = await state.get_data()
    await bot.delete_message(chat_id=message.from_user.id, message_id=data['msg'])
    await message.delete()
    if await is_admin(update=message):
        if message.text and message.text in db.pet_type:
            await state.update_data(type=db.pet_type[message.text])
            await state.set_state(FSMAddPet.sex)
            msg = await message.answer('Этап 4/10 ✅✅✅❎☑☑☑☑☑☑\n<b>Укажите пол животного.</b>', reply_markup=kb.pet_sex_kb)
        else:
            msg = await message.answer('<b>Неверно указан тип животного.</b>\n<i>Воспользуйтесь кнопками ниже.</i>', reply_markup=kb.pet_type_kb)
        await state.update_data(msg=msg.message_id)


async def admin_add_pets_sex(message: types.Message, state: FSMContext):
    data = await state.get_data()
    await bot.delete_message(chat_id=message.from_user.id, message_id=data['msg'])
    await message.delete()
    if await is_admin(update=message):
        if message.text and message.text in db.pet_sex:
            await state.update_data(sex=db.pet_sex[message.text])
            await state.set_state(FSMAddPet.age)
            msg = await message.answer('Этап 5/10 ✅✅✅✅❎☑☑☑☑☑\n<b>Укажите примерный возраст животного.</b>\nК примеру, <i>2 года</i>, или <i>три месяца</i>.')
        else:
            msg = await message.answer('<b>Неверно указан пол животного.</b>\n<i>Воспользуйтесь кнопками ниже.</i>', reply_markup=kb.pet_sex_kb)
        await state.update_data(msg=msg.message_id)


async def admin_add_pets_age(message: types.Message, state: FSMContext):
    data = await state.get_data()
    await bot.delete_message(chat_id=message.from_user.id, message_id=data['msg'])
    await message.delete()
    if await is_admin(update=message):
        if message.text and len(message.text) > 5:
            await state.update_data(age=message.text)
            await state.set_state(FSMAddPet.sterilized)
            msg = await message.answer('Этап 6/10 ✅✅✅✅✅❎☑☑☑☑\n<b>Укажите, стерилизовано ли животное.</b>\n<i>Если вы не уверены, выберите "<u>нет</u>", данный пункт можно будет изменить позднее.</i>', reply_markup=kb.pet_bool_kb)
        else:
            msg = await message.answer('<b>Укажите возраст более понятно.</b>\nНе следует указывать просто цифру и использовать сокращения (должно быть более 5 символов). К примеру, <i>2 года</i>, или <i>три месяца</i>.')
        await state.update_data(msg=msg.message_id)


async def admin_add_pets_sterilized(message: types.Message, state: FSMContext):
    data = await state.get_data()
    await bot.delete_message(chat_id=message.from_user.id, message_id=data['msg'])
    await message.delete()
    if await is_admin(update=message):
        if message.text and message.text in db.bool_answer:
            await state.update_data(sterilized=db.bool_answer[message.text])
            await state.set_state(FSMAddPet.place)
            msg = await message.answer('Этап 7/10 ✅✅✅✅✅✅❎☑☑☑\n<b>Укажите место, где находится животное</b>', reply_markup= await kb.pet_place_kb())
        else:
            msg = await message.answer('<b>Неверный ответ.</b>\n<i>Чтобы указать, стерилизовано ли животное, воспользуйтесь кнопками ниже.</i>', reply_markup=kb.pet_bool_kb)
        await state.update_data(msg=msg.message_id)


async def admin_add_pets_place(message: types.Message, state: FSMContext):
    data = await state.get_data()
    await bot.delete_message(chat_id=message.from_user.id, message_id=data['msg'])
    await message.delete()
    if await is_admin(update=message) and message.text:
        await state.update_data(place=message.text)
        await state.set_state(FSMAddPet.needs_temp_keeping)
        msg = await message.answer('Этап 8/10 ✅✅✅✅✅✅✅❎☑☑\n<b>Необходима ли животному передержка?</b>\n<i>Если вы не уверены, нажмите "нет", данный пункт возможно изменить позднее</i>', reply_markup=kb.pet_bool_kb)
        await state.update_data(msg=msg.message_id)


async def admin_add_pets_needs_temp_keeping(message: types.Message, state: FSMContext):
    data = await state.get_data()
    await bot.delete_message(chat_id=message.from_user.id, message_id=data['msg'])
    await message.delete()
    if await is_admin(update=message):
        if message.text and message.text in db.bool_answer:
            await state.update_data(needs_temp_keeping=db.bool_answer[message.text])
            await state.set_state(FSMAddPet.description)
            msg = await message.answer('Этап 9/10 ✅✅✅✅✅✅✅✅❎☑\n<b>Введите описание.</b>\n<i> В связи с ограничениями Telegram, описание может быть до 900 символов.</i>')
        else:
            msg = await message.answer('<b>Неверный ответ.</b>\n<i>Чтобы указать, нужна ли животному передержка, воспользуйтесь кнопками ниже.</i>', reply_markup=kb.pet_bool_kb)
        await state.update_data(msg=msg.message_id)


async def admin_add_pets_description(message: types.Message, state: FSMContext):
    data = await state.get_data()
    await bot.delete_message(chat_id=message.from_user.id, message_id=data['msg'])
    await message.delete()
    if await is_admin(update=message):
        if message.text and len(message.text) < 901:
            await state.update_data(description=message.text)
            await state.set_state(FSMAddPet.curator)
            msg = await message.answer('Этап 10/10 ✅✅✅✅✅✅✅✅✅❎\n<b>Введите данные куратора(имя и телефон).</b>')
        else:
            msg = await message.answer(f'<i>В связи с ограничениями Telegram, длина описания может быть до <b>900</b> символов. Вы ввели <b>{len(message.text)}</b>. Пожалуйста, сократите описание.</i>')
        await state.update_data(msg=msg.message_id)


async def admin_add_pets_curator(message: types.Message, state: FSMContext):
    data = await state.get_data()
    await bot.delete_message(chat_id=message.from_user.id, message_id=data['msg'])
    await message.delete()
    if message.text and await is_admin(update=message):
        await state.update_data(curator=message.text, published_by_id=message.from_user.id)
        data = await state.get_data()
        db.add_pet(data=data)
        await state.clear()
        await message.answer('Все этапы пройдены ✅✅✅✅✅✅✅✅✅✅\n<b>Питомец добавлен в базу данных.</b>', reply_markup= await kb.main_buttons(is_admin=True))


# async def admin_add_pets_cancel(message: types.Message, state: FSMContext):
#     if await is_admin(update=message):
#         current_state = await state.get_state()
#         if current_state is None:
#             return
#         await state.clear()
#         await message.answer('Вы вышли из раздела добавления питомца', reply_markup= await kb.main_buttons(is_admin=True))


def register_handlers_admin(dp: Dispatcher):
    dp.message.register(admin_add_pets_start, Text(text=kb.admin_button_text))
    # dp.message.register(admin_add_pets_cancel, Text(text='Выйти', ignore_case=True))
    # dp.message.register(prev, Text(text=kb.back_to_prev), state='*')
    dp.message.register(admin_add_pets_photo, FSMAddPet.photo)
    dp.message.register(admin_add_pets_name, FSMAddPet.name)
    dp.message.register(admin_add_pets_type, FSMAddPet.type)
    dp.message.register(admin_add_pets_sex, FSMAddPet.sex)
    dp.message.register(admin_add_pets_age, FSMAddPet.age)
    dp.message.register(admin_add_pets_sterilized, FSMAddPet.sterilized)
    dp.message.register(admin_add_pets_place, FSMAddPet.place)
    dp.message.register(admin_add_pets_needs_temp_keeping, FSMAddPet.needs_temp_keeping)
    dp.message.register(admin_add_pets_description, FSMAddPet.description)
    dp.message.register(admin_add_pets_curator, FSMAddPet.curator)
    # dp.callback_query.register(prev, lambda call: call.data == 'prevFSM')
