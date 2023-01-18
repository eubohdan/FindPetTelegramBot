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
    edit = State()


async def admin_edit_pet(message: types.Message = None, state: FSMContext = FSMAddPet.edit):
    try:
        await message.delete()
    finally:
        data = await state.get_data()
        circumstances = {'img': [message.photo, '<b>Вы загрузили не фотографию.</b>\n<i>Попробуйте снова.</i>'],
                         'description': [message.text and len(message.text) < 900, '<b>Имя может состоять только из букв.</b>\n<i>Попробуйте снова.</i>'],
                         'age': [message.text and len(message.text) > 5, '<b>Укажите возраст более понятно.</b>\nНе следует указывать просто цифру и использовать сокращения (должно быть более 5 символов). К примеру, <i>2 года</i> или <i>три месяца</i>.'],
                         'sterilized': [message.text and message.text in db.bool_answer, '<b>Неверный ответ.</b>\n<i>Чтобы указать, стерилизовано ли животное, воспользуйтесь кнопками ниже.</i>'],
                         'place': [message.text, 'Вы не ввели текст. Попробуйте снова'],
                         'curator': [message.text, 'Вы не ввели текст. Попробуйте снова'],
                         'needs_temp_keeping': [message.text and message.text in db.bool_answer, '<b>Неверный ответ.</b>\n<i>Чтобы указать, нужна ли животному передержка, воспользуйтесь кнопками ниже.</i>']}
        if circumstances[data['content_type']][0]:
            if db.edit_pet(image_link=data['image_link'], content_type=data['content_type'], data=message.text if data['content_type'] != 'img' else message.photo[0].file_id):
                await message.answer('<b>Данные успешно изменены.</b>', reply_markup=await kb.main_buttons(is_admin=True))
            else:
                await message.answer('<b>Что-то пошло не так. Пожалуйста, свяжитесь с администратором.</b>', reply_markup=kb.kb_about_me)
            await bot.delete_message(chat_id=message.from_user.id, message_id=data['first_msg'])
            await bot.delete_message(chat_id=message.from_user.id, message_id=data['msg'])
            await state.clear()
        else:
            await message.answer(text=circumstances[data['content_type']][1], reply_markup=message.reply_markup)


async def admin_add_pets_start(message: types.Message, state: FSMContext):
    try:
        await message.delete()
    finally:
        if await is_admin(update=message):
            await state.set_state(FSMAddPet.photo)
            first_msg = await bot.send_message(message.from_user.id, 'Вы находитесь в меню добавления питомца.\n<b>Чтобы отменить добавление <u>на любом этапе</u>, нажмите кнопку ниже</b>', reply_markup=kb.kb_cancel_edit)
            msg = await bot.send_message(message.from_user.id,
                                   'Этап 1/10 ❎☑☑☑☑☑☑☑☑☑\n<b>Загрузите фото питомца.</b>. <i>Рекомендуется загружать горизонтальные фото.</i>')
            await state.update_data(msg=msg.message_id, first_msg=first_msg.message_id)


async def admin_add_pets_photo(message: types.Message, state: FSMContext):
    try:
        data = await state.get_data()
        await bot.delete_message(chat_id=message.from_user.id, message_id=data['msg'])
        await message.delete()
    finally:
        if await is_admin(update=message):
            if message.photo:
                await state.set_state(FSMAddPet.name)
                msg = await message.answer_photo(photo=message.photo[0].file_id, caption='Этап 2/10 ✅❎☑☑☑☑☑☑☑☑\n<b>Введите имя питомца.</b>')
                await state.update_data(photo=message.photo[0].file_id, msg=msg)
            else:
                msg = await bot.send_message(message.from_user.id, '<b>Вы загрузили не фотографию.</b>\n<i>Попробуйте снова.</i>')
            await state.update_data(msg=msg.message_id)


