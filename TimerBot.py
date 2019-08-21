#!/usr/bin/env python
# -*- coding: utf-8 -*-

from telegram.ext import Updater, CommandHandler
from telegram.ext import CommandHandler, CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import telegram
import logging
import datetime
import re
import AdvancedHTMLParser
import requests
import json
import random
import difflib
from decimal import Decimal, ROUND_HALF_UP

#enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

#define class
class TimerBot:
    def __init__(self, token):
        self.token = token
        self.user_data = {}
        self.hilfs_dic = {}
        self.half_dic = {}
        self.time_dic = {}
        self.creator = {}
        self.anti_spam = {}
        self.black_list = {}

        with open('./resources/city.list.json', 'r', encoding="utf8") as f:
            self.city_list = json.load(f)
        
    def main(self):
        """Run bot."""
        updater = Updater(self.token) #for telegram v11.0 and v13.0
#        updater = Updater(self.token, use_context=True) # for telegram v12.0
        self.users = []
       
        dp = updater.dispatcher
    
        dp.add_handler(CommandHandler("start", self.start))
        dp.add_handler(CommandHandler("covfefe", self.covfefe, pass_args=True, pass_job_queue=True, pass_chat_data=True))
        dp.add_handler(CommandHandler("abort", self.abort, pass_args=True, pass_chat_data=True))
        dp.add_handler(CommandHandler("abortion", self.abortion, pass_chat_data=True))
        dp.add_handler(CommandHandler("metoo", self.metoo, pass_args=True, pass_chat_data=False))
        dp.add_handler(CommandHandler("menot", self.menot, pass_args=True, pass_chat_data=False))
        dp.add_handler(CommandHandler("list", self.list, pass_args=True, pass_chat_data=False))
        dp.add_handler(CommandHandler("nukular", self.nukular, pass_args=False, pass_chat_data=False))
        dp.add_handler(CommandHandler("kevin", self.kevin, pass_args=False, pass_chat_data=False))
        dp.add_handler(CommandHandler("attacke", self.attacke, pass_args=True, pass_chat_data=True))
        dp.add_handler(CommandHandler("block", self.block, pass_args=True, pass_chat_data=False))
        dp.add_handler(CommandHandler("deblock", self.deblock, pass_args=True, pass_chat_data=False))
        dp.add_handler(CommandHandler("blocklist", self.blocklist, pass_args=True, pass_chat_data=False))
        dp.add_handler(CommandHandler("wetter", self.weather, pass_args=True, pass_chat_data=False))
        dp.add_handler(CommandHandler("mordor", self.mordor, pass_args=True, pass_chat_data=False))
        dp.add_handler(CommandHandler("cm", self.cm, pass_args=True, pass_chat_data=False))
        dp.add_handler(CallbackQueryHandler(self.button))

        dp.add_error_handler(self.error)

        updater.start_polling()
        updater.idle()

