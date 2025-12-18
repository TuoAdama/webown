from app.models.espacil import Espacil
import logging
from urllib.parse import urlencode
import requests

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler("logs/espacil.log"),
        logging.StreamHandler()
    ]
)

base_url = "https://www.espacil-habitat.fr/devenir-locataire/rechercher-un-bien/"

def scrape(espacil: Espacil):
    logging.info(f"Starting scraping: {espacil.__dict__}")

    url = get_url(espacil)
    logging.info(f"URL: {url}")

    response = requests.get(url)
    logging.info(f"Response: {response.text}")

    return response.text

def get_url(espacil: Espacil):
    params = {
        "switch": "louer",
        "type": "logements",
        "price": 0,
        "loyer": espacil.price_max,
        "loctext": "",
        "localisation[]": espacil.city_name.lower()
    }
    params = {k: v for k, v in params.items() if v is not None}
    return f"{base_url}?{urlencode(params)}"