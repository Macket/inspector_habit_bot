import time
import datetime
from timeloop import Timeloop
from bot import bot
from users import intro
from users import new_habit
from users import contact_developers
from users import settings
from habits import handlers
from fines import payment, handlers
from users.utils import get_sticker_id
from utils.database import init_database
from checks.check_users import check_users, take_points_from_debtors, rate_users, motivate_users_with_Jason_Statham


tl = Timeloop()
last_check_utc = datetime.datetime.strptime(datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M"), "%Y-%m-%d %H:%M")  # TODO поправить
counter = 0


@tl.job(interval=datetime.timedelta(minutes=1))
def check_users_job():
    global last_check_utc
    last_check_utc = check_users(last_check_utc)


@tl.job(interval=datetime.timedelta(days=1))
def take_points_from_debtors_job():
    take_points_from_debtors()


# @tl.job(interval=datetime.timedelta(hours=20))
# def motivate_users_with_Jason_Statham_job():
#     motivate_users_with_Jason_Statham()


@tl.job(interval=datetime.timedelta(days=1))
def rate_users_job():
    global counter
    if counter == 7:
        counter = 0
        rate_users()
    else:
        counter += 1


init_database()

tl.start()

while True:
    try:
        time.sleep(1)
    except KeyboardInterrupt:
        tl.stop()
        print('stop')
    break

while True:
    try:
        bot.polling(none_stop=True, interval=1, timeout=0)
    except:
        time.sleep(10)
