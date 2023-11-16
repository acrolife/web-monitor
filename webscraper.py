import requests
from bs4 import BeautifulSoup
import json

def fetch_webpage(url):
    response = requests.get(url)
    return BeautifulSoup(response.content, 'html.parser')

def extract_slots(soup):
    slots = []
    for reservation in soup.find_all('a', string='RESERVATION'):
        date_info = reservation.find_previous('div', {'data-hook': 'ev-full-date-location'})
        if date_info:
            date = date_info.find('div', {'data-hook': 'date'}).get_text(strip=True)
            slots.append((date, reservation.get_text(strip=True)))
    return slots

def read_stored_slots(file_path):
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return []

def write_stored_slots(file_path, slots):
    with open(file_path, 'w') as file:
        json.dump(slots, file)    

def check_for_new_slots(current_slots, stored_slots):
    return [slot for slot in current_slots if slot not in stored_slots]
