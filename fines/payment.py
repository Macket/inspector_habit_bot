from bot import bot
from telebot.types import LabeledPrice
import settings
from users.models import User
from checks.utils import CheckStatus
from currency_converter import CurrencyConverter
from users.utils import get_user_naming


provider_token = settings.PROVIDER_TOKEN


@bot.message_handler(commands=['buy'])
def command_pay(message):
    prices = [LabeledPrice(label='Working Time Machine', amount=1000)]
    bot.send_invoice(message.chat.id, title='Оплата штрафов',
                     description='Test',
                     provider_token=provider_token,
                     currency='rub',
                     photo_url='https://safety4sea.com/wp-content/uploads/2016/06/fine-e1522744870402.png',
                     photo_height=512,  # !=0/None or picture won't be shown
                     photo_width=512,
                     photo_size=512,
                     is_flexible=False,  # True If you need to set up Shipping Fee
                     prices=prices,
                     start_parameter='fines-payment',
                     invoice_payload='FINES PAYMENT')


@bot.message_handler(commands=['usd'])
def command_pay(message):
    prices = [LabeledPrice(label='Working Time Machine', amount=100)]
    bot.send_invoice(message.chat.id, title='Оплата штрафов',
                     description='Test',
                     provider_token=provider_token,
                     currency='usd',
                     photo_url='https://safety4sea.com/wp-content/uploads/2016/06/fine-e1522744870402.png',
                     photo_height=512,  # !=0/None or picture won't be shown
                     photo_width=512,
                     photo_size=512,
                     is_flexible=False,  # True If you need to set up Shipping Fee
                     prices=prices,
                     start_parameter='fines-payment',
                     invoice_payload='FINES PAYMENT')


def send_invoice(user_id):
    user = User.get(user_id)
    violations = user.get_fines()

    title = 'Штрафы' if user.language_code == 'ru' else 'Fines'

    prices = []
    description = ''
    currency = 'rub' if user.language_code == 'ru' else 'usd'
    converter = CurrencyConverter('http://www.ecb.europa.eu/stats/eurofxref/eurofxref.zip')
    for violation in violations:
        label, datetime_native, fine = violation

        amount = int(converter.convert(fine, 'USD', 'RUB') * 100) if \
            user.language_code == 'ru' else fine * 100
        prices.append(LabeledPrice(label=f'{datetime_native} {label}', amount=amount))
        description += f'{datetime_native} {label} ${fine}\n\n'

    bot.send_invoice(user_id, title=title,
                     description=description,
                     provider_token=provider_token,
                     currency=currency,
                     photo_url='https://safety4sea.com/wp-content/uploads/2016/06/fine-e1522744870402.png',
                     photo_height=512,  # !=0/None or picture won't be shown
                     photo_width=512,
                     photo_size=512,
                     is_flexible=False,  # True If you need to set up Shipping Fee
                     prices=prices,
                     start_parameter='fines-payment',
                     invoice_payload='FINES PAYMENT')


@bot.pre_checkout_query_handler(func=lambda query: True)
def checkout(pre_checkout_query):
    bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True,
                                  error_message='🇷🇺 Что-то пошло не так\n🇬🇧 Something wents wrong')


@bot.message_handler(content_types=['successful_payment'])
def got_payment(message):
    user = User.get(message.chat.id)
    user.satisfy_fines(CheckStatus.PAID.name)

    ru_text = 'Все штрафы погашены, все обвинения сняты.'
    en_text = 'All fines repaid, all charges dropped.'
    text = ru_text if user.language_code == 'ru' else en_text

    bot.send_message(message.chat.id, text, parse_mode='Markdown')


@bot.callback_query_handler(func=lambda call: call.data.startswith('@@JUDGE_PAYMENT_REPORT'))
def got_judge_payment_report(call):
    user_id = int(call.data.split('/')[1])

    user = User.get(user_id)
    judge = User.get(call.message.chat.id)
    user.satisfy_fines(CheckStatus.JUSTIFIED.name, call.message.chat.id)

    ru_text_judge = f'Все штрафы {get_user_naming(user, "твоего друга")} погашены.'
    en_text_judge = f'All fines of {get_user_naming(user, "your friend")} are paid'
    text_judge = ru_text_judge if judge.language_code == 'ru' else en_text_judge

    ru_text_user = f'Все штрафы перед {get_user_naming(judge, "твоим другом")} погашены.'
    en_text_user = f'All fines to {get_user_naming(judge, "your friend")} are paid.'
    text_user = ru_text_user if user.language_code == 'ru' else en_text_user

    try:
        bot.send_message(call.message.chat.id, text_judge)
    except Exception:
        pass
    try:
        bot.send_message(user_id, text_user)
    except Exception:
        pass
