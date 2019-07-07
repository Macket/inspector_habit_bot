from bot import bot
from users.models import User
import users.markups as markups
import settings


@bot.message_handler(func=lambda message:
message.text in ['✉️ Написать разработчикам', '✉️ Contact developers'], content_types=['text'])
def contact_developers(message):
    feedback_request(message)


def feedback_request(message):
    user = User.get(message.chat.id)
    ru_text = f'У вас какая-то пролема или предложение по моему улучшению? ' \
              f'Напишите об этом, и я передам ваше сообщение разработчикам.'

    en_text = f'Do you have any problem or suggestion for my improvement? ' \
              f'Write about it and I will pass your message to developers.'

    text = ru_text if user.language_code == 'ru' else en_text

    bot.send_message(message.chat.id, text, reply_markup=markups.get_cancel_markup(message.chat.id))
    bot.register_next_step_handler(message, feedback_response)


def feedback_response(message):
    if message.text in ['❌ Отмена', '❌ Cancel']:
        bot.send_message(message.chat.id,
                         'Хорошо',
                         reply_markup=markups.get_main_menu_markup(message.chat.id),
                         parse_mode='Markdown')
    else:
        feedback = f'Пользователь: {message.from_user.username}\n' \
                   f'Имя: {message.from_user.first_name}\n' \
                   f'Фамилия: {message.from_user.last_name}\n' \
                   f'Язык: {message.from_user.language_code}\n\n' \
                   f'Сообщение: *{message.text}*'
        bot.send_message(settings.ADMIN_ID, feedback, parse_mode='Markdown')

        user = User.get(message.chat.id)

        ru_text = f'Спасибо! Я отослал ваше сообщение разработчикам.'
        en_text = f'Thank you! I have sent your message to developers.'
        text = ru_text if user.language_code == 'ru' else en_text

        bot.send_message(message.chat.id,
                         text,
                         reply_markup=markups.get_main_menu_markup(message.chat.id),
                         parse_mode='Markdown')
