from bot import bot
import datetime
import pytz


def remove_markup(chat_id, message_id):
    bot.edit_message_reply_markup(chat_id, message_id=message_id, reply_markup=None)


def get_native_datetime(date, time, timezone):
    return pytz.timezone(timezone).localize(
                datetime.datetime.strptime(f'{date} {time}', "%Y-%m-%d %H:%M"), is_dst=None)


def get_schedule(week_days, time_array, timezone):
    user_date_now = datetime.datetime.now(tz=pytz.timezone(timezone)).date()
    schedule_native = []
    for week_day in week_days:
        if week_day > user_date_now.weekday():
            first_day = user_date_now + datetime.timedelta(week_day - user_date_now.weekday())
        else:
            first_day = user_date_now + datetime.timedelta(7 - user_date_now.weekday() + week_day)

        second_day = first_day + datetime.timedelta(7)
        third_day = second_day + datetime.timedelta(7)

        for time in time_array:
            first_datetime_native, second_datetime_native, third_datetime_native = [
                get_native_datetime(str(day), time, timezone) for day in
                [first_day, second_day, third_day]]

            schedule_native.extend([first_datetime_native, second_datetime_native, third_datetime_native])

    schedule_native.sort()
    schedule_utc = [native_datetime.astimezone(pytz.utc) for native_datetime in schedule_native]
    return schedule_native, schedule_utc
