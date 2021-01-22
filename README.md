# Inspector Habit

Inspector Habit is a Telegram bot which helps people to develop good habits and break bad ones, fining them for laziness and weakness.


## Getting Started

Inspector Habit bot requires Python 3.7 and packages specified in ```requirements.txt```.

You can install them with

```
pip install -r requirements.txt
```

Before you start Inspector Habit it is necessary to create ```.env``` file:

```
touch .env
```

and fill in this file according to the example below:

```
DEBUG = True

BOT_TOKEN = XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
ADMIN_ID = XXXXXXXXXXX

DATABASE_URL = postgres://XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

DB_NAME = inspector_habit_db
DB_USER = user
DB_PASSWORD = XXXXXXXXXXX
DB_HOST = localhost

PROXY = https://XXX.XXX.XXX.XXX:XXXX

PROVIDER_TOKEN = XXXXXXXXXXX:XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

```

```DEBUG``` should be **False** in prod

```BOT_TOKEN``` is the token got from [BotFather](https://t.me/BotFather)

```ADMIN_ID``` is the telegram id of the admin

```DATABASE_URL``` is used to access the database in prod

```DB_NAME```, ```DB_USER```, ```DB_PASSWORD``` and  ```DB_HOST```  are used to access the database in dev

```PROXY``` is used if Telegram is blocked in your country (also uncomment appropriate code in ***bot.py***)

```PROVIDER_TOKEN``` is used for payments (see ***fines/payments***), you can connect the payment provider to your bot via [BotFather](https://t.me/BotFather)

Then you can start Inspector Habit with this command:

```
python main.py
```


## Use case

Let's see how [the Dude](https://en.wikipedia.org/wiki/The_Big_Lebowski) could discipline himself with Inspector Habit and of course [Walter](https://en.wikipedia.org/wiki/The_Big_Lebowski).

First of all, the Dude starts Inspector Habit and assigns the habit he wants to develop.

![1](https://raw.githubusercontent.com/Macket/inspector_habit_bot/master/img/readme/1.png)

Then he chooses days and time for checks, specifies his timezone and selects the amount of the fine.

![2](https://raw.githubusercontent.com/Macket/inspector_habit_bot/master/img/readme/2.png)

Also the Dude has to choose where his money will go: to a friend or to charity.

![3](https://raw.githubusercontent.com/Macket/inspector_habit_bot/master/img/readme/3.png)

Of course, the Dude chooses **To a friend**.

![4](https://raw.githubusercontent.com/Macket/inspector_habit_bot/master/img/readme/4.png)

And asks Walter to become his judge.

![5](https://raw.githubusercontent.com/Macket/inspector_habit_bot/master/img/readme/5.png)

When Walter becomes the judge he can also **Sign up** to develop his own habits.

![6](https://raw.githubusercontent.com/Macket/inspector_habit_bot/master/img/readme/6.png)

The Dude gets notified about it and now he can see the menu.

![7](https://raw.githubusercontent.com/Macket/inspector_habit_bot/master/img/readme/7.png)

![8](https://raw.githubusercontent.com/Macket/inspector_habit_bot/master/img/readme/8.png)

When check time is coming, the Dude gets the following message from Inspector Habit.

![9](https://raw.githubusercontent.com/Macket/inspector_habit_bot/master/img/readme/9.png)

It seems that he overslept and Walter is trying to remind the Dude about his promise.

![10](https://raw.githubusercontent.com/Macket/inspector_habit_bot/master/img/readme/10.png)

![11](https://raw.githubusercontent.com/Macket/inspector_habit_bot/master/img/readme/11.png)

But it's too late. Dude taps **❌ No** and gets fined.

![12](https://raw.githubusercontent.com/Macket/inspector_habit_bot/master/img/readme/12.png)

If the Dude forgets to pay fine, Walter will remind him.

![13](https://raw.githubusercontent.com/Macket/inspector_habit_bot/master/img/readme/13.png)

![14](https://raw.githubusercontent.com/Macket/inspector_habit_bot/master/img/readme/14.png)

Once the Dude pays, Walter taps **💰 Fines paid** and everything goes on.