async def admin_add_pets_name(message: types.Message, state: FSMContext):
    try:
        data = await state.get_data()
        await bot.delete_message(chat_id=message.from_user.id, message_id=data['msg'])
        await message.delete()
    finally:
        if await is_admin(update=message):
            if message.text and len(message.text) < 30 and message.text.isalpha():
                await state.update_data(name=message.text.capitalize())
                await state.set_state(FSMAddPet.type)
                msg = await message.answer('Этап 3/10 ✅✅❎☑☑☑☑☑☑☑\n<b>Укажите тип животного.</b>', reply_markup=kb.pet_type_kb)
            else:
                msg = await message.answer('<b>Имя может состоять только из букв.</b>\n<i>Попробуйте снова.</i>')
            await state.update_data(msg=msg.message_id)


async def admin_add_pets_type(message: types.Message, state: FSMContext):
    try:
        data = await state.get_data()
        await bot.delete_message(chat_id=message.from_user.id, message_id=data['msg'])
        await message.delete()
    finally:
        if await is_admin(update=message):
            if message.text and message.text in db.pet_type:
                await state.update_data(type=db.pet_type[message.text])
                await state.set_state(FSMAddPet.sex)
                msg = await message.answer('Этап 4/10 ✅✅✅❎☑☑☑☑☑☑\n<b>Укажите пол животного.</b>', reply_markup=kb.pet_sex_kb)
            else:
                msg = await message.answer('<b>Неверно указан тип животного.</b>\n<i>Воспользуйтесь кнопками ниже.</i>', reply_markup=kb.pet_type_kb)
            await state.update_data(msg=msg.message_id)


async def admin_add_pets_sex(message: types.Message, state: FSMContext):
    try:
        data = await state.get_data()
        await bot.delete_message(chat_id=message.from_user.id, message_id=data['msg'])
        await message.delete()
    finally:
        if await is_admin(update=message):
            if message.text and message.text in db.pet_sex:
                await state.update_data(sex=db.pet_sex[message.text])
                await state.set_state(FSMAddPet.age)
                msg = await message.answer('Этап 5/10 ✅✅✅✅❎☑☑☑☑☑\n<b>Укажите примерный возраст животного.</b>\nК примеру, <i>2 года</i>, или <i>три месяца</i>.')
            else:
                msg = await message.answer('<b>Неверно указан пол животного.</b>\n<i>Воспользуйтесь кнопками ниже.</i>', reply_markup=kb.pet_sex_kb)
            await state.update_data(msg=msg.message_id)


async def admin_add_pets_age(message: types.Message, state: FSMContext):
    try:
        data = await state.get_data()
        await bot.delete_message(chat_id=message.from_user.id, message_id=data['msg'])
        await message.delete()
    finally:
        if await is_admin(update=message):
            if message.text and 5 < len(message.text) < 30:
                await state.update_data(age=message.text)
                await state.set_state(FSMAddPet.sterilized)
                msg = await message.answer('Этап 6/10 ✅✅✅✅✅❎☑☑☑☑\n<b>Укажите, стерилизовано ли животное.</b>\n<i>Если вы не уверены, выберите "<u>нет</u>", данный пункт можно будет изменить позднее.</i>', reply_markup=kb.pet_bool_kb)
            else:
                msg = await message.answer('<b>Укажите возраст более понятно.</b>\nНе следует указывать просто цифру и использовать сокращения (должно быть более 5 символов). К примеру, <i>2 года</i> или <i>три месяца</i>.')
            await state.update_data(msg=msg.message_id)


async def admin_add_pets_sterilized(message: types.Message, state: FSMContext):
    try:
        data = await state.get_data()
        await bot.delete_message(chat_id=message.from_user.id, message_id=data['msg'])
        await message.delete()
    finally:
        if await is_admin(update=message):
            if message.text and message.text in db.bool_answer:
                await state.update_data(sterilized=db.bool_answer[message.text])
                await state.set_state(FSMAddPet.place)
                msg = await message.answer('Этап 7/10 ✅✅✅✅✅✅❎☑☑☑\n<b>Укажите место, где находится животное</b>', reply_markup= await kb.pet_place_kb())
            else:
                msg = await message.answer('<b>Неверный ответ.</b>\n<i>Чтобы указать, стерилизовано ли животное, воспользуйтесь кнопками ниже.</i>', reply_markup=kb.pet_bool_kb)
            await state.update_data(msg=msg.message_id)


