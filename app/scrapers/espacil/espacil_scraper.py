from app.models.espacil import Espacil
import logging
from urllib.parse import urlencode
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Any
import re

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

    return extract_properties(response.text)

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

def extract_properties(html_content: str) -> List[Dict[str, Any]]:
    """
    Extract property information from HTML content.
    
    Args:
        html_content: HTML content containing property listings
        
    Returns:
        List of dictionaries containing property information:
        - rooms: Number of rooms (int or None)
        - price: Monthly rent amount (float or None)
        - charges_included: Whether charges are included (bool)
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    properties = []
    
    # Find all article elements with class "posts_list-one"
    articles = soup.find_all('article', class_='posts_list-one')
    
    for article in articles:
        property_info = {
            'rooms': None,
            'price': None,
            'charges_included': False
        }
        
        # Extract number of rooms from info paragraph
        info_paragraph = article.find('p', class_='info')
        if info_paragraph:
            info_text = info_paragraph.get_text(strip=True)
            # Extract number from "X pièce(s)" pattern
            rooms_match = re.search(r'(\d+)\s*pièces?', info_text, re.IGNORECASE)
            if rooms_match:
                try:
                    property_info['rooms'] = int(rooms_match.group(1))
                except ValueError:
                    logging.warning(f"Could not parse rooms number from: {info_text}")
        
        # Extract price from price paragraph
        price_paragraph = article.find('p', class_='price')
        if price_paragraph:
            price_text = price_paragraph.get_text(strip=True)
            
            # Check if charges are included (CC = Charges Comprises)
            property_info['charges_included'] = 'CC' in price_text.upper()
            
            # Extract price amount (number before €)
            price_match = re.search(r'(\d+(?:\s*\d+)*)\s*€', price_text)
            if price_match:
                try:
                    # Remove spaces from price string (e.g., "1 234" -> "1234")
                    price_str = price_match.group(1).replace(' ', '')
                    property_info['price'] = float(price_str)
                except ValueError:
                    logging.warning(f"Could not parse price from: {price_text}")
        
        properties.append(property_info)
    
    logging.info(f"Extracted {len(properties)} properties from HTML")
    return properties