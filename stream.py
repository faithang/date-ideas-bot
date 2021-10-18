import os
from dotenv import load_dotenv
import requests
import random
from datetime import datetime

load_dotenv()
NOTION_KEY = os.getenv('NOTION_KEY')
BASE_URL = os.getenv('BASE_URL')
DATABASE_ID = os.getenv('NOTION_DATABASE_ID')
NOTION_VERSION = os.getenv('NOTION_VERSION')

header = {
    "Authorization": NOTION_KEY,
    "Notion-Version": NOTION_VERSION
}


def get_tags():
    print("getting tags")
    response = requests.get(BASE_URL + DATABASE_ID, headers = header)
    tags = response.json()['properties']['Tags']['multi_select']['options']
    return tags

def query_by_tag(tag):
    query = {"filter": {"property": "Tags", "multi_select": {"contains": tag}}, "sorts": [{"property": "Done", "direction": "ascending"}]}
    response = requests.post(BASE_URL + DATABASE_ID + '/query', 
    headers = header,
    json = query)
    raw_dates = response.json()['results']
    list = []
    for date in raw_dates: 
        item_name = date['properties']['Name']['title'][0]['plain_text']
        item_id = date['id']
        list.append({ "name": item_name, "id": item_id })
    return list

def random_date():
    response = requests.post(BASE_URL + DATABASE_ID + '/query', headers = header)
    raw_dates = response.json()['results']
    list = []
    for date in raw_dates: 
        item_name = date['properties']['Name']['title'][0]['plain_text']
        item_id = date['id']
        list.append({ "name": item_name, "id": item_id })
    return random.choice(list)

def all_dates():
    response = requests.post(BASE_URL + DATABASE_ID + '/query', headers = header)
    raw_dates = response.json()['results']
    list = []
    for date in raw_dates: 
        item_name = date['properties']['Name']['title'][0]['plain_text']
        item_id = date['id']
        list.append({ "name": item_name, "id": item_id })
    return list

def upcoming_dates():
    query = {"filter": {"property": "Date", "date": {"on_or_after": datetime.today().strftime('%Y-%m-%d')}},"sorts": [{"property": "Date", "direction": "ascending"}]}
    response = requests.post(BASE_URL + DATABASE_ID + '/query', 
    headers = header,
    json = query)
    raw_dates = response.json()['results']
    list = []
    for date in raw_dates: 
        item_name = date['properties']['Name']['title'][0]['plain_text']
        item_id = date['id']
        item_date = date['properties']['Date']['date']['start']
        list.append({ "name": item_name, "id": item_id, "date": item_date })
    return list

def mark_done(id):
    query = {"properties": {"Done": { "checkbox": True}}}
    requests.patch('https://api.notion.com/v1/pages/' + id, headers = header, json = query)
