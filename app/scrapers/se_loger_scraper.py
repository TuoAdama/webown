from typing import Optional
from selenium import webdriver
from selenium.webdriver.common.by import By
from app.enums.type_searching import TypeSearching
from app.models.se_loger import SeLoger
import requests
from time import sleep

url = "https://www.seloger.com/"
rent_attribute ='[data-key="RENT"]'
buy_attribute ='[data-key="BUY"]'


def scrape(se_loger: SeLoger):
    firefox = webdriver.Firefox()
    firefox.get(url)
    sleep(5)
    firefox.save_screenshot("main_page.png")
    type_searching = TypeSearching.RENT.value if se_loger.type_searching == TypeSearching.RENT else TypeSearching.BUY.value
    element = firefox.find_element(By.CSS_SELECTOR, type_searching)
    print(element)
    element.click()
    firefox.close()


def get_autocomplete(text: str) -> Optional[list]:
    data = {
        "text": text,
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
    response = requests.post("https://www.seloger.com/search-mfe-bff/autocomplete", json=data)
    if response.status_code != 200:
        return None
    return response.json()