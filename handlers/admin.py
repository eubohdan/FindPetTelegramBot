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
        await bot.send_message(message.from_user.id,
                               'Вы находитесь в меню добавления питомца в базу. Чтобы отменить добавление, <b>нажмите кнопку ниже\nЗагрузите фото питомца.</b>. <i>Рекомендуется загружать горизонтальные фото.</i>',
                               reply_markup=kb.kb_cancel_edit)


async def prev(call: types.CallbackQuery, state: FSMContext):
    if await is_admin(update=call):
        await FSMAddPet.previous() if FSMAddPet.previous is not None else state.finish()
        await call.message.delete()


async def admin_add_pets_photo(message: types.Message, state: FSMContext):
    if await is_admin(update=message):
        try:
            await state.storage.set_data(bot, key=state.key, data={'photo': message.photo[0].file_id})
            await state.set_state(FSMAddPet.name)
            await message.answer('<b>Введите имя питомца.</b>')
        except IndexError:
            await bot.send_message(message.from_user.id, 'Вы загрузили не фотографию, попробуйте снова.',
                                   reply_markup=kb.kb_cancel_edit)


async def admin_add_pets_name(message: types.Message, state: FSMContext):
    if await is_admin(update=message):
        if message.text.isalpha():
            await state.storage.update_data(bot, key=state.key, data={'name': message.text})
            await state.set_state(FSMAddPet.type)
        else:
            await message.answer('Имя может состоять только из букв, попробуйте снова')

            await message.reply('Укажите тип животного', reply_markup=kb.add_pet_kb2)


async def admin_add_pets_type(message: types.Message, state: FSMContext):
    if message.from_user.id in config.admins:
        async with state.proxy() as data:
            data['type'] = message.text
            await FSMAdmin.next()
            await message.reply('Укажите пол животного', reply_markup=kb.add_pet_kb3)


async def admin_add_pets_sex(message: types.Message, state: FSMContext):
    if message.from_user.id in config.admins:
        async with state.proxy() as data:
            data['sex'] = message.text
            await FSMAdmin.next()
            await message.reply('Укажите примерный возраст животного')


async def admin_add_pets_age(message: types.Message, state: FSMContext):
    if message.from_user.id in config.admins:
        async with state.proxy() as data:
            data['age'] = message.text
            await FSMAdmin.next()
            await message.reply('Укажите, стерилизовано ли животное', reply_markup=kb.add_pet_kb5)


async def admin_add_pets_sterilized(message: types.Message, state: FSMContext):
    if message.from_user.id in config.admins:
        async with state.proxy() as data:
            data['sterilized'] = message.text
            await FSMAdmin.next()
            await message.reply('Укажите место, где находится животное', reply_markup=kb.add_pet_kb4)


async def admin_add_pets_place(message: types.Message, state: FSMContext):
    if message.from_user.id in config.admins:
        async with state.proxy() as data:
            data['place'] = message.text
            await FSMAdmin.next()
            await message.reply('Необходима ли животному передержка?', reply_markup=kb.add_pet_kb6)


async def admin_add_pets_needs_temp_keeping(message: types.Message, state: FSMContext):
    if message.from_user.id in config.admins:
        async with state.proxy() as data:
            data['needs_temp_keeping'] = message.text
            await FSMAdmin.next()
            await message.answer('Введите описание (до 900 символов).')


async def admin_add_pets_description(message: types.Message, state: FSMContext):
    if message.from_user.id in config.admins:
        if len(message.text) < 951:
            async with state.proxy() as data:
                data['description'] = message.text
                await FSMAdmin.next()
                await message.reply('Введите данные куратора(имя и телефон)')


async def admin_add_pets_curator(message: types.Message, state: FSMContext):
    if message.from_user.id in config.admins:
        async with state.proxy() as data:
            data['curator'] = message.text
            data['published_by_id'] = message.from_user.id
        await db_sqlite.add_value(state)
        # await db_sqlite.sql_add(state)
        await state.finish()
        await message.reply('Питомец добавлен в базу', reply_markup=kb.keyboard_main_admin)


async def admin_add_pets_cancel(message: types.Message, state: FSMContext):
    if message.from_user.id in config.admins:
        current_state = await state.get_state()
        if current_state is None:
            return
        await state.finish()
        await message.reply('OK', reply_markup=kb.keyboard_main_admin)


def register_handlers_admin(dp: Dispatcher):
    dp.message.register(admin_add_pets_start, Text(text=kb.admin_button_text))
    dp.message.register(admin_add_pets_cancel, Text(text='Выйти', ignore_case=True), state='*')
    dp.message.register(prev, Text(text=kb.back_to_prev), state='*')
    dp.message.register(admin_add_pets_photo, content_types=types.ContentType.ANY, state=FSMAddPet.photo)
    dp.message.register(admin_add_pets_name, state=FSMAddPet.name)
    dp.message.register(admin_add_pets_type, state=FSMAddPet.type)
    dp.message.register(admin_add_pets_sex, state=FSMAddPet.sex)
    dp.message.register(admin_add_pets_age, state=FSMAddPet.age)
    dp.message.register(admin_add_pets_sterilized, state=FSMAddPet.sterilized)
    dp.message.register(admin_add_pets_place, state=FSMAddPet.place)
    dp.message.register(admin_add_pets_needs_temp_keeping, state=FSMAddPet.needs_temp_keeping)
    dp.message.register(admin_add_pets_description, state=FSMAddPet.description)
    dp.message.register(admin_add_pets_curator, state=FSMAddPet.curator)
    dp.callback_query.register(prev, lambda call: call.data == 'prevFSM')
