from bot import bot
from telebot.types import LabeledPrice
import settings
from users.models import User
from checks.utils import CheckStatus


provider_token = settings.PROVIDER_TOKEN


@bot.message_handler(commands=['buy'])
def command_pay(message):
    prices = [LabeledPrice(label='Working Time Machine', amount=200)]
    bot.send_invoice(message.chat.id, title='Оплата штрафов',
                     description='Test',
                     provider_token=provider_token,
                     currency='uah',
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
    for violation in violations:
        label = violation[0]
        datetime_native = violation[1]
        fine = violation[2]
        prices.append(LabeledPrice(label=f'{datetime_native} {label}', amount=fine * 100))
        description += f'{datetime_native} {label} ${fine}\n\n'

    bot.send_invoice(user_id, title=title,
                     description=description,
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


@bot.pre_checkout_query_handler(func=lambda query: True)
def checkout(pre_checkout_query):
    bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True,
                                  error_message='🇷🇺 Что-то пошло не так\n🇬🇧 Something wents wrong')


@bot.message_handler(content_types=['successful_payment'])
def got_payment(message):
    user = User.get(message.chat.id)
    user.satisfy_fines(CheckStatus.PAID.name)

    ru_text = 'Вы честный человек! Все штрафы погашены, все обвинения сняты.'
    en_text = 'You are an honest person! All fines repaid, all charges dropped.'
    # ru_text = 'Вы честный человек! А вот я вас немного обманул ' \
    #           'и не взял ни копейки. Надеюсь, вы не в обиде😁\n\n' \
    #           'Не беспокойтесь, скоро ко мне подключат реальные платежи, ' \
    #           'и тогда вы уже так просто не отделаетесь😉'
    # en_text = 'You are an honest person! But I deceived you a little ' \
    #           'and did not take a penny. I hope you are not offended😁\n\n' \
    #           'Do not worry, soon real payments will be connected to me, ' \
    #           'and then you will not get off so easily😉'
    text = ru_text if user.language_code == 'ru' else en_text

    bot.send_message(message.chat.id, text, parse_mode='Markdown')
