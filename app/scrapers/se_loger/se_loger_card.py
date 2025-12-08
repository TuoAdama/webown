from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
import re

from app.models.se_loger_result import SeLogerResult

def card_to_result(card: WebElement):
    if not len(card.text.strip()):
        return None
    result = SeLogerResult()
    try:
        result.id = get_id(card)
        result.link = get_link(card)
        result.images.append(get_image(card))
        result.price = get_price(card)
        description = get_description(card).text
        result.space = get_space(description)
        result.baths = get_baths(description)
        result.floors = get_floors(description)
    except NoSuchElementException:
        return None
    return result

def get_price(card: WebElement):
    try:
        price_element = card.find_element(By.XPATH, './/div[@data-testid="cardmfe-price-testid"]').text
        price = price_element.split("€")[0].strip()
        return float(price)
    except (NoSuchElementException, ValueError, TypeError):
        return None

def get_image(card: WebElement):
    main_image_container = get_element_by_xpath(card, './/div[@data-testid="card-mfe-picture-box-gallery-test-id"]')
    main_image = main_image_container.find_element(By.TAG_NAME, "img")
    return main_image.get_attribute("src")

def get_link(card: WebElement):
    return card.find_element(By.TAG_NAME, "a").get_attribute("href")


def get_space(description: str):
    match = re.search(r'([\d,]+)\s*m²', description)
    if match:
        return float(match.group(1).replace(",", "."))
    return None

def get_num_of_rooms(description: str):
    match = re.search(r'(\d+)\s*pièces?', description)
    if match:
        return int(match.group(1))
    return None

def get_baths(description: str):
    match = re.search(r'(\d+)\s*chambres?', description)
    if match:
        return int(match.group(1))
    return None

def get_floors(description: str):
    match = re.search(r'Étage\s*(\d+)\s*/\s*(\d+)', description)
    if match:
        return {
            "floor": int(match.group(1)),
            "total": int(match.group(2)),
        }
    return None

def get_id(card: WebElement):
    # extract last id (248GPIYASUUW) on string like this classified-card-248GPIYASUUW
    match = re.search(r'classified-card-(\w+)', card.get_attribute("id"))
    if match:
        return match.group(1)
    return None


def get_description(card: WebElement):
    return get_element_by_xpath(card, './/div[@data-testid="cardmfe-description-box-text-test-id"]')

def get_element_by_xpath(card: WebElement, xpath: str):
    return card.find_element(By.XPATH, xpath)