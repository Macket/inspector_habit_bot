from bot import bot
from telebot.types import LabeledPrice, ShippingOption
import settings


provider_token = settings.PROVIDER_TOKEN
prices = [LabeledPrice(label='Working Time Machine', amount=100)]
shipping_options = [
    ShippingOption(id='instant', title='WorldWide Teleporter').add_price(LabeledPrice('Teleporter', 1000)),
    ShippingOption(id='pickup', title='Local pickup').add_price(LabeledPrice('Pickup', 0))]


@bot.message_handler(commands=['pay'])
def pay(message):
    bot.send_invoice(message.chat.id,
                     title='Working Time Machine',
                     description='Want to visit your great-great-great-grandparents?'
                                     ' Make a fortune at the races?'
                                     ' Shake hands with Hammurabi and take a stroll in the Hanging Gardens?'
                                     ' Order our Working Time Machine today!',
                     provider_token=provider_token,
                         currency='usd',
                         photo_url='http://erkelzaar.tsudao.com/models/perrotta/TIME_MACHINE.jpg',
                         photo_height=512,  # !=0/None or picture won't be shown
                         photo_width=512,
                         photo_size=512,
                         is_flexible=False,  # True If you need to set up Shipping Fee
                         prices=prices,
                         start_parameter='time-machine-example',
                         invoice_payload='HAPPY FRIDAYS COUPON')


@bot.shipping_query_handler(func=lambda query: True)
def shipping(shipping_query):
    print(shipping_query)
    bot.answer_shipping_query(shipping_query.id, ok=True, shipping_options=shipping_options,
                              error_message='Oh, seems like our Dog couriers are having a lunch right now. Try again later!')


@bot.pre_checkout_query_handler(func=lambda query: True)
def checkout(pre_checkout_query):
    bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True,
                                  error_message="Aliens tried to steal your card's CVV, but we successfully protected your credentials,"
                                                " try to pay again in a few minutes, we need a small rest.")


@bot.message_handler(content_types=['successful_payment'])
def got_payment(message):
    bot.send_message(message.chat.id,
                     'Hoooooray! Thanks for payment! We will proceed your order for `{} {}` as fast as possible! '
                     'Stay in touch.\n\nUse /buy again to get a Time Machine for your friend!'.format(
                         message.successful_payment.total_amount / 100, message.successful_payment.currency),
                     parse_mode='Markdown')
