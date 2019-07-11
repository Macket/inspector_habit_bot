from bot import bot
from telebot.types import LabeledPrice
import settings

provider_token = settings.PROVIDER_TOKEN


prices = [LabeledPrice(label='Working Time Machine', amount=200)]


@bot.message_handler(commands=['buy'])
def command_pay(message):
    bot.send_invoice(message.chat.id, title='Оплата штрафов',
                     description='',
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
    print(pre_checkout_query)
    bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)


@bot.message_handler(content_types=['successful_payment'])
def got_payment(message):
    bot.send_message(message.chat.id,
                     'Hoooooray! Thanks for payment! We will proceed your order for `{} {}` as fast as possible! '
                     'Stay in touch.\n\nUse /buy again to get a Time Machine for your friend!'.format(
                         message.successful_payment.total_amount / 100, message.successful_payment.currency),
                     parse_mode='Markdown')