#   sub functions, used in main functions:
    def createTimer(self, bot, job, messageText, halfTime = False):
        userlist = ""
        for key,val in self.half_dic.items() if halfTime else self.hilfs_dic.items():
            if val == job:
                utimername = key
        timername = utimername[9:] if halfTime else utimername
        userlist = "@" + " @".join(self.user_data[timername])
        bot.send_message(job.context, text=messageText.format(timername,userlist))
        if halfTime:
            del self.half_dic[utimername]
        else:
            del self.hilfs_dic[utimername]
            del self.time_dic[utimername]
            del self.user_data[utimername]

    def createTimerName(self, bot, update, args):
        try:
            timername = str(args[1:]).strip('[]').replace('u\'','').replace('\'','').replace(',','')
            if timername == "":
                raise ValueError
        except (IndexError, ValueError):
            timername = 'covfefe'
        if timername in self.hilfs_dic:
            bot.send_message(chat_id=update.message.chat_id, text='Den Timer "{}" gibts schon!!!!'.format(timername))
            return
        return timername

    def getTimerName(self, args):
        try:
            timername = str(args[0:]).strip('[]').replace('u\'','').replace('\'','').replace(',','')
            if timername == "":
                raise ValueError
        except (IndexError, ValueError):
            if len(self.hilfs_dic) == 1:
                timername = next(iter(self.hilfs_dic))
            else:
                timername = 'covfefe'
        return timername
    
    def checkTimer(self, bot, update, timername):
        if not bool(self.hilfs_dic):
            bot.send_message(chat_id=update.message.chat_id, text='Keine Timer gefunden....')
            return True
        elif timername not in self.hilfs_dic:
            bot.send_message(chat_id=update.message.chat_id, text='Timer "{}" gibts net.....'.format(timername))
            return True
        else:
            return False

    def createUser(self, update):
        user = update.message.from_user
        if user['username'] == 'None' or user['username'] is None:
            username = user['first_name']
        else:
            username = user['username']
        return username
        
    def cleanupEarly(self, timername, chat_data):
        halftimename = 'halftime_' + timername
        if halftimename in chat_data:
            job = chat_data[halftimename]
            job.schedule_removal()
            del chat_data[halftimename]
            del self.half_dic[halftimename]
            del self.user_data[halftimename]
    
        job = chat_data[timername]
        job.schedule_removal()
        del chat_data[timername]
        del self.hilfs_dic[timername]
        del self.time_dic[timername]
        del self.user_data[timername]
        if timername in self.anti_spam:
            del self.anti_spam[timername]

    def alarm(self, bot, job):
        messageText = '"{}" auf gehts: \n {}'
        self.createTimer(bot, job, messageText)

    def halftime(self, bot, job):
        messageText = 'Noch 5 Minuten bis "{}" !! \n {}'
        self.createTimer(bot, job, messageText, True)

    def joinTimer(self, bot, chatId, username, timername):
        if not username in self.user_data[timername]:
            self.user_data[timername].append(username)
            try:
                if username in self.anti_spam[timername]:
                    self.anti_spam[timername].remove(username)
            except (KeyError):
                self.anti_spam[timername] = []
            bot.send_message(chat_id=chatId, text='"{}": {} geht mit'.format(timername, username))
        else:
            bot.send_message(chat_id=chatId, text='Wie oft willst noch mitgehen?')
    
    def leaveTimer(self, bot, chatId, username, timername):
        if username in self.user_data[timername]:
            self.user_data[timername].remove(username)
            try:
                self.anti_spam[timername].append(username)
            except (KeyError):
                self.anti_spam[timername] = []

            bot.send_message(chat_id=chatId, text='"{}": {} geht doch net mit'.format(timername, username))
        else:
            if not username in self.anti_spam[timername]:
                self.anti_spam[timername].append(username)
                bot.send_message(chat_id=chatId, text='"{}": {} geht net mit'.format(timername, username))
            else:
                bot.send_message(chat_id=chatId, text='Du gehst eh net mit....')

