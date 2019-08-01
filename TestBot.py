#!/usr/bin/env python
# -*- coding: utf-8 -*-

from telegram.ext import Updater, CommandHandler
from telegram.ext import CommandHandler, CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import telegram
import logging
import datetime
import re

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
        self.menu_dummy = ""
        self.kb_remove = telegram.ReplyKeyboardRemove(False)
        
    def main(self):
        print "WIP"
        """Run bot."""
        updater = Updater("TOKEN")
    
        global users
        users = []
       
        dp = updater.dispatcher
    
        dp.add_handler(CommandHandler("start", self.start))
        dp.add_handler(CommandHandler("covfefe", self.covfefe, pass_args=True, pass_job_queue=True, pass_chat_data=True))
        dp.add_handler(CommandHandler("covfefe_test", self.covfefe, pass_args=True, pass_job_queue=True, pass_chat_data=True))
        dp.add_handler(CommandHandler("abort", self.abort, pass_args=True, pass_chat_data=True))
        dp.add_handler(CommandHandler("abortion", self.abortion, pass_chat_data=True))
        dp.add_handler(CommandHandler("metoo", self.metoo, pass_args=True, pass_chat_data=True))
        dp.add_handler(CommandHandler("menot", self.menot, pass_args=True, pass_chat_data=True))
        dp.add_handler(CommandHandler("list", self.list, pass_args=True, pass_chat_data=True))
        dp.add_handler(CommandHandler("nukular", self.nukular, pass_args=True, pass_chat_data=True))
        dp.add_handler(CommandHandler("kevin", self.kevin, pass_args=True, pass_chat_data=True))
        dp.add_handler(CommandHandler("attacke", self.attacke, pass_args=True, pass_chat_data=True))
        dp.add_handler(CommandHandler("block", self.block, pass_args=True, pass_chat_data=True))
        dp.add_handler(CommandHandler("deblock", self.deblock, pass_args=True, pass_chat_data=True))
        dp.add_handler(CallbackQueryHandler(self.button))
    
        dp.add_error_handler(self.error)
    
        updater.start_polling()
        updater.idle()
    
#sub functions:
    def createTimer(self, bot, job, messageText, halfTime = False):
        userlist = ""
        for key,val in self.hilfs_dic.iteritems():
            if val == job:
                utimername = key
        for u in self.user_data[utimername]:
            userlist = userlist + "@" + str(u) + " "
        timername = utimername[9:] if halfTime else utimername
        bot.send_message(job.context, text=messageText.format(timername,userlist))
        if halfTime:
            del self.half_dic[utimername]
        else:
            del self.hilfs_dic[utimername]
            del self.time_dic[utimername]

    def getTimerName(self, args):
        try:
            timername = str(args[0])
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
            bot.send_message(chat_id=update.message.chat_id, text='Timer {} gibts net.....'.format(timername))
            return True
        else:
            return False
    
#main functions
    def start(self, bot, update):
        update.message.reply_text('Hi! Use /covfefe <minutes> <timername> to set a timer \nUse /abort <timer> to kill a timer \nUse /metoo <timer> to join a timer \nUse /menot <timer> to leave a timer \n Use /list <timer> to list all active timer (or all members of timer) ')

    def alarm(self, bot, job):
        messageText = '{} auf gehts: \n {}'
        self.createTimer(bot, job, messageText)

    def halftime(self, bot, job):
        messageText = 'Noch 5 Minuten bis {} !! \n {}'
        self.createTimer(bot, job, messageText, True)

    def covfefe(self, bot, update, args, job_queue, chat_data):
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
        if timername in self.hilfs_dic:
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
                        self.time_dic[timername] = endtime
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
                        self.time_dic[timername] = deltatime
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
    
                self.hilfs_dic[timername] = job
    
                user = update.message.from_user
                if user['username'] == 'None' or user['username'] is None:
                    username = user['first_name']
                else:
                    username = user['username']
    
                usernames = [username]
                self.user_data[timername] = usernames
    
                global creator
                creator[timername] = username
            keyboard = [[InlineKeyboardButton("metoo", callback_data=timername+":1"),
                        InlineKeyboardButton("menot", callback_data=timername+":0")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            update.message.reply_text('{} hat {} Timer für {}, in {} Minuten gestartet'.format(user['username'],timername,self.time_dic[timername].strftime("%H:%M:%S"),due), reply_markup=reply_markup)
    
            except (IndexError, ValueError):
                bot.send_message(chat_id=update.message.chat_id, text='Usage: /covfefe <minutes> <timername>')

    def button(self, bot, update):
        query = update.callback_query
        timername = query.data.split(":")[0]
        yes = query.data.split(":")[1]
        user = update.callback_query.from_user
    
        if not bool(self.hilfs_dic):
            bot.send_message(chat_id=update.message.chat_id, text='Keine Timer gefunden....')
            return
        elif timername not in self.hilfs_dic:
            bot.send_message(chat_id=update.message.chat_id, text='Timer {} gibts net.....'.format(args[0]))
            return
    
        if user['username'] == 'None' or user['username'] is None:
            username = user['first_name']
        else:
            username = user['username']
    
        if yes == "1":
            if not username in self.user_data[timername]:
                usernames = self.user_data[timername]
                usernames.append(username)
                self.user_data[timername] = usernames
                bot.send_message(chat_id=query.message.chat_id, text='{}: {} geht mit'.format(timername, username))
        else:
            pass
    #            bot.send_message(chat_id=query.message.chat_id, text='Wie oft willst noch mitgehen?')
        else:
            usernames = self.user_data[timername]
            if username in usernames:
                usernames.remove(username)
                self.user_data[timername] = usernames
                bot.send_message(chat_id=query.message.chat_id, text='{}: {} geht doch net mit'.format(timername, username))
        else:
                if timername in self.anti_spam:
                    if not username in self.anti_spam[timername]:
                        bot.send_message(chat_id=query.message.chat_id, text='{}: {} geht nicht mit'.format(timername, username))
                        usernames = self.anti_spam[timername]
                        usernames.append(username)
                        self.anti_spam[timername] = usernames
                    else:
                        pass
                else:
                    bot.send_message(chat_id=query.message.chat_id, text='{}: {} geht nicht mit'.format(timername, username))
                    usernames = self.anti_spam[timername]
                    usernames.append(username)
                    self.anti_spam[timername] = usernames

    def abort(self, bot, update, args, chat_data):
        global kb_remove
        timername = self.getTimerName(self, args)
        return if self.checkTimer(self, bot, update, timername)
    
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

    def attacke(self, bot, update, args, chat_data):
        global kb_remove
        timername = self.getTimerName(self, args)
        return if self.checkTimer(self, bot, update, timername)
    
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
    
    def abortion(self, bot, update, chat_data):
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

TelegramBot = TimerBot("123456789ABCD")

TelegramBot.main()