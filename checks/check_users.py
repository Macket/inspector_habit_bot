from datetime import datetime
from telebot import types
from utils.database import execute_database_command
from bot import bot
from users.models import User
from checks.models import Check
from habits.models import Habit
from checks.utils import CheckStatus
from checks import markups
from fines.handlers import user_violations, user_violations_with_judge
from fines.markups import get_punishment_markup
import ast
import random
from users.utils import get_user_naming


ru_success_phrases = ['Красавчик👍', 'Хорооош👍', 'Еееее', 'Крутяк😊', 'Капитальный красавчик👍',
                      'А я уже было подумал, что ты лентяй😂', 'Лучший!!!', 'Так держать👍']
en_success_phrases = ['Cool👍', 'You are pretty good👍', 'Yeah!!!', 'Best!',
                      'And I already thought you were lazy😂', 'Keep it up👍']

success_stickers = ['CAADAgADawIAAsY4fgsDhbjMBJlV4AI',
                    'CAADAgADugIAAsY4fgu4uDPJXXphTgI',
                    'CAADAgADUgADYIltDBp238_XJHBwAg',
                    'CAADAgADFQkAAgi3GQLidaybScg8wwI',
                    'CAADAgAD8wAEOKAKN5v1aQrj1EgC',
                    'CAADBQADbgMAAukKyAN8NA8_2uwEbRYE',
                    'CAADBQADbwMAAukKyAOvzr7ZArpddBYE',
                    'CAADBQADzwMAAukKyAPJ6kGu2BGu0hYE',
                    'CAADAgADCgkAAgi3GQL7DdMy7QMLYhYE',
                    'CAADAgADVgkAAgi3GQKZSn_np-jbNRYE']

fail_stickers = ['CAADAgADzwEAAvnkbAABsjFAs3iK3fgC',
                 'CAADAgADYQAD6u8-Cu07kxWOZDfKAg',
                 'CAADAgADkAIAAsY4fgsQVTK1QgZFoQI',
                 'CAADAgADZwkAAnlc4gmuNXdMkJqu5wI',
                 'CAADAgADuwEAAvFCvwUHymbGsZgiLQI',
                 'CAADAgADDAkAAgi3GQKIOO6UHoJovxYE',
                 'CAADAgADEwkAAgi3GQKQqZ1Of22QNBYE',
                 'CAADAgADWwkAAgi3GQJorlW1m4id3xYE',
                 'CAADAgADhgADE-ZSAcQNAW3NGZOSFgQ',
                 'CAADAgADjAgAAnlc4gmFDSBf_qyCOxYE']

remind_stickers = ['CAADAgAD2AIAAsY4fgtkktnDjo_g_hYE',
                   'CAADAgADCwcAAnlc4gnFFPkWJcR13hYE',
                   'CAADAQADMAcAAr-MkATOOPvgQ3A3LhYE',
                   'CAADAgADTgQAAmvEygo8YG7sYoE4WhYE',
                   'CAADAgADiAgAAnlc4gkZZtd2m1gdLRYE']


