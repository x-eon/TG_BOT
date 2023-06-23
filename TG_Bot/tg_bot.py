
#from aiogram.utils import executor
from datetime import datetime
import sqlite3
import sys
#import pandas as pd
import json

pydub_path = ''
sys.path.append(pydub_path)
TG_BOT_TOKEN = 'токен телеграм бота'
import os
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import  ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

class dataBase():
    def __init__(self):
        self.list_users = {} #self.init_db('filename.db')

class TGBot:
    def __init__(self):
        db = dataBase()
        #self.users_id = db.list_users
        self.users_id = self.loadJSON()
        self.section_type = 'head'
        if self.users_id == {}:
            userid = 'default'
            self.users_id = {userid:{'nickname':'','in_case':0,'out_case':0,'out_adres':''}}
            self.saveJSON(self.users_id)

        bot = Bot(token=TG_BOT_TOKEN)
        dp = Dispatcher(bot)
        self.dp = dp
        # Обработчик команды /start
        @dp.message_handler(commands=['start'])
        async def process_start_command(message: types.Message):
            answer = 'Главное меню \n мой телеграм для связи: @txeon \n  мой телефон: +79034349459'

            await message.reply(answer, reply_markup=self.head_menu())

        #--------------------------- главное меню ---------------------------------------
        @dp.message_handler(lambda message: message.text in ['🔂 Вернутся в главное меню','🔂 Очистить и вернутся в главное меню'])
        async def process_level1_buttons(message: types.Message):
            if self.section_type == 'new_user':
                userid = str(message.from_user.id)
                self.users_id.pop(userid)

            await message.reply("Главное меню", reply_markup=self.head_menu())

        #--------------------------- Пополить депозит ---------------------------------------
        @dp.message_handler(lambda message: message.text in ['💰 Пополнить депозит'])
        async def process_level1_buttons(message: types.Message):
            # Создание кнопок для второго уровня дерева
            button8 = KeyboardButton('👨‍💼 Новый пользователь')
            button9 = KeyboardButton('🤵 Инвестор')
            markup_level2 = ReplyKeyboardMarkup(resize_keyboard=True).add(button8, button9)
            await message.reply("Выберите вариант входа:", reply_markup=markup_level2)

        #---------------------------- Новый пользователь ------------------------------------
        @dp.message_handler(lambda message: message.text in ['👨‍💼 Новый пользователь','👨‍💼 Регистрация'])
        async def process_level1_buttons(message: types.Message):
            button8 = KeyboardButton('👨‍💼 Да')
            button9 = KeyboardButton('👨‍💼 Нет')
            markup_level2 = ReplyKeyboardMarkup(resize_keyboard=True).add(button8, button9)
            await message.reply("Ознакомились ли Вы с правилами?", reply_markup=markup_level2)

        #------------------------------------- Да --------------------------------------------
        @dp.message_handler(lambda message: message.text in ['👨‍💼 Да'])
        async def process_level1_buttons(message: types.Message):
            button9 = KeyboardButton('🔂 Вернутся в главное меню')
            markup_return = ReplyKeyboardMarkup(resize_keyboard=True).add(button9)
            self.section_type = 'nickname'
            await message.reply("Укажите nickname телеграм аккаунта и нажмите ввод.", reply_markup=markup_return)

        #------------------------------------- Нет --------------------------------------------
        @dp.message_handler(lambda message: message.text in ['👨‍💼 Нет'])
        async def process_level1_buttons(message: types.Message):
            button1 = KeyboardButton('📋 Правила')
            button0 = KeyboardButton('🔂 Вернутся в главное меню')
            markup_lev = ReplyKeyboardMarkup(resize_keyboard=True).add(button1,button0)
            await message.reply("Прочитать правила", reply_markup=markup_lev)

        #------------------------------------- Правила --------------------------------------------
        @dp.message_handler(lambda message: message.text in ['📋 Правила'])
        async def process_level1_buttons(message: types.Message):
            button0 = KeyboardButton('🔂 Вернутся в главное меню')
            markup_lev = ReplyKeyboardMarkup(resize_keyboard=True).add(button0)
            rules = self.loadFile('rules.txt')
            await message.reply(rules, reply_markup=markup_lev)

