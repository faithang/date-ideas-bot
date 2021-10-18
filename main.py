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
global selected_dates
selected_dates = {}
global selected_id
selected_id = ""


commands = {  # command description used in the "help" command
    'help'        : 'List available commands',
    'upcoming': 'View your upcoming dates',
    'all'         : 'List all date ideas',
    'dates':'List date ideas by category',
    'srv': 'List SRV-eligible date ideas',
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
def all_dates(message):
    chat_id = message.chat.id
    markup = create_markup()
    list = stream.all_dates()
    if list:
        for item in list:
            item = InlineKeyboardButton(item['name'], callback_data=item['id'])
            markup.add(item)
        bot.send_message(chat_id, "Looking up <b>all</b> dates:", reply_markup=markup)

@bot.message_handler(commands=['upcoming'])
def upcoming_dates(message):
    chat_id = message.chat.id
    list = stream.upcoming_dates()
    if list:
        string = ""
        for item in list:
            string += item['date'] + ": " + item['name'] + "\n"
        bot.send_message(chat_id, string)

@bot.message_handler(commands=['srv'])
def upcoming_dates(message):
    chat_id = message.chat.id
    list = stream.srv_dates()
    markup = create_markup()
    for item in list:
        global selected_dates
        selected_dates[item['id']] = item['name']
        date = InlineKeyboardButton(item['name'], callback_data=item['id'])
        markup.add(date)
    bot.send_message(chat_id, "Looking up <b>SRV-eligible</b> dates:", reply_markup=markup)

@bot.message_handler(commands=['dates'])
def find_dates(message):
    chat_id = message.chat.id
    markup = create_markup()
    markup.add(InlineKeyboardButton("All", callback_data="all"))
    for tag in tags: 
        date = InlineKeyboardButton(tag['name'], callback_data=tag['name'])
        markup.add(date)
    bot.send_message(chat_id, "What kind of date ideas are you interested in?", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    chat_id = call.message.chat.id
    print(call.data)
    # When tag is chosen
    if is_tag(call):
        list = stream.query_by_tag(call.data)
        markup = create_markup()
        for item in list:
            global selected_dates
            selected_dates[item['id']] = item['name']
            date = InlineKeyboardButton(item['name'], callback_data=item['id'])
            markup.add(date)
        bot.send_message(chat_id, "Looking up <b>" + call.data.lower() + "</b> dates:", reply_markup=markup)

    # When 'all' tag is chosen
    elif call.data == "all":
        markup = create_markup()
        list = stream.all_dates()
        for item in list:
            selected_dates[item['id']] = item['name']
            date = InlineKeyboardButton(item['name'], callback_data=item['id'])
            markup.add(date)
        bot.send_message(chat_id, "Looking up <b>all</b> dates:", reply_markup=markup)

    # When a particular date ID is chosen
    elif call.data in selected_dates:
        global selected_id
        selected_id = call.data
        markup = create_markup()
        markup.add(InlineKeyboardButton("Mark date as done", callback_data="mark_done"))
        # markup.add(InlineKeyboardButton("Schedule date", callback_data="schedule_date"))
        bot.send_message(chat_id, "You've chosen: <b>" + selected_dates[call.data] + "</b>.", reply_markup=markup)
    
    # When actions on date is chosen
    elif call.data == "mark_done":
        # TODO: mark date as done
        stream.mark_done(selected_id)
        # bot.send_message(chat_id, selected_date + " has been marked as done.")
        bot.send_message(chat_id, "<b>" + selected_dates[selected_id] + "</b> has been marked as done.")

    elif call.data == "schedule_date":
        # TODO: schedule date
        # bot.send_message(chat_id, selected_date + " has been scheduled.")
        bot.send_message(chat_id, "Date has been scheduled.")

    else: 
        bot.send_message(chat_id, "I don't recognise that command. Let's start from the beginning.")
        markup = create_markup()
        markup.add(InlineKeyboardButton("All", callback_data="all"))
        for tag in tags: 
            date = InlineKeyboardButton(tag['name'], callback_data=tag['name'])
            markup.add(date)
        bot.send_message(chat_id, "What kind of date ideas are you interested in?", reply_markup=markup)
    
    


@bot.message_handler(commands=['random'])
def find_random_date(message):
    chat_id = message.chat.id
    random_date = stream.random_date()
    global selected_id
    selected_id = random_date['id']
    global selected_dates
    selected_dates[random_date['id']] = random_date['name']
    markup = create_markup()
    markup.add(InlineKeyboardButton("Mark date as done", callback_data="mark_done"))
    # markup.add(InlineKeyboardButton("Schedule date", callback_data="schedule_date"))
    bot.send_message(chat_id, "Let's go... <b>" + random_date['name'] + "</b>!", reply_markup=markup)

bot.infinity_polling()
