#!/usr/bin/env python
# -*- coding: utf-8 -*-

from telegram.ext import Updater, CommandHandler
from telegram.ext import CommandHandler, CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import telegram
import logging
import datetime
import re

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

global user_data
user_data = {}

global hilfs_dic
hilfs_dic = {}

global half_dic
half_dic = {}

global time_dic
time_dic = {}

global creator
creator = {}

global anti_spam
anti_spam = {}

global black_list
black_list = {}

global menu_dummy
menu_dummy = ""

global kb_remove
kb_remove = telegram.ReplyKeyboardRemove(False)

def start(bot, update):
    update.message.reply_text('Hi! Use /covfefe <minutes> <timername> to set a timer \nUse /abort <timer> to kill a timer \nUse /metoo <timer> to join a timer \nUse /menot <timer> to leave a timer \n Use /list <timer> to list all active timer (or all members of timer) ')

def alarm(bot, job):
    userlist = ""
    global hilfs_dic
    for key,val in hilfs_dic.iteritems():
        if val == job:
            utimername = key
    global user_data
    for u in user_data[utimername]:
        userlist = userlist + "@" + str(u) + " "
    bot.send_message(job.context, text='{} auf gehts: \n {}'.format(utimername,userlist))
    del hilfs_dic[utimername]
    global time_dic
    del time_dic[utimername]
    del anti_spam[utimername]

def halftime(bot, job):
    userlist = ""
    global half_dic
    for key,val in half_dic.iteritems():
        if val == job:
            utimername = key
    timername = utimername[9:]
    global user_data
    for u in user_data[timername]:
        userlist = userlist + "@" + str(u) + " "
    bot.send_message(job.context, text='Noch 5 Minuten bis {} !! \n {}'.format(timername,userlist))
    del half_dic[utimername]

def covfefe(bot, update, args, job_queue, chat_data):
    global kb_remove
    chat_id = update.message.chat_id
    user = update.message.from_user
    mini = datetime.datetime.combine(datetime.date.today(), datetime.time(6, 0, 0))
    maxi = datetime.datetime.combine(datetime.date.today(), datetime.time(19, 0, 0))

    try:
        timername = str(args[1])
        namecheck = re.compile('[a-zA-Z0-9_]+')
        if not namecheck.match(timername):
            bot.send_message(chat_id=update.message.chat_id, text='Gib dem Timer bitte an richtigen Namen...!!!!')
            return
    except (IndexError, ValueError):
        timername = 'covfefe'
    global hilfs_dic
    global time_dic
    if timername in hilfs_dic:
        bot.send_message(chat_id=update.message.chat_id, text='Den Timer gibts schon du Depp!!!!')
    else:
        if timername in chat_data:
            job = chat_data[timername]
            job.schedule_removal()
            del chat_data[timername]
        try:
            if ":" in str(args[0]): #check if specific time not minutes
                rawinput = str(args[0])
                rawhour = int(rawinput.split(":")[0])
                rawmin = int(rawinput.split(":")[1])
                if rawhour > 6 and rawhour < 19 and rawmin >= 0 and rawmin < 60:
                    endtime = datetime.datetime.combine(datetime.date.today(), datetime.time(rawhour, rawmin, 0))
                    time_dic[timername] = endtime
                    difftime = endtime - datetime.datetime.now()
                    due = int(difftime.total_seconds() / 60)
                    if due < 0 or due == 0:
                        bot.send_message(chat_id=update.message.chat_id, text='Gib was gscheides für die Uhrzeit ein')
                        return
                else:
                    bot.send_message(chat_id=update.message.chat_id, text='Gib was gscheides für die Uhrzeit ein')
                    return
            else:
                due = int(args[0])
                if due < 0 or due == 0:
                    bot.send_message(chat_id=update.message.chat_id, text='Gib was gscheides für die Minuten ein')
                    return
                else:
                    deltatime = datetime.datetime.now() + datetime.timedelta(minutes=due)
                    time_dic[timername] = deltatime
                    if deltatime < mini or deltatime > maxi:
                        bot.send_message(chat_id=update.message.chat_id, text='Computer says no...')
                        return

            if due > 5:
                halftimename = 'halftime_' + timername
                job = job_queue.run_once(halftime, (due-5)*60, context=chat_id)
                chat_data[halftimename] = job
                half_dic[halftimename] = job

            job = job_queue.run_once(alarm, due*60, context=chat_id)
            chat_data[timername] = job

            hilfs_dic[timername] = job

            user = update.message.from_user
            if user['username'] == 'None' or user['username'] is None:
                username = user['first_name']
            else:
                username = user['username']

            global user_data
            usernames = [username]
            user_data[timername] = usernames

            global creator
            creator[timername] = username
            bot.send_message(job.context, text='{} hat {} Timer für {}, in {} Minuten gestartet'.format(user['username'],timername,time_dic[timername].strftime("%H:%M:%S"),due))

        except (IndexError, ValueError):
            bot.send_message(chat_id=update.message.chat_id, text='Usage: /covfefe <minutes> <timername>')