def check_users(last_check_utc):
    now_utc = datetime.strptime(datetime.utcnow().strftime("%Y-%m-%d %H:%M"), "%Y-%m-%d %H:%M")  # Нужно исправить
    checks = execute_database_command('''SELECT c.id, c.habit_id, c.datetime_native, c.datetime_utc, h.label, h.user_id, h.judge FROM
    checks c JOIN habits h ON c.habit_id = h.id JOIN users u ON u.id = h.user_id 
    WHERE c.datetime_utc <= %s AND c.datetime_utc > %s AND c.status=%s;
    ''', (now_utc, last_check_utc, CheckStatus.PENDING.name))[0]
    for check in checks:
        check_id, habit_id, datetime_native, datetime_utc, label, user_id, judge_id = check
        c = Check(habit_id, datetime_native, datetime_utc, CheckStatus.CHECKING.name, check_id)
        c.save()

        user = User.get(user_id)
        ru_text = f'Ты обещал "*{label}*". Ты держишь своё слово?\n\n' \
                  f'Учти, что за ответ "❌ Нет" нужно будет заплатить штраф'
        en_text = f'You promised "*{label}*". Are you keeping your promise?\n\n' \
                  f'Note that you will have to pay a fine for the answer "❌ No"'
        text = ru_text if user.language_code == 'ru' else en_text

        try:
            bot.send_message(user_id,
                             text,
                             reply_markup=markups.get_check_inline_markup(user_id, check_id),
                             parse_mode='Markdown')
        except Exception:
            pass

        if judge_id:
            judge = User.get(judge_id)
            ru_text_judge = f'{get_user_naming(user, "Твой друг")} обещал "*{label}*"'
            en_text_judge = f'{get_user_naming(user, "Your friend")} promised "*{label}*"'
            text_judge = ru_text_judge if judge.language_code == 'ru' else en_text_judge

            try:
                bot.send_message(judge_id,
                                 text_judge,
                                 reply_markup=markups.get_kick_lazy_ass_markup(judge_id, habit_id),
                                 parse_mode='Markdown')
            except Exception as e:
                print(e)
    return now_utc


@bot.callback_query_handler(func=lambda call: call.data.startswith('@@CHECKS'))
def handle_check_query(call):
    data = ast.literal_eval(call.data.split('/')[1])

    check = Check.get(data['check_id'])
    check.status = data['status']
    check.save()

    habit = Habit.get(check.habit_id)

    user = User.get(call.message.chat.id)

    called_button_label = call.message.json['reply_markup']['inline_keyboard'][0][0]['text'] if \
        data['status'] == CheckStatus.SUCCESS.name else \
        call.message.json['reply_markup']['inline_keyboard'][0][1]['text']

    try:
        bot.edit_message_text(chat_id=call.message.chat.id,
                              text=call.message.text,
                              message_id=call.message.message_id,
                              reply_markup=markups.get_check_result_inline_markup(called_button_label),
                              parse_mode='HTML')
    except:
        pass

    if data['status'] == CheckStatus.SUCCESS.name:
        user.score += habit.fine
        user.save()

        ru_text = f'{random.choice(ru_success_phrases)}\n\n*+{habit.fine} очков*'
        en_text = f'{random.choice(en_success_phrases)}\n\n*+{habit.fine} points*'
        text = ru_text if user.language_code == 'ru' else en_text

        try:
            bot.send_message(call.message.chat.id, text, parse_mode='Markdown')
            bot.send_sticker(call.message.chat.id, random.choice(success_stickers))
        except:
            pass

        if habit.judge:
            judge = User.get(habit.judge)

            ru_text_judge = f'{get_user_naming(user, "Твой друг")} выполнил обещание *{habit.label}*'
            en_text_judge = f'{get_user_naming(user, "Your friend")} fulfilled the promise *{habit.label}*'
            text_judge = ru_text_judge if judge.language_code == 'ru' else en_text_judge

            try:
                bot.send_message(judge.id, text_judge, parse_mode='Markdown')
            except Exception:
                pass
    else:
        if habit.judge:
            user_violations_with_judge(user.id, habit.judge)
        else:
            try:
                bot.send_sticker(call.message.chat.id, random.choice(fail_stickers))
            except:
                pass
            user_violations(call.message)

    suggest_new_habit(user, habit)


@bot.callback_query_handler(func=lambda call: call.data.startswith('@@KICK_LAZY_ASS'))
def handle_kick_lazy_ass_query(call):
    habit_id = int(call.data.split('/')[1])
    habit = Habit.get(habit_id)
    user = User.get(habit.user_id)

    judge = User.get(call.message.chat.id)
    ru_text = f'{get_user_naming(judge, "Твой друг")} ' \
              f'напоминает тебе, что ты обещал "*{habit.label}*"'
    en_text = f'{get_user_naming(judge, "Your friend")} ' \
              f'reminds you that you promised "*{habit.label}*"'
    text = ru_text if user.language_code == 'ru' else en_text
    try:
        bot.send_message(user.id, text, parse_mode='Markdown')
        bot.send_sticker(user.id, random.choice(remind_stickers))
    except Exception:
        pass

    try:
        bot.send_message(judge.id, 'Сделано!')
    except:
        pass


