from aiogram import Dispatcher, types
from aiogram.filters import Text
from create_bot import bot
import keyboards as kb
import database.db_sqlite as db
import callback_factories as cf


async def help_menu(update: types.Update) -> None:
    try:
        if type(update) == types.Message:
            await update.delete()
        else:
            await update.message.delete()
    finally:
        msg = 'В этом разделе Вы можете найти информацию о возможных вариантах помощи и предложить посильную для Вас помощь. Если у Вас имеются иные предложения, просим Вас связаться с волонтёрами.'
        await bot.send_message(chat_id=update.from_user.id, text=msg, reply_markup=kb.kb_help_menu)


async def some_help(call: types.CallbackQuery) -> None:
    try:
        await call.message.delete()
    finally:
        help_type = call.data.split('|')[1]
        msg_dict = {'volunteer_help': 'Приютам необходима помощь волонтеров в уходе за собаками и кошками, два раза в день день мы приходим к животным. Нам постоянно нужны люди, которые готовы ухаживать за ними (убирать, кормить, выгуливать). Если у вас есть возможность посвятить хотя бы 1 утро или вечер в неделю помощи бездомным животным, оставьте заявку ниже и с вами свяжутся волонтеры.',
                    'financial_help': 'Приютам и волонтерам всегда необходима финансовая помощь для обеспечения питомцев всем необходимым: корма, средства по уходу за животными, ветеринарная помощь, стерилизации, другие неотложные нужды приюта. Осуществив перевод любой суммы денежных средств по указанным реквизитам, вы поможете сделать жизнь питомцев лучше, а, возможно, сможете спасти чью-то жизнь.',
                    'material_help': 'Сообщение о том, что нужно животным: корм, лекарства, наполнитель, пелёнки, газеты'}
        await call.message.answer(text=msg_dict[help_type], reply_markup= await kb.kb_orgs(help_type))


def register_handlers(dp: Dispatcher):
    dp.message.register(help_menu, Text(text=kb.main_buttons_text[1]))
    dp.callback_query.register(help_menu, lambda call: call.data == 'help')
    dp.callback_query.register(some_help, lambda call: call.data.endswith('_help'))