#====================================================================================================================
        #====================================== Инвестор =========================================
        @dp.message_handler(lambda message: message.text in ['💰 Перейти к пополнению','🔄 Попробовать снова','🤵 Инвестор'])
        async def process_level1_buttons(message: types.Message):
            self.section_type = 'investor_id'
            button1 = KeyboardButton('🆔 Войти по текущему id')
            button0 = KeyboardButton('🔂 Вернутся в главное меню')
            markup_lev = ReplyKeyboardMarkup(resize_keyboard=True).add(button1,button0)
            user_id = message.from_user.id
            await message.reply(f'введите свой индивидуальный номер, \nили войдите по текущему id: {user_id}', reply_markup=markup_lev)

        @dp.message_handler(lambda message: message.text in ['💹 Получить отчет за последний цикл'])
        async def process_level2_buttons(message: types.Message):
            button0 = KeyboardButton('🔂 Вернутся в главное меню')
            markup_return = ReplyKeyboardMarkup(resize_keyboard=True).add(button0)
            await message.reply("отчет", reply_markup=markup_return)

        #======================================== Вывод средств =========================================
        @dp.message_handler(lambda message: message.text in ['💵 Вывод средств','💵 Попробовать снова'])
        async def process_level1_buttons(message: types.Message):
            self.section_type = 'out_case'
            button8 = KeyboardButton('💵 Войти под текущим ID')
            button9 = KeyboardButton('🔂 Вернутся в главное меню')
            markup_level2 = ReplyKeyboardMarkup(resize_keyboard=True).add(button8,button9)
            user_id = message.from_user.id
            await message.reply(f'введите свой индивидуальный номер, \nили войдите по текущему id: {user_id}', reply_markup=markup_level2)

        @dp.message_handler(lambda message: message.text in ['💵 Войти под текущим ID'])
        async def process_level3_buttons(message: types.Message):
            self.section_type = 'out_case'
            await self.outCase(message)

        #------------------------------------- ALL --------------------------------------------

        @dp.message_handler()
        async def all_callback(message: types.Message):
            userid = str(message.from_user.id)
            if self.section_type == 'nickname':
                if message.text != '':
                    self.registration(message)
                    button1 = KeyboardButton('💰 Перейти к пополнению')
                    button0 = KeyboardButton('🔂 Очистить и вернутся в главное меню')
                    markup_return = ReplyKeyboardMarkup(resize_keyboard=True).add(button1, button0)
                    await message.reply(f"{self.users_id[userid]['nickname']}, Вам присвоен индивидуальный номер: "
                                        f"{message.from_user.id}", reply_markup=markup_return)

            await self.inCase(message)
            await self.outCase(message)

        #================================================


    async def inCase(self, message):

        if self.section_type == 'investor_in_case':
            if self.access_check(message):
                if self.request_case_add(message):
                    button0 = KeyboardButton('🔂 Вернутся в главное меню')
                    markup_return = ReplyKeyboardMarkup(resize_keyboard=True).add(button0)
                    dtm = self.timeNew()
                    await message.reply(f"Спасибо, Ваша заявка принята. {dtm} \n "
                                        f"Ващ баланс будет пополнен согласно правилам",reply_markup=markup_return)
                else:
                    button2 = KeyboardButton('🔄 Попробовать снова')
                    button0 = KeyboardButton('🔂 Вернутся в главное меню')
                    markup_return = ReplyKeyboardMarkup(resize_keyboard=True).add(button2, button0)
                    await message.reply("Внимание!\n Заявка отклонена, попробуйте еще, немного позже",
                                        reply_markup=markup_return)

        if self.section_type == 'investor_id':
            if message.text != '':
                if self.access_check(message):
                    button2 = KeyboardButton('🔂 Вернутся в главное меню')
                    markup_return = ReplyKeyboardMarkup(resize_keyboard=True).add(button2)
                    self.section_type = 'investor_in_case'
                    await message.reply("Укажите точную сумму пополнения и нажмите ▶", reply_markup=markup_return)
                else:
                    button2 = KeyboardButton('🔄 Попробовать снова')
                    button1 = KeyboardButton('👨‍💼 Регистрация')
                    button0 = KeyboardButton('🔂 Вернутся в главное меню')
                    markup_return = ReplyKeyboardMarkup(resize_keyboard=True).add(button2, button1, button0)
                    await message.reply("Указанный номер не найден", reply_markup=markup_return)



    async def outCase(self, message):
        print('SECT:',self.section_type,'MESSAGE:',message.text)
        if self.section_type == 'investor_out_adres':
            if message.text != '':
                if self.access_check(message):
                    button0 = KeyboardButton('🔂 Вернутся в главное меню')
                    markup_return = ReplyKeyboardMarkup(resize_keyboard=True).add(button0)
                    dtm = self.timeNew()
                    if self.request_case_out(message, dtm):
                        await message.reply(f"Спасибо, Ваша заявка принята. {dtm} \n "
                                            f"Ващи средства будут выведены согласно правилам",
                                            reply_markup=markup_return)
                    else:
                        await message.reply("Внимание!, заявка на вывод средств отклонена", reply_markup=markup_return)

        if self.section_type == 'investor_out_case':
            if message.text != '':
                if self.access_check(message):
                    button0 = KeyboardButton('🔂 Вернутся в главное меню')
                    markup_return = ReplyKeyboardMarkup(resize_keyboard=True).add(button0)
                    self.section_type = 'investor_out_adres'
                    await message.reply("Введите адрес для вывода средств и нажмите ▶, \n "
                                        "Внимание! вывод средств производится только на адреса сети BEP20",
                                        reply_markup=markup_return)

        if self.section_type == 'out_case':
            if self.access_check(message):
                button2 = KeyboardButton('🔂 Вернутся в главное меню')
                markup_return = ReplyKeyboardMarkup(resize_keyboard=True).add(button2)
                self.section_type = 'investor_out_case'
                await message.reply("Укажите точную сумму выводимых средств и нажмите ▶", reply_markup=markup_return)
            else:
                button2 = KeyboardButton('💵 Попробовать снова')
                button0 = KeyboardButton('🔂 Вернутся в главное меню')
                markup_return = ReplyKeyboardMarkup(resize_keyboard=True).add(button2, button0)
                await message.reply("Указанный номер не найден", reply_markup=markup_return)

    def head_menu(self):
        markup = ReplyKeyboardMarkup(resize_keyboard=True)
        button1 = KeyboardButton('💰 Пополнить депозит')
        button2 = KeyboardButton('💵 Вывод средств')
        button3 = KeyboardButton('📋 Правила')
        button4 = KeyboardButton('💹 Получить отчет за последний цикл')
        markup.add(button1, button2, button3, button4)
        return markup

    #-----------------------------------------------------------------------------------------------------
    def access_check(self, message):
        res = False
        userid = str(message.from_user.id)
        if userid in self.users_id:
            res = True
        return res

    def loadFile(self, filename):
        print('rules0',filename)
        if os.path.exists(filename):
            res = ''
            print('rules1')
            with open(filename, 'r', encoding='utf8') as file:
                line = file.readlines()
                for _str in line:
                    res = res + _str + "\n"
            return res
        else:
            return 'no file: '+filename

    def loadJSON(self):
        data = {}
        if os.path.exists('users.json'):
            with open('users.json', 'r') as file:
                data = json.load(file)
        print('JSON',data)
        return data

    def saveJSON(self, data):
        with open('users.json', 'w') as file:
            json.dump(data, file)


    def registration(self,message):
        userid = str(message.from_user.id)
        if userid in self.users_id:
            self.users_id[userid]['nickname'] = message.text
        else:
            self.users_id.update({userid:{'nickname':message.text,'in_case':0,'out_case':0,'out_adres':''}})
        self.saveJSON(self.users_id)

    def request_case_add(self,message):
        userid = str(message.from_user.id)
        self.users_id[userid]['in_case'] = message.text
        print(F'ПРИШЕЛ ЗАПРОС ОТ {userid} НА ДОБАВЛЕНИЕ СРЕДСТВ')
        res = self.sendMessage(message)

        return res

    def request_case_out(self, message, dtm):
        userid = str(message.from_user.id)
        self.users_id[userid]['in_adres'] = message.text
        print(F'ПРИШЕЛ ЗАПРОС ОТ {userid} НА ВЫВОД СРЕДСТВ')
        res = self.sendMessage(message)
        return res

    def sendMessage(self,message):
        userid = str(message.from_user.id)
        tm = self.timeNew()
        snd_message = {userid: self.users_id[userid],'time':tm}
        return True

    def timeNew(self):
        """локальное время компьютера"""
        return datetime.now().strftime("%d-%m-%Y %H:%M:%S")

if __name__ == '__main__':
    tgbot = TGBot()
    executor.start_polling(tgbot.dp, skip_updates=True)
