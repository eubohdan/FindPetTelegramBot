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


async def temp_keeping(call: types.CallbackQuery) -> None:
    try:
        await call.message.delete()
    finally:
        await call.message.answer(text=f'Передержка – ключевой момент в спасении бездомного животного. Если в Вашем доме есть место для кота или собаки, которые пока не нашли своего хозяина, Вы можете помочь, предоставив им временный дом! И это совсем не означает, что, взяв собаку или кота к себе, Вы берете на себя его дальнейшее содержание и пристройство. Кураторы животных всегда помогут всем необходимым, привезут и увезут в оговоренные с Вами сроки. Даже кратковременная передержка – это очень большая помощь!',
                                  reply_markup=kb.kb_temp_keeping)


async def auto_help(call: types.CallbackQuery) -> None:
    try:
        await call.message.delete()
    finally:
        await call.message.answer(text=f'Автопомощь – одно из важных направлений помощи бездомным животным. Ежедневно кому-то из наших животных нужно попасть на прием к врачу, переехать на передержку, поучаствовать в акциях и выставках, доехать к новому хозяину, но не всегда у волонтеров есть возможность транспортировать животное на общественном транспорте. Именно поэтому нам очень нужна Ваша помощь, уважаемые автовладельцы! Если у вас найдется немного свободного времени и желание помочь – проявите участие! Оставьте заявку и вам иногда будут приходить персональные уведомления, на которые вы сможете откликнуться, нажав на соответствующую кнопку.',
                                  reply_markup=kb.kb_auto_help)


def register_handlers(dp: Dispatcher):
    dp.message.register(help_menu, Text(text=kb.main_buttons_text[1]))
    dp.callback_query.register(help_menu, lambda call: call.data == 'help')
    dp.callback_query.register(some_help, lambda call: call.data.endswith('_help'))
    dp.callback_query.register(temp_keeping, lambda call: call.data == 'keep')
    dp.callback_query.register(auto_help, lambda call: call.data == 'auto')
