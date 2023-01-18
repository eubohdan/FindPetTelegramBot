from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from database import db_sqlite as db
import callback_factories as cf

main_buttons_text = ['🐾Выбрать питомца', '🫶Хочу помочь', '🏡Организации']
admin_button_text = 'Добавить питомца'


async def main_buttons(is_admin: bool) -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    for item in main_buttons_text:
        builder.button(text=item)
    if is_admin:
        builder.button(text=admin_button_text)
    builder.adjust(3)
    return builder.as_markup(resize_keyboard=True,
                             input_field_placeholder='Для выбора пункта меню нажмите на кнопку')


kb_about_me = InlineKeyboardMarkup(
    inline_keyboard=[[InlineKeyboardButton(text='✍️Написать автору бота', url='https://t.me/id7489')],
                     [InlineKeyboardButton(text='Скрыть', callback_data='hide')]])


async def kb_orgs(action: str) -> InlineKeyboardMarkup:
    '''Собирает клавиатуру со списком организаций'''
    builder = InlineKeyboardBuilder()
    orgs = db.get_org_names()
    for i in range(len(orgs)):
        builder.button(text=orgs[i][1], callback_data=cf.InfoCallbackFactory(action=action, value=orgs[i][0]))
    if action == 'description':
        builder.button(text='Скрыть', callback_data='hide')
    else:
        builder.button(text='Назад', callback_data='help')
    builder.adjust(1)
    return builder.as_markup()


async def kb_org_socials(row_id: str, user_id: int) -> InlineKeyboardMarkup:
    '''Собирает клавиатуру со списком социальных сетей и кнопкой редактировать для админа'''
    builder = InlineKeyboardBuilder()
    socials = db.get_org_social(row_id)
    for item in socials.items():
        builder.add(InlineKeyboardButton(text=item[0], url=item[1]))
    # if await is_admin_silent(userid): # измененить описание могут все админы из чата
    if str(user_id) == db.get_org_info(data_type='admin_id', row_id=row_id):  # изменить может только конкретный админ
        builder.add(InlineKeyboardButton(text='Редактировать', callback_data=f'orgedit|{row_id}|menu'))
    builder.add(InlineKeyboardButton(text='Назад', callback_data='orgs'))
    builder.adjust(2)
    return builder.as_markup()


async def kb_edit_org(row_id: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text='Фото', callback_data=f'orgedit|{row_id}|photo')  # !!
    builder.button(text='Описание', callback_data=f'orgedit|{row_id}|description')  # !!
    builder.button(text='Отмена', callback_data=cf.InfoCallbackFactory(action='description', value=row_id))
    builder.adjust(2)
    return builder.as_markup()


kb_cancel_edit = InlineKeyboardMarkup(
    inline_keyboard=[[InlineKeyboardButton(text='Отменить и выйти', callback_data='cancelFSM')]])


kb_cancel_edit2 = InlineKeyboardMarkup(
    inline_keyboard=[[InlineKeyboardButton(text='К предыдущему пункту', callback_data='prevFSM')], [InlineKeyboardButton(text='Отменить и выйти', callback_data='cancelFSM')]])


kb_help_menu = InlineKeyboardMarkup(
    inline_keyboard=[[InlineKeyboardButton(text='🏠Передержка', callback_data='keep'),
                      InlineKeyboardButton(text='🚗Автопомощь', callback_data='auto')],
                     [InlineKeyboardButton(text='🧽Волонтерство', callback_data='help|volunteer_help'),
                      InlineKeyboardButton(text='💳Финансово', callback_data='help|financial_help')],
                     [InlineKeyboardButton(text='🍖Материально', callback_data='help|material_help'),
                      InlineKeyboardButton(text='Скрыть', callback_data='hide')]])


async def kb_search_menu() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for num, item in enumerate(['🐱Котята', '🐶Щенки', '🐈Кошки', '🐕Собаки']):
        builder.button(text=item, callback_data=cf.SearchCallbackFactory(pet_type=num, page=0, action='scrolling'))
    builder.button(text='Скрыть', callback_data='hide')
    builder.adjust(2)
    return builder.as_markup()


async def scrolling_kb(pet_type: int, page: int, pages: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text='Забрать питомца',
                   callback_data=cf.SearchCallbackFactory(pet_type=pet_type, page=page, action='sure'))
    builder.button(text='Подробнее',
                   callback_data=cf.SearchCallbackFactory(pet_type=pet_type, page=page, action='post'))
    builder.button(text='<-- Назад', callback_data=cf.SearchCallbackFactory(pet_type=pet_type, page=(page - 1) % pages,
                                                                            action='scrolling'))
    builder.button(text=f'{page + 1}/{pages}',
                   callback_data=cf.SearchCallbackFactory(pet_type=pet_type, page=page, action='pointer'))
    builder.button(text='Вперед -->', callback_data=cf.SearchCallbackFactory(pet_type=pet_type, page=(page + 1) % pages,
                                                                             action='scrolling'))
    builder.button(text='Вернуться', callback_data='search')
    builder.adjust(1, 1, 3, 1)
    return builder.as_markup()