#   main functions, called by main
    def start(self, bot, update):
        update.message.reply_text('Hi! Use /covfefe <minutes> <timername> to set a timer \nUse /abort <timer> to kill a timer \nUse /metoo <timer> to join a timer \nUse /menot <timer> to leave a timer \n Use /list <timer> to list all active timer (or all members of timer) ')

    def covfefe(self, bot, update, args, job_queue, chat_data):
        chat_id = update.message.chat_id
        user = update.message.from_user
    
        timername = self.createTimerName(bot, update, args)
        if timername is None:
            return
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
                    if rawhour > 0 and rawhour < 24 and rawmin >= 0 and rawmin < 60:
                        endtime = datetime.datetime.combine(datetime.date.today(), datetime.time(rawhour, rawmin, 0))
                        self.time_dic[timername] = endtime
                        difftime = endtime - datetime.datetime.now()
                        due = int(difftime.total_seconds() / 60)
                        if due < 0 or due == 0:
                            bot.send_message(chat_id=update.message.chat_id, text='A bissl mehr Zeit muast den anderen schon lassen')
                            return
                    else:
                        bot.send_message(chat_id=update.message.chat_id, text='Was gscheides für die Uhrzeit solltest schon angeben')
                        return
                else:
                    due = int(args[0])
                    if due < 0 or due == 0:
                        bot.send_message(chat_id=update.message.chat_id, text='A bissl mehr Zeit muast den anderen schon lassen')
                        return
                    else:
                        deltatime = datetime.datetime.now() + datetime.timedelta(minutes=due)
                        self.time_dic[timername] = deltatime
                if due > 5:
                    halftimename = 'halftime_' + timername
                    job = job_queue.run_once(self.halftime, (due-5)*60, context=chat_id)
                    chat_data[halftimename] = job
                    self.half_dic[halftimename] = job
    
                job = job_queue.run_once(self.alarm, due*60, context=chat_id)
                chat_data[timername] = job
    
                self.hilfs_dic[timername] = job
                
                username = self.createUser(update)
                self.user_data[timername] = [username]
                self.creator[timername] = username

                keyboard = [[InlineKeyboardButton("metoo", callback_data=timername+":1"),
                             InlineKeyboardButton("menot", callback_data=timername+":0")]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                update.message.reply_text('{} hat "{}" Timer für {}, in {} Minuten gestartet'.format(user['username'],timername,self.time_dic[timername].strftime("%H:%M:%S"),due), reply_markup=reply_markup)
    
            except (IndexError, ValueError):
                bot.send_message(chat_id=update.message.chat_id, text='Usage: /covfefe <minutes> <timername>')

    def button(self, bot, update):
        query = update.callback_query
        timername = query.data.split(":")[0]
        yes = query.data.split(":")[1]
        user = update.callback_query.from_user

        if self.checkTimer(bot, update, timername):
            return
    
        if user['username'] == 'None' or user['username'] is None:
            username = user['first_name']
        else:
            username = user['username']

        if yes == "1":
            self.joinTimer(bot, query.message.chat_id, username, timername)
        else:
            self.leaveTimer(bot, query.message.chat_id, username, timername)

    def abort(self, bot, update, args, chat_data):
        timername = self.getTimerName(args)
        if self.checkTimer(bot, update, timername):
            return
    
        username = self.createUser(update)
        
        if not username == self.creator[timername]:
            bot.send_message(chat_id=update.message.chat_id, text='Timer "{}" darf nur von {} aborted werden.....'.format(timername,self.creator[timername]))
            return
    
        self.cleanupEarly(timername, chat_data)

        bot.send_message(chat_id=update.message.chat_id, text='"{}" abgebrochen!'.format(timername))

    def attacke(self, bot, update, args, chat_data):
        timername = self.getTimerName(args)
        if self.checkTimer(bot, update, timername):
            return
    
        username = self.createUser(update)
        
        if not username == self.creator[timername]:
            bot.send_message(chat_id=update.message.chat_id, text='Timer "{}" darf nur von {} attackiert werden.....'.format(timername,self.creator[timername]))
            return
    
        userlist = ""
        userlist = "@" + " @".join(self.user_data[timername])
        bot.send_message(chat_id=update.message.chat_id, text='"{}" wurde attackiert, auf gehts \n {}'.format(timername,userlist))
    
        self.cleanupEarly(timername, chat_data)
    
    def abortion(self, bot, update, chat_data):
        username = self.createUser(update)
        if not username in self.black_list:
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
            self.hilfs_dic.clear()
            self.half_dic.clear()
            self.time_dic.clear()
            self.anti_spam.clear()
            self.user_data.clear()
    
            bot.send_message(chat_id=update.message.chat_id, text='Alle Timer abgebrochen!')
        else:
            bot.send_message(chat_id=update.message.chat_id, text='Kein Timer abgebrochen!')

    def metoo(self, bot, update, args):
        timername = self.getTimerName(args)
        if self.checkTimer(bot, update, timername):
            return
    
        username = self.createUser(update)
        self.joinTimer(bot, update.message.chat_id, username, timername)

    def menot(self, bot, update, args):
        timername = self.getTimerName(args)
        if self.checkTimer(bot, update, timername):
            return
    
        username = self.createUser(update)
        self.leaveTimer(bot, update.message.chat_id, username, timername)

    def list(self, bot, update, args):
        try:
            userlist = ""
            timername = ""
            try:
                timername = str(args[0:]).strip('[]').replace('u\'','').replace('\'','').replace(',','')
                if timername == "":
                    raise ValueError
            except (IndexError, ValueError):
                if len(self.hilfs_dic) == 1:
                    timername = next(iter(self.hilfs_dic))
                elif len(self.hilfs_dic) == 0:
                    bot.send_message(chat_id=update.message.chat_id, text='Keine Timer gefunden...')
                    return
                else:
                    timerlist = ""
                    for key in self.hilfs_dic:
                        timerlist = timerlist + str(key) + " "
                    bot.send_message(chat_id=update.message.chat_id, text='Timer: {}'.format(timerlist))
                    return
    
            if timername not in self.hilfs_dic:
                bot.send_message(chat_id=update.message.chat_id, text='Timer "{}" gibts net.....'.format(timername))
                return
            userlist = " ,".join(self.user_data[timername])
            difftime = self.time_dic[timername] - datetime.datetime.now()
            timeto = int(difftime.total_seconds() / 60)
            bot.send_message(chat_id=update.message.chat_id, text='"{}" um {}, in {} Minuten: \n Teilnehmer: {}'.format(timername,self.time_dic[timername].strftime("%H:%M:%S"),timeto,userlist))
        except (IndexError, ValueError):
            timerlist = ""
            for key in self.hilfs_dic:
                timerlist = timerlist + str(key) + " "
            bot.send_message(chat_id=update.message.chat_id, text='Timer: {}'.format(timerlist))

    def block(self, bot, update, args):
        username = str(args[0])
    
        self.black_list[username] = username
        bot.send_message(chat_id=update.message.chat_id, text='{} darf nicht mehr abtreiben'.format(username))
    
    def deblock(self, bot, update, args):
        username = str(args[0])

        if username in self.black_list:
            del self.black_list[username]
            bot.send_message(chat_id=update.message.chat_id, text='{} darf wieder abtreiben'.format(username))

    def blocklist(self, bot, update):
        try:
            blocked_names = str(self.black_list).strip('[]').replace('\'','')
        except (IndexError, ValueError):
            if len(self.black_list) == 0:
                bot.send_message(chat_id=update.message.chat_id, text='Es gibt keine Abtreibungsverbot')
                return
        bot.send_message(chat_id=update.message.chat_id, text='Abtreibungsverbot für: {}'.format(blocked_names))

    def weather(self, bot, update, args):
        try:
            days = int(args[1])
        except (IndexError, ValueError):
            days = 1

        try:
            location = str(args[0])
        except (IndexError, ValueError):
            bot.send_message(chat_id=update.message.chat_id, text='An Ort musst schon angeben....')
            return

        page = requests.get('https://www.bergfex.at/sommer/' + location + '/wetter/prognose')
        parser = AdvancedHTMLParser.AdvancedHTMLParser()
        parser.parseStr(page.content)
    
        masterkeys = []
        for i in range(0,days):
            masterkeys.append("forecast-day-" + str(i))

        masterdic = dict.fromkeys(masterkeys, {})

        datakeys = ['tmax','tmin','rrp','rrr','sonne','sgrenze','wgew']

        dataReplaceKeys = {'tmax':      'Max. Temperatur',
                           'tmin':      'Min. Temperatur',
                           'rrp':       'Regenwahrscheinlichkeit',
                           'rrr':       'Regenmenge in Liter',
                           'sonne':     'Sonnenstunden',
                           'sgrenze':   'Schneefallgrenze',
                           'wgew':      'Gewitterwahrscheinlichkeit'}

        datadic = dict.fromkeys(datakeys, "-")

        messageOutput = ""
        for m in sorted(masterdic.keys()):
            if m == "forecast-day-0":
                mFormated = "Heute:"
            elif m == "forecast-day-1":
                mFormated = "\nMorgen:"
            else:
                mFormated = "\nIn " + m.strip('forecast-day-') + " Tagen :"
            messageOutput = messageOutput + mFormated + "\n"

            day = parser.getElementById(m)

            if day is None:
                bot.send_message(chat_id=update.message.chat_id, text='Keine Daten für: {} für die nächsten {} Tage'.format(location,str(days)))
                return

            for k in datadic:
                datadic[k] = day.getElementsByClassName(k)[0].innerHTML.strip()
                messageOutput = messageOutput + dataReplaceKeys[k] + ": " + datadic[k] + "\n"

        bot.send_message(chat_id=update.message.chat_id, text='Wetterinfo: \n{}'.format(messageOutput.encode("utf-8")))

    def cm(self, bot, update, args):
        try:
            celcius = float(args[0])
            mordor = Decimal((celcius-29)/2).to_integral_value(rounding=ROUND_HALF_UP)
            bot.send_message(chat_id=update.message.chat_id, text="%s°C san %s°M" %(celcius, mordor))
        except:
            bot.send_message(chat_id=update.message.chat_id, text="irgendwos is schief gangen. kann i net umrechnen. vielleicht muast wos gscheits angeben")

    def mordor(self, bot, update, args):

        username = self.createUser(update)

        texts = [
              "wir ham {}°M in {}",
              "Michse denken wir {}°M haben in {}",
              "Meine innere Stimme sagt mir wir haben {}°M in {}",
              "Ein Ring sie zu knechten, ins Dunkel zu treibn...Aso, nur die Temperatur. Alsdann: {}°M in {}",
              "Was sagt es mein Schatz? {}°M in {} mein Schatz. Garstige kleine Hobbits!",
              "Es hat gmiatliche {}°M in {}",
              "Mr " + username + " no home. {}°M in {} No no. I need more lemon pledge",
              "Frag mich nicht. Ich will nicht denken. Ich bin voller Schoggi. ({}°M in {})",
              "Wir ham {}°M in {}. Hasta la vista baby!",
              "{}°M in {}. Yippee-ki-yay, Motherfucker",
              "This is {}°M in {}!",
              "Enough is Enough! I've had it with this motherfucking {}°M in this motherfucking {}.",
              "You want the truth? You can't handle the truth! {}°M in {}",
              "Goooood morning Chat. Wir ham {}°M in {}",
              "Life is like a box of chocolate. You'll never no how many {}°M you'll get in {}",
              "Alright alright alright wir ham {}°M in {}"
        ]

        name = ""
        for arg in args:
            name += arg
            name += " "

        name = name.strip()

        cities = []
        # search for the city
        for city in self.city_list:
            if name.lower() == city["name"].lower():
                cities.clear()
                cities.append(city["name"])
                break
            if name.lower() in city["name"].lower():
                if city["name"] not in cities:
                    cities.append(city["name"])

        try:
            if len(cities) > 5:
                bot.send_message(chat_id=update.message.chat_id, text="bist deppert. i hob viel zviele ortschaften gfunden. anti spam maßnahmen wurden ergriffen aka i gib nix aus.")
            elif len(cities) == 0:
                posCities = difflib.get_close_matches(name.lower(),[c["name"].lower() for c in self.city_list],5)
                cities = ", ".join(self.user_data[posCities])
                bot.send_message(chat_id=update.message.chat_id, text='Manst vl an von den Ortn? {}'.format(cities))
            else:
                for city in cities:
                    response = requests.get("http://api.openweathermap.org/data/2.5/weather?q=%s&APPID=2859b9ab776091795c380b4696c1d58a&units=metric" % city)
                    data = response.json()
                    temp=data["main"]["temp"]
                    mordor=Decimal((temp-29)/2).to_integral_value(rounding=ROUND_HALF_UP)
                    text = random.choice(texts)
                    tmp_str = text.format(mordor, data["name"])
                    bot.send_message(chat_id=update.message.chat_id, text=tmp_str)
        except:
            bot.send_message(chat_id=update.message.chat_id, text="irgendwos is schief gangen. hob kane wetterdaten für di\nprobiers mal mit /mordor <die ortschaft>")

    def nukular(self, bot, update):
        bot.send_photo(chat_id=update.message.chat_id, photo=open('/home/zenzmatz/Telegram_Bot/nucular_simpsons.jpg', 'rb'))
    
    def kevin(self, bot, update):
        bot.send_document(chat_id=update.message.chat_id, document=open('/home/zenzmatz/Telegram_Bot/nein.gif', 'rb'))

    def error(self, bot, update, error):
        logger.warning('Update "%s" caused error "%s"', update, error)

TelegramBot = TimerBot("TOKEN")

TelegramBot.main()
