from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from database import db_sqlite as db
import callback_factories as cf


main_buttons_text = ['🐾Выбрать питомца', '🫶Хочу помочь', '🏡Организации']
main_buttons_kb = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text=item) for item in main_buttons_text]],
                                      resize_keyboard=True,
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
    builder.button(text='Фото', callback_data=f'orgedit|{row_id}|photo') #!!
    builder.button(text='Описание', callback_data=f'orgedit|{row_id}|description') #!!
    builder.button(text='Отмена', callback_data=cf.InfoCallbackFactory(action='description', value=row_id))
    builder.adjust(2)
    return builder.as_markup()


kb_cancel_edit = InlineKeyboardMarkup(
    inline_keyboard=[[InlineKeyboardButton(text='Отменить и выйти', callback_data='cancelFSM')]])


kb_help_menu = InlineKeyboardMarkup(
    inline_keyboard=[[InlineKeyboardButton(text='🏠Передержка', callback_data='keep'),
                      InlineKeyboardButton(text='🚗Автопомощь', callback_data='auto')],
                     [InlineKeyboardButton(text='🧽Волонтерство', callback_data='help|volunteer_help'),
                      InlineKeyboardButton(text='💳Финансово', callback_data='help|financial_help')],
                     [InlineKeyboardButton(text='🍖Материально', callback_data='help|material_help'),
                      InlineKeyboardButton(text='Скрыть', callback_data='hide')]])


# kb_search_menu = InlineKeyboardMarkup(
#     inline_keyboard=[[InlineKeyboardButton(text='🐱Котята', callback_data=f'search|{pet_type[0]}|0'),
#                       InlineKeyboardButton(text='🐶Щенки', callback_data=f'search|{pet_type[1]}|0')],
#                      [InlineKeyboardButton(text='🐈Кошки', callback_data=f'search|{pet_type[2]}|0'),
#                       InlineKeyboardButton(text='🐕Собаки', callback_data=f'search|{pet_type[3]}|0')],
#                      [InlineKeyboardButton(text='Скрыть', callback_data='hide')]])


async def kb_search_menu() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for num, item in enumerate(['🐱Котята', '🐶Щенки', '🐈Кошки', '🐕Собаки']):
        builder.button(text=item, callback_data=cf.SearchCallbackFactory(pet_type=num, page=0, action='scrolling'))
    builder.button(text='Скрыть', callback_data='hide')
    builder.adjust(2)
    return builder.as_markup()


async def scrolling_kb(row_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.button(text='Скрыть', callback_data='hide')
    builder.adjust(3)
    return builder.as_markup()


async def kb_help_org(action: str, row_id: str, user_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    admin = db.get_org_info(data_type='admin_id', row_id=row_id)  # изменить может только конкретный админ
    if str(user_id) == admin:
        builder.add(InlineKeyboardButton(text='Редактировать', callback_data=f'orgedit|{row_id}|{action}'))
    else:
        builder.row(InlineKeyboardButton(text='Предложить помощь', url=f"tg://user?id={admin}")) #!!! будет ошибка если у админа настроена приватность
    builder.row(InlineKeyboardButton(text='Назад', callback_data=f'help|{action}'))
    return builder.as_markup()


kb_temp_keeping = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='🐾Взять на передержку', callback_data='in_dev')],
                                        [InlineKeyboardButton(text='Назад', callback_data='help')]])


kb_auto_help = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='Оставить заявку', callback_data='in_dev')],
                                     [InlineKeyboardButton(text='Назад', callback_data='help')]])