async def pet_choosed_kb(pet_type: int, page: int, is_admin: bool) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    if is_admin:
        builder.button(text='Редактировать описание',
                       callback_data=cf.SearchCallbackFactory(pet_type=pet_type, page=page, action='edit'))
        builder.button(text='Удалить',
                       callback_data=cf.SearchCallbackFactory(pet_type=pet_type, page=page, action='delete_sure'))
    else:
        builder.button(text='Забрать питомца',
                       callback_data=cf.SearchCallbackFactory(pet_type=pet_type, page=page, action='sure'))
    builder.button(text='Назад',
                   callback_data=cf.SearchCallbackFactory(pet_type=pet_type, page=page, action='scrolling'))
    builder.adjust(2, 1) if is_admin else builder.adjust(1)
    return builder.as_markup()


async def pet_choosed_sure(pet_type: int, page: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text='Подтвердить',
                   callback_data=cf.SearchCallbackFactory(pet_type=pet_type, page=page, action='request'))
    builder.button(text='Назад',
                   callback_data=cf.SearchCallbackFactory(pet_type=pet_type, page=page, action='scrolling'))
    return builder.as_markup()


async def pet_delete_sure(pet_type: int, page: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text='Удалить',
                   callback_data=cf.SearchCallbackFactory(pet_type=pet_type, page=page, action='delete'))
    builder.button(text='Не удалять',
                   callback_data=cf.SearchCallbackFactory(pet_type=pet_type, page=page, action='post'))
    return builder.as_markup()


async def pet_was_deleted(pet_type: int, page: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text='К списку питомцев',
                   callback_data=cf.SearchCallbackFactory(pet_type=pet_type, page=page, action='scrolling'))
    return builder.as_markup()


async def what_to_edit(pet_type: int, page: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text='Фото', callback_data=cf.SearchCallbackFactory(pet_type=pet_type, page=page, action='edit', additional='img'))
    builder.button(text='Описание', callback_data=cf.SearchCallbackFactory(pet_type=pet_type, page=page, action='edit', additional='description'))
    builder.button(text='Возраст', callback_data=cf.SearchCallbackFactory(pet_type=pet_type, page=page, action='edit', additional='age'))
    builder.button(text='Стерилизация', callback_data=cf.SearchCallbackFactory(pet_type=pet_type, page=page, action='edit', additional='sterilized'))
    builder.button(text='Место', callback_data=cf.SearchCallbackFactory(pet_type=pet_type, page=page, action='edit', additional='place'))
    builder.button(text='Куратор', callback_data=cf.SearchCallbackFactory(pet_type=pet_type, page=page, action='edit', additional='curator'))
    builder.button(text='Нужна ли передержка', callback_data=cf.SearchCallbackFactory(pet_type=pet_type, page=page, action='edit', additional='needs_temp_keeping'))
    builder.button(text='Назад', callback_data=cf.SearchCallbackFactory(pet_type=pet_type, page=page, action='post'))
    builder.adjust(2, 2, 2, 1, 1)
    return builder.as_markup()


async def kb_help_org(action: str, row_id: str, user_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    admin = db.get_org_info(data_type='admin_id', row_id=row_id)  # изменить может только конкретный админ
    if str(user_id) == admin:
        builder.add(InlineKeyboardButton(text='Редактировать', callback_data=f'orgedit|{row_id}|{action}'))
    else:
        builder.row(InlineKeyboardButton(text='Предложить помощь',
                                         url=f"tg://user?id={admin}"))  # !!! будет ошибка если у админа настроена приватность
    builder.row(InlineKeyboardButton(text='Назад', callback_data=f'help|{action}'))
    return builder.as_markup()


kb_temp_keeping = InlineKeyboardMarkup(
    inline_keyboard=[[InlineKeyboardButton(text='🐾Взять на передержку', callback_data='search')],
                     [InlineKeyboardButton(text='Назад', callback_data='help')]])

kb_auto_help = InlineKeyboardMarkup(
    inline_keyboard=[[InlineKeyboardButton(text='Оставить заявку', callback_data='in_dev')],
                     [InlineKeyboardButton(text='Назад', callback_data='help')]])


pet_type_kb = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text=i) for i in db.pet_type]],
                resize_keyboard=True, one_time_keyboard=True, input_field_placeholder='Выберите вариант из предложенных')

pet_sex_kb = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text=i) for i in db.pet_sex]],
                resize_keyboard=True, one_time_keyboard=True, input_field_placeholder='Выберите вариант из предложенных')

pet_bool_kb = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text=i) for i in db.bool_answer]],
                resize_keyboard=True, one_time_keyboard=True, input_field_placeholder='Выберите вариант из предложенных')


async def pet_place_kb() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    for name in [i[1] for i in db.get_org_names()]:
        builder.button(text=name)
    builder.button(text='Гурского, 42')
    builder.button(text='Передержка')
    builder.adjust(2)
    return builder.as_markup()