async def admin_add_pets_place(message: types.Message, state: FSMContext):
    try:
        data = await state.get_data()
        await bot.delete_message(chat_id=message.from_user.id, message_id=data['msg'])
        await message.delete()
    finally:
        if await is_admin(update=message) and message.text and len(message.text) < 30:
            await state.update_data(place=message.text)
            await state.set_state(FSMAddPet.needs_temp_keeping)
            msg = await message.answer('Этап 8/10 ✅✅✅✅✅✅✅❎☑☑\n<b>Необходима ли животному передержка?</b>\n<i>Если вы не уверены, нажмите "нет", данный пункт возможно изменить позднее</i>', reply_markup=kb.pet_bool_kb)
            await state.update_data(msg=msg.message_id)


async def admin_add_pets_needs_temp_keeping(message: types.Message, state: FSMContext):
    try:
        data = await state.get_data()
        await bot.delete_message(chat_id=message.from_user.id, message_id=data['msg'])
        await message.delete()
    finally:
        if await is_admin(update=message):
            if message.text and message.text in db.bool_answer:
                await state.update_data(needs_temp_keeping=db.bool_answer[message.text])
                await state.set_state(FSMAddPet.description)
                msg = await message.answer('Этап 9/10 ✅✅✅✅✅✅✅✅❎☑\n<b>Введите описание.</b>\n<i> В связи с ограничениями Telegram, описание может быть до 900 символов.</i>')
            else:
                msg = await message.answer('<b>Неверный ответ.</b>\n<i>Чтобы указать, нужна ли животному передержка, воспользуйтесь кнопками ниже.</i>', reply_markup=kb.pet_bool_kb)
            await state.update_data(msg=msg.message_id)


async def admin_add_pets_description(message: types.Message, state: FSMContext):
    try:
        data = await state.get_data()
        await bot.delete_message(chat_id=message.from_user.id, message_id=data['msg'])
        await message.delete()
    finally:
        if await is_admin(update=message):
            if message.text and len(message.text) < 901:
                await state.update_data(description=message.text)
                await state.set_state(FSMAddPet.curator)
                msg = await message.answer('Этап 10/10 ✅✅✅✅✅✅✅✅✅❎\n<b>Введите данные куратора(имя и телефон).</b>')
            else:
                msg = await message.answer(f'<i>В связи с ограничениями Telegram, длина описания может быть до <b>900</b> символов. Вы ввели <b>{len(message.text)}</b>. Пожалуйста, сократите описание.</i>')
            await state.update_data(msg=msg.message_id)


async def admin_add_pets_curator(message: types.Message, state: FSMContext):
    try:
        data = await state.get_data()
        await bot.delete_message(chat_id=message.from_user.id, message_id=data['first_msg'])
        await bot.delete_message(chat_id=message.from_user.id, message_id=data['msg'])
        await message.delete()
    finally:
        if message.text and await is_admin(update=message):
            if len(message.text) < 50:
                await state.update_data(curator=message.text, published_by_id=message.from_user.id)
                db.add_pet(data=await state.get_data())
                await state.clear()
                await message.answer('Все этапы пройдены ✅\n<b>Питомец добавлен в базу данных.</b>', reply_markup= await kb.main_buttons(is_admin=True))
            else:
                await message.answer('<b>Сведения о кураторе - не более 50 символов.</b>\n<i>Повторите ввод.</i>')

def register_handlers_admin(dp: Dispatcher):
    dp.message.register(admin_add_pets_start, Text(text=kb.admin_button_text))
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
    dp.message.register(admin_edit_pet, FSMAddPet.edit)
