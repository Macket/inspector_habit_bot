from bot import bot
from users import markups as user_markups
from fines import markups
from fines.payment import send_invoice
from users.models import User
from users.utils import get_user_naming


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


@bot.message_handler(func=lambda message:
message.text in ['🤨 Куда пойдут мои деньги?', '🤨 Where will my money go?'], content_types=['text'])
def user_violations(message):
    user = User.get(message.chat.id)

    ru_text = '80% пойдут детишкам на интернет: https://giveinternet.org/\n\n' \
              'Остальное я потрачу на кофе с булочками😊'
    en_text = '80% of money I will donate on Internet access to ' \
              'underprivileged high-school students: https://giveinternet.org/\n\n' \
              "I'll spend the rest on coffee with buns😊"
    text = ru_text if user.language_code == 'ru' else en_text

    try:
        bot.send_message(message.chat.id,
                         text=text,
                         parse_mode='Markdown',
                         reply_markup=user_markups.get_main_menu_markup(message.chat.id))
    except:
        pass


def user_violations_with_judge(user_id, judge_id):
    user = User.get(user_id)
    judge = User.get(judge_id)

    violations = user.get_fines(judge_id)

    ru_report_user = f'Ты обвиняешься в следующих нарушениях перед ' \
                     f'{get_user_naming(judge, "своим другом")}:\n\n'
    en_report_user = f'You are accused of the following violations in front of ' \
                     f'{get_user_naming(judge, "your friend")}:\n\n'

    ru_report_judge = f'{get_user_naming(user, "Твой друг")} обвиняется в следующих нарушениях перед тобой:\n\n'
    en_report_judge = f'{get_user_naming(user, "Your friend")} accused of the following violations in front of you:\n\n'

    report_user = ru_report_user if user.language_code == 'ru' else en_report_user
    report_judge = ru_report_judge if judge.language_code == 'ru' else en_report_judge

    sum = 0
    for violation in violations:
        label = violation[0]
        datetime_native = violation[1]
        fine = violation[2]

        report_user += f'_{datetime_native}_ {label} *${fine}*\n\n'
        report_judge += f'_{datetime_native}_ {label} *${fine}*\n\n'

        sum += fine

    report_user += f'Заплати {get_user_naming(judge, "другу")} *${sum}*' if user.language_code == 'ru' else \
        f'Pay {get_user_naming(judge, "your friend")} *${sum}*'

    report_judge += f'Когда {get_user_naming(user, "твой друг")} заплатит тебе *${sum}*, нажми кнопку👇' if user.language_code == 'ru' else \
        f'When {get_user_naming(user, "your friend")} pays you *${sum}*, hit the button👇'

    try:
        bot.send_message(user_id, text=report_user, parse_mode='Markdown')
    except Exception:
        pass

    try:
        bot.send_message(judge_id, text=report_judge, parse_mode='Markdown',
                         reply_markup=markups.get_judge_payment_report_markup(user_id, judge_id))
    except Exception:
        pass


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
