import time
from bot import bot
from users import intro
from utils.database import init_database
from timeloop import Timeloop
from checks.check_users import check_users
import datetime


tl = Timeloop()
last_check_utc = datetime.datetime.strptime(datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M"), "%Y-%m-%d %H:%M")  # поправить


@tl.job(interval=datetime.timedelta(minutes=1))
def check():
    global last_check_utc
    last_check_utc = check_users(last_check_utc)


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
