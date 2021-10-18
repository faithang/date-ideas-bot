import os
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import stream
from dotenv import load_dotenv

load_dotenv()

TELE_API_KEY = os.getenv('TELE_API_KEY')
NOTION_URL = os.getenv('NOTION_URL')

bot = telebot.TeleBot(TELE_API_KEY, parse_mode='HTML')
tags = stream.get_tags()
selected_date = ""

commands = {  # command description used in the "help" command
    'start'       : 'Initiate the bot',
    'help'        : 'Gives you information about the available commands',
    'dates'        : 'List dates by category',
    'random': 'Get a random date idea',
    'link' : 'Get URL to the Notion document'
}


def is_tag(call):
    for tag in tags:
        if call.data == tag['name']:
            return True
    return False

def is_date(call):
    return True

def create_markup():
    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    return markup


@bot.message_handler(commands=['start', 'help'])
def start(m):  
    cid = m.chat.id
    help_text = "The following commands are available: \n"
    for key in commands:  # generate help text out of the commands dictionary defined at the top
        help_text += "/" + key + ": "
        help_text += commands[key] + "\n"
    bot.send_message(cid, help_text)  # send the generated help page


@bot.message_handler(commands=['link'])
def link(message):  
    bot.send_message(message.chat.id, NOTION_URL)

@bot.message_handler(commands=['all'])
def find_dates(message):
    chat_id = message.chat.id
    markup = create_markup()
    list = stream.all_dates()
    for item in list:
        item = InlineKeyboardButton(item, callback_data=item)
        markup.add(item)
        bot.send_message(chat_id, "Looking up <b>all</b> dates:", reply_markup=markup)

@bot.message_handler(commands=['dates'])
def find_dates(message):
    chat_id = message.chat.id
    markup = create_markup()
    for tag in tags: 
        print(tag)
        item = InlineKeyboardButton(tag['name'], callback_data=tag['name'])
        markup.add(item)
    bot.send_message(chat_id, "What kind of date ideas are you interested in?", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    chat_id = call.message.chat.id
    if is_tag(call):
        list = stream.query_by_tag(call.data)
        string = ""
        markup = create_markup()
        for item in list:
            item = InlineKeyboardButton(item, callback_data=item)
            markup.add(item)
        bot.send_message(chat_id, "Looking up <b>" + call.data.lower() + "</b> dates:", reply_markup=markup)
    elif call.data == "mark_done":
        # TODO: mark date as done
        # bot.send_message(chat_id, selected_date + " has been marked as done.")
        bot.send_message(chat_id, "Date has been marked as done.")
    elif call.data == "schedule_date":
        # TODO: schedule date
        # bot.send_message(chat_id, selected_date + " has been scheduled.")
        bot.send_message(chat_id, "Date has been scheduled.")
    elif is_date(call):
        selected_date = call.data
        markup = create_markup()
        markup.add(InlineKeyboardButton("Mark date as done", callback_data="mark_done"))
        # markup.add(InlineKeyboardButton("Schedule date", callback_data="schedule_date"))
        bot.send_message(chat_id, "You've chosen: <b>" + call.data + "</b>.", reply_markup=markup)


@bot.message_handler(commands=['random'])
def find_random_date(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, "Let's go... " + stream.random_date() + "!")

bot.infinity_polling()
