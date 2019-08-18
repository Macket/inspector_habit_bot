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
    ru_text = "Ты что решил пожаловаться на меня начальству!? Ну давай пиши, что там у тебя, я передам."

    en_text = "Have you decided to complain to my boss!? Well, let's write what you have there, I will convey."

    text = ru_text if user.language_code == 'ru' else en_text

    bot.send_message(message.chat.id, text, reply_markup=markups.get_cancel_markup(message.chat.id))
    bot.register_next_step_handler(message, feedback_response)


def feedback_response(message):
    if message.text in ['❌ Отмена', '❌ Cancel']:
        text = 'Хорошо' if message.text == '❌ Отмена' else 'Ok'
        bot.send_message(message.chat.id,
                         text,
                         reply_markup=markups.get_main_menu_markup(message.chat.id),
                         parse_mode='Markdown')
    else:
        feedback = f'id: {message.chat.id}\n' \
                   f'Пользователь: {message.from_user.username}\n' \
                   f'Имя: {message.from_user.first_name}\n' \
                   f'Фамилия: {message.from_user.last_name}\n' \
                   f'Язык: {message.from_user.language_code}\n\n' \
                   f'Сообщение: *{message.text}*'
        bot.send_message(settings.ADMIN_ID, feedback, parse_mode='Markdown')

        user = User.get(message.chat.id)

        ru_text = 'Твоё обращение уже на столе у начальника😉'
        en_text = "Your appeal is already on the boss's desk😉"
        text = ru_text if user.language_code == 'ru' else en_text

        bot.send_message(message.chat.id,
                         text,
                         reply_markup=markups.get_main_menu_markup(message.chat.id),
                         parse_mode='Markdown')