def take_points_from_debtors():
    debtors = execute_database_command('''SELECT u.id, SUM(h.fine) FROM users u JOIN 
    habits h ON u.id = h.user_id JOIN checks c ON c.habit_id = h.id 
    WHERE c.status = 'FAIL' GROUP BY u.id;
    ''', (CheckStatus.SUCCESS.name,))[0]

    for debtor in debtors:
        user = User.get(debtor[0])
        user.score -= debtor[1]
        user.save()

        ru_text = f'Должникам по долгам их!\n\nТвой долг по штрафам составляет *${debtor[1]}*\n\n*-{debtor[1]} очков*'
        en_text = f'Debtors must be punished!\n\nYour debt on fines *${debtor[1]}*\n\n*-{debtor[1]} points*'
        text = ru_text if user.language_code == 'ru' else en_text

        try:
            bot.send_message(user.id, text, parse_mode='Markdown')
        except Exception:
            pass

        # TODO убрать дублирование с user_violations
        violations = user.get_fines()

        if violations:
            ru_report = 'Ты обвиняешься в следующих нарушениях:\n\n'
            en_report = 'You are charged with the following violations:\n\n'
            report = ru_report if user.language_code == 'ru' else en_report

            for violation in violations:
                label = violation[0]
                datetime_native = violation[1]
                fine = violation[2]

                report += f'_{datetime_native}_ {label} *${fine}*\n\n'
                report += 'Выбери наказание' if user.language_code == 'ru' else 'Choose punishment'

            bot.send_message(user.id,
                             text=report,
                             parse_mode='Markdown',
                             reply_markup=get_punishment_markup(user.id))


def rate_users():
    rating = execute_database_command(
        'SELECT id, score FROM users ORDER BY score DESC;',
        (CheckStatus.SUCCESS.name,))[0]

    total = len(rating)

    for place, record in enumerate(rating, 1):
        u = User.get(record[0])

        ru_text = f'Твоё место в рейтинге: *{place}/{total}*\n\n' \
                  f'Количество очков: *{record[1]}*'
        en_text = f'Your place in rating *{place}/{total}*\n\n*' \
                  f'Score: *{record[1]}*'
        text = ru_text if u.language_code == 'ru' else en_text

        try:
            bot.send_message(u.id, text, parse_mode='Markdown')
        except Exception:
            pass


Jason_Statham_sticker_pack = ['CAADBAADiAIAAoVpUQWeomfO2K5XagI',
                              'CAADBAADuQIAAoVpUQVxWNshtJbFxwI',
                              'CAADBAADjgIAAoVpUQWFTHDH5-5gLQI',
                              'CAADBAADkwIAAoVpUQUWaJtDeSffxQI',
                              'CAADBAADlQIAAoVpUQXTjabcb8sc5QI',
                              'CAADBAADlwIAAoVpUQU_mDUvVNQrCgI',
                              'CAADBAADnQIAAoVpUQUzSVrPUoUblQI',
                              'CAADBAADnwIAAoVpUQUv6h29VDUm0wI',
                              'CAADBAADoQIAAoVpUQUp6ATKJ0CCwgI',
                              'CAADBAADowIAAoVpUQUe179jKBFMmAI',
                              'CAADBAADpQIAAoVpUQX5pkA5Un8m9gI',
                              'CAADBAADpwIAAoVpUQULoMsJeHJ5dQI',
                              'CAADBAADqQIAAoVpUQV8lGGpxy7bLwI',
                              'CAADBAADqwIAAoVpUQVnjHeRzWVcfgI',
                              'CAADBAADrQIAAoVpUQWCbdLOmJiC2wI',
                              'CAADBAADrwIAAoVpUQWj5VIseT0VmwI',
                              'CAADBAADsQIAAoVpUQXeqyOsHpec8wI',
                              'CAADBAADswIAAoVpUQWZdNjc6_LJNwI',
                              'CAADBAADtQIAAoVpUQWcyMnP-eLZdgI',
                              'CAADBAADtwIAAoVpUQWPap6lxRn7lgI',
                              'CAADBAADuwIAAoVpUQWQWheljG3tRQI']

