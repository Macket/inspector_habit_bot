from bot import bot
from users import markups as user_markups
from fines import markups
from fines.payment import send_invoice
from users.models import User


@bot.message_handler(func=lambda message:
message.text in ['❗️ Мои нарушения', '❗ My violations'], content_types=['text'])
def user_violations(message):
    user = User.get(message.chat.id)
    violations = user.get_fines()

    if len(violations) == 0:
        ru_report = 'Ты чист как слеза: ни одного нарушения.'
        en_report = "You are clean as a whistle: there are not any violations."
        report = ru_report if user.language_code == 'ru' else en_report
        markup = user_markups.get_main_menu_markup(message.chat.id)
    else:
        ru_report = 'Ты обвиняешься в следующих нарушениях:\n\n'
        en_report = 'You are charged with the following violations:\n\n'
        report = ru_report if user.language_code == 'ru' else en_report

        for violation in violations:
            label = violation[0]
            datetime_native = violation[1]
            fine = violation[2]

            report += f'_{datetime_native}_ {label} *${fine}*\n\n'

        report += 'Выбери наказание' if user.language_code == 'ru' else 'Choose punishment'
        markup = markups.get_punishment_markup(message.chat.id)

    bot.send_message(message.chat.id, text=report, parse_mode='Markdown', reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data.startswith('@@PUNISHMENT'))
def handle_punishment_query(call):
    if call.data == '@@PUNISHMENT/pay':
        send_invoice(call.message.chat.id)
    else:
        user = User.get(call.message.chat.id)
        ru_text = 'Пригласи друга. Когда он перейдёт по твоей ссылке ' \
                  'и назначит свою первую привычку, ' \
                  'все обвинения с тебя будут сняты.\n\n' \
                  'Просто перешли своему другу сообщение ниже👇'
        en_text = 'Invite a friend. When he follows your ' \
                  'link and assigns his first habit, ' \
                  'all charges will be dropped.\n\n ' \
                  'Just forward to your friend the message below👇'
        text = ru_text if user.language_code == 'ru' else en_text
        bot.send_message(user.id, text)

        violations = user.get_fines()
        report = ''
        sum = 0
        for violation in violations:
            label = violation[0]
            datetime_native = violation[1]
            fine = violation[2]

            report += f'_{datetime_native}_ *{label}*\n\n'
            sum += fine
        ru_text_invite = f'Привет! Твой друг переслал тебе это сообщение, чтобы ты его выручил. ' \
                         f'Дело в том, что он чёртов лентяй и обвиняется в нарушении следующих обещаний:\n\n' \
                         f'{report}' \
                         f'За это ему грозит *суммарный штраф ${sum}*. ' \
                         f'Чтобы избавить друга от штрафа, нажми кнопку внизу и назначь свою первую привычку. ' \
                         f'Очень надеюсь, что ты не такой прокрастинатор, как он.'
        en_text_invite = f'Hello! Your friend has forwarded this message to you so that you can help him out. ' \
                         f'The fact is that he is a damn bummer and is accused of breaking the following promises:\n\n' \
                         f'{report}' \
                         f'For this your friend faces a *total fine ${sum}*. ' \
                         f'To save a friend from the fine, click the button below and assign your first habit. ' \
                         f'I really hope that you are not such a procrastinator like him.'
        text_invite = ru_text_invite if user.language_code == 'ru' else en_text_invite

        bot.send_message(user.id,
                         text_invite,
                         reply_markup=markups.get_social_work_markup(user.id),
                         parse_mode='Markdown')