def covfefe_test(bot, update, args, job_queue, chat_data):
    global kb_remove
    chat_id = update.message.chat_id
    user = update.message.from_user
    mini = datetime.datetime.combine(datetime.date.today(), datetime.time(6, 0, 0))
    maxi = datetime.datetime.combine(datetime.date.today(), datetime.time(19, 0, 0))

    try:
        timername = str(args[1])
        namecheck = re.compile('[a-zA-Z0-9_]+')
        if not namecheck.match(timername):
            bot.send_message(chat_id=update.message.chat_id, text='Gib dem Timer bitte an richtigen Namen...!!!!')
            return
    except (IndexError, ValueError):
        timername = 'covfefe'
    global hilfs_dic
    global time_dic
    if timername in hilfs_dic:
        bot.send_message(chat_id=update.message.chat_id, text='Den Timer gibts schon du Depp!!!!')
    else:
        if timername in chat_data:
            job = chat_data[timername]
            job.schedule_removal()
            del chat_data[timername]
        try:
            if ":" in str(args[0]): #check if specific time not minutes
                rawinput = str(args[0])
                rawhour = int(rawinput.split(":")[0])
                rawmin = int(rawinput.split(":")[1])
                if rawhour > 6 and rawhour < 19 and rawmin >= 0 and rawmin < 60:
                    endtime = datetime.datetime.combine(datetime.date.today(), datetime.time(rawhour, rawmin, 0))
                    time_dic[timername] = endtime
                    difftime = endtime - datetime.datetime.now()
                    due = int(difftime.total_seconds() / 60)
                    if due < 0 or due == 0:
                        bot.send_message(chat_id=update.message.chat_id, text='Gib was gscheides für die Uhrzeit ein')
                        return
                else:
                    bot.send_message(chat_id=update.message.chat_id, text='Gib was gscheides für die Uhrzeit ein')
                    return
            else:
                due = int(args[0])
                if due < 0 or due == 0:
                    bot.send_message(chat_id=update.message.chat_id, text='Gib was gscheides für die Minuten ein')
                    return
                else:
                    deltatime = datetime.datetime.now() + datetime.timedelta(minutes=due)
                    time_dic[timername] = deltatime
                    if deltatime < mini or deltatime > maxi:
                        bot.send_message(chat_id=update.message.chat_id, text='Computer says no...')
                        return
            if due > 5:
                halftimename = 'halftime_' + timername
                job = job_queue.run_once(halftime, (due-5)*60, context=chat_id)
                chat_data[halftimename] = job
                half_dic[halftimename] = job

            job = job_queue.run_once(alarm, due*60, context=chat_id)
            chat_data[timername] = job

            hilfs_dic[timername] = job

            user = update.message.from_user
            if user['username'] == 'None' or user['username'] is None:
                username = user['first_name']
            else:
                username = user['username']

            global user_data
            usernames = [username]
            user_data[timername] = usernames

            global creator
            creator[timername] = username
            keyboard = [[InlineKeyboardButton("metoo", callback_data=timername+":1"),
	                InlineKeyboardButton("menot", callback_data=timername+":0")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            update.message.reply_text('{} hat {} Timer für {}, in {} Minuten gestartet'.format(user['username'],timername,time_dic[timername].strftime("%H:%M:%S"),due), reply_markup=reply_markup)

        except (IndexError, ValueError):
            bot.send_message(chat_id=update.message.chat_id, text='Usage: /covfefe <minutes> <timername>')

def button(bot, update):
    query = update.callback_query
    timername = query.data.split(":")[0]
    yes = query.data.split(":")[1]
    user = update.callback_query.from_user

    if not bool(hilfs_dic):
        bot.send_message(chat_id=update.message.chat_id, text='Keine Timer gefunden....')
        return
    elif timername not in hilfs_dic:
        bot.send_message(chat_id=update.message.chat_id, text='Timer {} gibts net.....'.format(args[0]))
        return

    if user['username'] == 'None' or user['username'] is None:
        username = user['first_name']
    else:
        username = user['username']

    if yes == "1":
        global user_data
        if not username in user_data[timername]:
            usernames = user_data[timername]
            usernames.append(username)
            user_data[timername] = usernames
            bot.send_message(chat_id=query.message.chat_id, text='{}: {} geht mit'.format(timername, username))
        else:
            pass
#            bot.send_message(chat_id=query.message.chat_id, text='Wie oft willst noch mitgehen?')
    else:
        usernames = user_data[timername]
        if username in usernames:
            usernames.remove(username)
            user_data[timername] = usernames
            bot.send_message(chat_id=query.message.chat_id, text='{}: {} geht doch net mit'.format(timername, username))
        else:
            global anti_spam
            if timername in anti_spam:
                if not username in anti_spam[timername]:
                    bot.send_message(chat_id=query.message.chat_id, text='{}: {} geht nicht mit'.format(timername, username))
                    usernames = anti_spam[timername]
                    usernames.append(username)
                    anti_spam[timername] = usernames
                else:
                    pass
            else:
                bot.send_message(chat_id=query.message.chat_id, text='{}: {} geht nicht mit'.format(timername, username))
                usernames = anti_spam[timername]
                usernames.append(username)
                anti_spam[timername] = usernames

def abort(bot, update, args, chat_data):
    global kb_remove
    try:
        timername = str(args[0])
    except (IndexError, ValueError):
        if len(hilfs_dic) == 1:
            timername = next(iter(hilfs_dic))
        else:
            timername = 'covfefe'

    if not bool(hilfs_dic):
        bot.send_message(chat_id=update.message.chat_id, text='Keine Timer gefunden....')
        return
    elif timername not in hilfs_dic:
        bot.send_message(chat_id=update.message.chat_id, text='Timer {} gibts net.....'.format(args[0]))
        return

    user = update.message.from_user
    if user['username'] == 'None' or user['username'] is None:
        username = user['first_name']
    else:
        username = user['username']
    global creator
    if not username == creator[timername]:
        bot.send_message(chat_id=update.message.chat_id, text='Timer {} darf nur von {} aborted werden.....'.format(timername,creator[timername]))
        return

    halftimename = 'halftime_' + timername
    if halftimename in chat_data:
        job = chat_data[halftimename]
        job.schedule_removal()
        del chat_data[halftimename]
        del half_dic[halftimename]

    job = chat_data[timername]
    job.schedule_removal()
    del chat_data[timername]
    del hilfs_dic[timername]
    global time_dic
    del time_dic[timername]
    if timername in anti_spam:
        del anti_spam[timername]

    bot.send_message(chat_id=update.message.chat_id, text='{} abgebrochen!'.format(timername))

def attacke(bot, update, args, chat_data):
    global kb_remove
    try:
        timername = str(args[0])
    except (IndexError, ValueError):
        if len(hilfs_dic) == 1:
            timername = next(iter(hilfs_dic))
        else:
            timername = 'covfefe'

    if not bool(hilfs_dic):
        bot.send_message(chat_id=update.message.chat_id, text='Keine Timer gefunden....')
        return
    elif timername not in hilfs_dic:
        bot.send_message(chat_id=update.message.chat_id, text='Timer {} gibts net.....'.format(timername))
        return

    user = update.message.from_user
    if user['username'] == 'None' or user['username'] is None:
        username = user['first_name']
    else:
        username = user['username']
    global creator
    if not username == creator[timername]:
        bot.send_message(chat_id=update.message.chat_id, text='Timer {} darf nur von {} attackiert werden.....'.format(timername,creator[timername]))
        return

    userlist = ""
    global user_data
    for u in user_data[timername]:
        userlist = userlist + "@" + str(u) + " "
    bot.send_message(chat_id=update.message.chat_id, text='{} wurde attackiert, auf gehts \n {}'.format(timername,userlist))

    halftimename = 'halftime_' + timername
    if halftimename in chat_data:
        job = chat_data[halftimename]
        job.schedule_removal()
        del chat_data[halftimename]
        del half_dic[halftimename]

    job = chat_data[timername]
    job.schedule_removal()
    del chat_data[timername]
    del hilfs_dic[timername]
    global time_dic
    del time_dic[timername]
    if timername in anti_spam:
        del anti_spam[timername]

def abortion(bot, update, chat_data):
    global kb_remove
    user = update.message.from_user
    if user['username'] == 'None' or user['username'] is None:
        username = user['first_name']
    else:
        username = user['username']

    global black_list
    if not username in black_list:
        if not bool(chat_data):
            bot.send_message(chat_id=update.message.chat_id, text='Keine Timer gefunden....')
            return

        for timername in chat_data:
            job = chat_data[timername]
            job.schedule_removal()

            halftimename = 'halftime_' + timername
            if halftimename in chat_data:
                job = chat_data[halftimename]
                job.schedule_removal()
        chat_data.clear()
        hilfs_dic.clear()
        half_dic.clear()
        global time_dic
        time_dic.clear()
        anti_spam.clear()

        bot.send_message(chat_id=update.message.chat_id, text='Alle Timer abgebrochen!')
    else:
        bot.send_message(chat_id=update.message.chat_id, text='Kein Timer abgebrochen!')

def metoo(bot, update, args, chat_data):
    global kb_remove
    try:
        timername = str(args[0])
    except (IndexError, ValueError):
        if len(hilfs_dic) == 1:
            timername = next(iter(hilfs_dic))
        else:
            timername = 'covfefe'

    if not bool(hilfs_dic):
        bot.send_message(chat_id=update.message.chat_id, text='Keine Timer gefunden....')
        return
    elif timername not in hilfs_dic:
        bot.send_message(chat_id=update.message.chat_id, text='Timer {} gibts net.....'.format(args[0]))
        return

    user = update.message.from_user
    if user['username'] == 'None' or user['username'] is None:
        username = user['first_name']
    else:
        username = user['username']

    global user_data
    if not username in user_data[timername]:
        usernames = user_data[timername]
        usernames.append(username)
        user_data[timername] = usernames
        bot.send_message(chat_id=update.message.chat_id, text='{}: {} geht mit'.format(timername, username))
    else:
        bot.send_message(chat_id=update.message.chat_id, text='Wie oft willst noch mitgehen?')

def block(bot, update, args, chat_data):
    global kb_remove
    username = str(args[0])

    global black_list
    black_list[username] = username
    bot.send_message(chat_id=update.message.chat_id, text='{} wurde geblockt'.format(username))

def deblock(bot, update, args, chat_data):
    global kb_remove
    username = str(args[0])

    global black_list
    if username in black_list:
        del black_list[username]

def menot(bot, update, args, chat_data):
    global kb_remove
    try:
        timername = str(args[0])
    except (IndexError, ValueError):
        if len(hilfs_dic) == 1:
            timername = next(iter(hilfs_dic))
        else:
            timername = 'covfefe'

    if not bool(hilfs_dic):
        bot.send_message(chat_id=update.message.chat_id, text='Keine Timer gefunden....')
        return
    elif timername not in hilfs_dic:
        bot.send_message(chat_id=update.message.chat_id, text='Timer {} gibts net.....'.format(args[0]))
        return

    user = update.message.from_user
    if user['username'] == 'None' or user['username'] is None:
        username = user['first_name']
    else:
        username = user['username']

    global user_data
    usernames = user_data[timername]
    if username in usernames:
        usernames.remove(username)
        user_data[timername] = usernames
        bot.send_message(chat_id=update.message.chat_id, text='{}: {} geht doch net mit'.format(timername, username))
    else:
        bot.send_message(chat_id=update.message.chat_id, text='Du depp gehst eh net mit....')

def error(bot, update, error):
    logger.warning('Update "%s" caused error "%s"', update, error)


def list(bot, update, args, chat_data):
    global kb_remove
    try:
        userlist = ""
        timername = ""
        try:
            timername = str(args[0])
        except (IndexError, ValueError):
            if len(hilfs_dic) == 1:
                timername = next(iter(hilfs_dic))
            elif len(hilfs_dic) == 0:
                bot.send_message(chat_id=update.message.chat_id, text='Keine Timer gefunden...')
                return
            else:
                timerlist = ""
                for key in hilfs_dic:
                    timerlist = timerlist + str(key) + " "
                bot.send_message(chat_id=update.message.chat_id, text='Timer: {}'.format(timerlist))
                return

        if timername not in hilfs_dic:
            bot.send_message(chat_id=update.message.chat_id, text='Timer {} gibts net.....'.format(timername))
            return
        global user_data
        for u in user_data[timername]:
            userlist = userlist + str(u) + " "
        global time_dic
        difftime = time_dic[timername] - datetime.datetime.now()
        timeto = int(difftime.total_seconds() / 60)
        bot.send_message(chat_id=update.message.chat_id, text='{} um {}, in {} Minuten: \n Teilnehmer: {}'.format(timername,time_dic[timername].strftime("%H:%M:%S"),timeto,userlist))        
    except (IndexError, ValueError):
        timerlist = ""
        for key in hilfs_dic:
            timerlist = timerlist + str(key) + " "
        bot.send_message(chat_id=update.message.chat_id, text='Timer: {}'.format(timerlist))

def nukular(bot, update, args, chat_data):
    global kb_remove
    bot.send_photo(chat_id=update.message.chat_id, photo=open('/home/zenzmatz/Telegram_Bot/nucular_simpsons.jpg', 'rb'))

def kevin(bot, update, args, chat_data):
    global kb_remove
    bot.send_document(chat_id=update.message.chat_id, document=open('/home/zenzmatz/Telegram_Bot/nein.gif', 'rb'))

def cm(bot, update, args, chat_data):
    from decimal import Decimal, ROUND_HALF_UP
    try:
        celcius = float(args[0])
        mordor = Decimal((celcius-29)/2).to_integral_value(rounding=ROUND_HALF_UP)
        bot.send_message(chat_id=update.message.chat_id, text="*%s°C* san *%s°M*" %(celcius, mordor), parse_mode="Markdown")
    except:
        bot.send_message(chat_id=update.message.chat_id, text="irgendwos is schief gangen. kann i net umrechnen. vielleicht muast wos gscheits angeben")

def mordor(bot, update, args, chat_data):
  import requests
  import json
  import random
  from decimal import Decimal, ROUND_HALF_UP

  texts = [
      "wir ham *%s°M* in *%s*",
      "Michse denken wir *%s°M* haben in *%s*",
      "Meine innere Stimme sagt mir wir haben *%s°M* in *%s*",
      "Ein Ring sie zu knechten, ins Dunkel zu treibn...Aso, nur die Temperatur. Alsdann: *%s°M* in *%s*"
  ]

  text = random.choice(texts)

  name = ""
  for arg in args:
      name += arg
      name += " "

  try:
    response = requests.get("http://api.openweathermap.org/data/2.5/weather?q=%s&APPID=2859b9ab776091795c380b4696c1d58a&units=metric" % name)

    data = response.json()
    temp=data["main"]["temp"]
    mordor=Decimal((temp-29)/2).to_integral_value(rounding=ROUND_HALF_UP)#round((temp-29)/2)
    tmp_str = text % (mordor, data["name"])
    bot.send_message(chat_id=update.message.chat_id, text=tmp_str, parse_mode="Markdown")
  except:
    bot.send_message(chat_id=update.message.chat_id, text="irgendwos is schief gangen. hob kane wetterdaten für di")
    bot.send_message(chat_id=update.message.chat_id, text="probiers mal mit /mordor <die ortschaft>")

def main():
    """Run bot."""
    updater = Updater("TOKEN")

    global users
    users = []
   
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("covfefe", covfefe_test, pass_args=True, pass_job_queue=True, pass_chat_data=True))
    dp.add_handler(CommandHandler("covfefe_test", covfefe_test, pass_args=True, pass_job_queue=True, pass_chat_data=True))
    dp.add_handler(CommandHandler("abort", abort, pass_args=True, pass_chat_data=True))
    dp.add_handler(CommandHandler("abortion", abortion, pass_chat_data=True))
    dp.add_handler(CommandHandler("metoo", metoo, pass_args=True, pass_chat_data=True))
    dp.add_handler(CommandHandler("menot", menot, pass_args=True, pass_chat_data=True))
    dp.add_handler(CommandHandler("list", list, pass_args=True, pass_chat_data=True))
    dp.add_handler(CommandHandler("nukular", nukular, pass_args=True, pass_chat_data=True))
    dp.add_handler(CommandHandler("kevin", kevin, pass_args=True, pass_chat_data=True))
    dp.add_handler(CommandHandler("attacke", attacke, pass_args=True, pass_chat_data=True))
    dp.add_handler(CommandHandler("block", block, pass_args=True, pass_chat_data=True))
    dp.add_handler(CommandHandler("deblock", deblock, pass_args=True, pass_chat_data=True))
    dp.add_handler(CommandHandler("mordor", mordor, pass_args=True, pass_chat_data=True))
    dp.add_handler(CommandHandler("cm", cm, pass_args=True, pass_chat_data=True))

    dp.add_handler(CallbackQueryHandler(button))

    dp.add_error_handler(error)

    updater.start_polling()

    updater.idle()

if __name__ == '__main__':
    main()
