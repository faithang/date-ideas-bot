import os
import telebot
from telebot import types
import stream
from dotenv import load_dotenv
import time

load_dotenv()

TELE_API_KEY = os.getenv('TELE_API_KEY')

bot = telebot.TeleBot(TELE_API_KEY)
tags = stream.get_tags()

def is_tag(message):
    print(message)
    for tag in tags:
        print(tag['name'])
        if message.text == tag['name']:
            return True
    return False

@bot.message_handler(commands=['start', 'help'])
def start(message):  
    bot.send_message(message.chat.id,
     "Hey " + message.chat.first_name + "! Here are the available commands.\n/dates: list dates\n/random: find random date\n")

@bot.message_handler(commands=['dates'])
def find_dates(message):
    chat_id = message.chat.id
    markup = types.ReplyKeyboardMarkup(row_width=2, one_time_keyboard=True)
    for tag in tags: 
        print(tag['name'])
        item = types.KeyboardButton(tag['name'])
        markup.add(item)
    bot.send_message(chat_id, "What kind of date ideas are you interested in?", reply_markup=markup)

@bot.message_handler(commands=['random'])
def find_random_date(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, "Let's go... " + stream.random_date() + "!")

@bot.message_handler(func=is_tag)
def find_filtered_dates(message):
    bot.send_message(message.chat.id, "Ok, searching for " + message.text.lower() + " dates")
    list = stream.query_by_tag(message.text)
    string = ""
    for item in list:
        string += item + "\n"
    bot.send_message(message.chat.id, string)

@bot.inline_handler(lambda query: query.query == '/random')
def test(inline_query):
    find_random_date(inline_query)


bot.infinity_polling()
