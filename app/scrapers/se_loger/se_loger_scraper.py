from typing import Optional
from urllib.parse import urlencode
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By

from app.models.se_loger import SeLoger
from app.scrapers.se_loger.se_loger_card import card_to_result

se_loger_url = "https://www.seloger.com"


def scrape(se_loger: SeLoger):
    auto_completion = get_autocomplete(se_loger.city_name)
    if auto_completion is None:
        return None
    ids = [item['id'] for item in auto_completion if len(item['id']) == 11]
    search_url = get_url(se_loger, ids[0] if len(ids) else None)
    driver = webdriver.Firefox()
    driver.get(search_url)
    cards = driver.find_elements(By.XPATH, "//*[starts-with(@id, 'classified-card-')]")
    results = [card_to_result(card) for card in cards if card is not None]
    driver.close()
    return results

def get_url(se_loger: SeLoger, location: None):
    base_url = f"{se_loger_url}/classified-search"
    params = {
        "locations": location,
        "priceMin": se_loger.min_price,
        "priceMax": se_loger.max_price,
        "distributionTypes": (
            se_loger.type_searching.value if se_loger.type_searching else None
        ),
        "spaceMin": se_loger.space_min,
        "spaceMax": se_loger.space_max,
        "numberOfRoomsMin": se_loger.number_of_rooms_min,
        "numberOfRoomsMax": se_loger.number_of_rooms_max,
    }
    params = {k: v for k, v in params.items() if v is not None}
    return f"{base_url}?{urlencode(params)}"

def get_autocomplete(location_or_postal_code: str) -> Optional[list]:
    data = {
        "text": location_or_postal_code,
        "limit": 10,
        "placeTypes": [
            "NBH1",
            "NBH3",
            "AD09",
            "NBH2",
            "AD08",
            "AD06",
            "AD04",
            "POCO",
            "AD02"
        ],
        "parentTypes": [
            "NBH1",
            "NBH3",
            "AD09",
            "NBH2",
            "AD08",
            "AD06",
            "AD04",
            "POCO",
            "AD02"
        ],
        "locale": "fr"
    }
    response = requests.post(f"{se_loger_url}/search-mfe-bff/autocomplete", json=data)
    if response.status_code != 200:
        return None
    return response.json()