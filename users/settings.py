from bot import bot
from users.models import User
import users.markups as markups
import settings
import pytz
from tzwhere import tzwhere


@bot.message_handler(func=lambda message:
message.text in ['⚙️ Настройки', '⚙️ Settings'], content_types=['text'])
def settings_type_request(message):
    user = User.get(message.chat.id)

    ru_text = "Что будем настраивать?"
    en_text = "What will we configure?"
    text = ru_text if user.language_code == 'ru' else en_text

    bot.send_message(message.chat.id,
                     text, reply_markup=markups.get_settings_markup(message.chat.id))
    bot.register_next_step_handler(message, settings_type_recieve)


def settings_type_recieve(message):
    if message.text == '🇷🇺 Язык':
        bot.send_message(message.chat.id,
                         'Выбери язык', reply_markup=markups.get_languages_markup())
        bot.register_next_step_handler(message, language_receive)
    elif message.text == '🇬🇧 Language':
        bot.send_message(message.chat.id,
                         'Choose the language', reply_markup=markups.get_languages_markup())
        bot.register_next_step_handler(message, language_receive)
    elif message.text == '🕒 Часовой пояс':
        bot.send_message(message.chat.id,
                         "Можно задать часовой пояс вручную или просто поделиться местоположением.",
                         reply_markup=markups.get_location_markup(message.chat.id))
        bot.register_next_step_handler(message, location_receive)
    elif message.text == '🕒 Timezone':
        bot.send_message(message.chat.id,
                         "You can specify timezone manually or just share location.",
                         reply_markup = markups.get_location_markup(message.chat.id))
        bot.register_next_step_handler(message, location_receive)
    else:  # Отмена
        bot.send_message(message.chat.id,
                         message.text,
                         reply_markup=markups.get_main_menu_markup(message.chat.id))


def language_receive(message):
    print(message)
    print(message.text)
    user = User.get(message.chat.id)

    if message.text in ('🇷🇺Русский', '🇬🇧English'):
        # set user language
        user.language_code = 'ru' if message.text == '🇷🇺Русский' else 'en'
        user.save()

        ru_text = 'Язык изменён на *русский*'
        en_text = 'Language changed to *English*'
        text = ru_text if user.language_code == 'ru' else en_text
        bot.send_message(message.chat.id,
                         text,
                         reply_markup=markups.get_main_menu_markup(message.chat.id),
                         parse_mode='Markdown')
    else:
        bot.register_next_step_handler(message, language_receive)


def location_receive(message):
    if message.location:
        tzw = tzwhere.tzwhere()
        timezone_str = tzw.tzNameAt(message.location.latitude, message.location.longitude)
        user = User.get(message.chat.id)
        user.timezone = timezone_str
        user.save()

        ru_text = f'Часовой пояс изменён на *{timezone_str}*'
        en_text = f'Timezone changed to *{timezone_str}*'
        text = ru_text if user.language_code == 'ru' else en_text
        bot.send_message(message.chat.id,
                         text,
                         reply_markup=markups.get_main_menu_markup(message.chat.id),
                         parse_mode='Markdown')
    elif message.text == 'Указать вручную':
        bot.send_message(message.chat.id, 'Выбери свой часовой пояс', reply_markup=markups.get_timezone_markup())
        bot.register_next_step_handler(message, timezone_receive)
    elif message.text == 'Specify manually':
        bot.send_message(message.chat.id, 'Choose your timezone', reply_markup=markups.get_timezone_markup())
        bot.register_next_step_handler(message, timezone_receive)
    else:
        bot.register_next_step_handler(message, location_receive)


def timezone_receive(message):
    user = User.get(message.chat.id)

    tz = 'Etc/' + message.text
    tz = tz.replace('-', '+') if '-' in tz else tz.replace('+', '-')
    if tz in pytz.all_timezones:
        user.timezone = tz
        user.save()

        ru_text = f'Часовой пояс изменён на *{tz}*'
        en_text = f'Timezone changed to *{tz}*'
        text = ru_text if user.language_code == 'ru' else en_text
        bot.send_message(message.chat.id,
                         text,
                         reply_markup=markups.get_main_menu_markup(message.chat.id),
                         parse_mode='Markdown')
    else:
        ru_text = 'Ты отправил что-то не то'
        en_text = 'You sent something wrong'
        text = ru_text if user.language_code == 'ru' else en_text

        bot.send_message(message.chat.id, text)
        bot.register_next_step_handler(message, timezone_receive)