Jason_Statham_quotes_ru = ['В любом процессе важна не скорость, а удовольствие.',
                           'Не так важно, как тебя ударили, - важно, как ты встал и ответил.',
                           'Если стараться обходить все неприятности, то можно пройти мимо всех удовольствий.',
                           'Ты свободен, а значит, всерьёз за себя отвечаешь.',
                           'Молчание - лучший способ ответа на бессмысленные вопросы.',
                           'Тем, кого вдохновляют мои герои, не помешало бы лишний раз подумать.',
                           'Живи в свое удовольствие, но не забывай про тех кто рядом.',
                           'Будь самим собой, имей свою точку зрения, умей постоять за себя и за своих близких и тебя будут уважать.',
                           'У тебя есть враги? Хорошо. Значит, в своей жизни ты что-то когда-то отстаивал.',
                           'Если вы идете сквозь ад — идите, не останавливаясь.',
                           'Умный человек не делает сам все ошибки — он дает шанс и другим.',
                           'Любой кризис — это новые возможности.',
                           'Успех — это способность шагать от одной неудачи к другой, не теряя энтузиазма.',
                           'Сокол высоко поднимается, когда летит против ветра, а не по ветру.',
                           'Глуп тот человек, который никогда не меняет своего мнения.',
                           'Когда орлы молчат, болтают попугаи.']

Jason_Statham_quotes_en = ["I've come from nowhere, and I'm not shy to go back.",
                           "You only get one shot in your life, and you might as well push yourself and try things.",
                           "Revenge is a caustic thing. I say, breathe in, breathe deeply, let it go.",
                           "How long you can continue to be good at something is how much you believe in yourself and how much hard work you do with the training.",
                           "If you're going to do something, do it with style!",
                           "Looking good and feeling good go hand in hand. If you have a healthy lifestyle, your diet and nutrition are set, and you're working out, you're going to feel good.",
                           "Success is not final, failure is not fatal: it is the courage to continue that counts.",
                           "You have enemies? Good. That means you've stood up for something, sometime in your life.",
                           "Men occasionally stumble over the truth, but most of them pick themselves up and hurry off as if nothing ever happened",
                           "If you are going through hell, keep going.",
                           "My tastes are simple: I am easily satisfied with the best",
                           "History will be kind to me for I intend to write it."]


def motivate_users_with_Jason_Statham():
    users = execute_database_command('SELECT id, language_code FROM users;')[0]

    for user in users:
        user_id = user[0]
        language_code = user[1]

        quote = random.choice(Jason_Statham_quotes_ru) + '\n\n*Джейсон Стэтхэм*' if language_code == 'ru' else \
            random.choice(Jason_Statham_quotes_en) + '\n\n*Jason Statham*'

        sticker = random.choice(Jason_Statham_sticker_pack)

        try:
            bot.send_message(user_id, quote, parse_mode='Markdown')
            bot.send_sticker(user_id, sticker)
        except Exception:
            pass


def suggest_new_habit(user, old_habit):
    print(old_habit.get_remaining_checks())
    if not old_habit.get_remaining_checks():
        ru_text = f'Что ж, ты завершил работу над привычкой *{old_habit.label}*. ' \
                  f'Пора назначить новую!'
        en_text = f'Well, you finished the habit *{old_habit.label}*. ' \
                  f"It's time to assign the new one!"
        text = ru_text if user.language_code == 'ru' else en_text

        try:
            bot.send_message(user.id,
                             text,
                             reply_markup=markups.get_suggest_new_habit_markup(user.id),
                             parse_mode='Markdown')
        except:
            pass
