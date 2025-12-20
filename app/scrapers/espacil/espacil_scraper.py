from app.models.espacil import Espacil
import logging
from urllib.parse import urlencode
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Any
import re
import os

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler("logs/espacil.log"),
        logging.StreamHandler()
    ]
)

# Setup debug logger for full HTML logging (only if LOG_FULL_HTML is enabled)
debug_logger = logging.getLogger("espacil.debug")
if os.getenv("LOG_FULL_HTML", "false").lower() == "true" and not debug_logger.handlers:
    debug_handler = logging.FileHandler("logs/espacil_debug.log")
    debug_handler.setLevel(logging.DEBUG)
    debug_handler.setFormatter(logging.Formatter("%(asctime)s | %(levelname)s | %(message)s"))
    debug_logger.addHandler(debug_handler)
    debug_logger.setLevel(logging.DEBUG)


def scrape(espacil: Espacil):
    base_url = os.getenv("ESPACIL_BASE_URL")
    if not base_url:
        raise ValueError("ESPACIL_BASE_URL is not set")

    logging.info(f"Starting scraping: {espacil.__dict__}")

    url = get_url(espacil)
    logging.info(f"URL: {url}")

    response = requests.get(url)
    
    # Log response metadata at INFO level (best practice)
    content_length = len(response.text) if response.text else 0
    logging.info(f"Response status: {response.status_code}, Content-Length: {content_length} bytes")
    
    # Log HTML preview at INFO level (first 500 chars for quick debugging)
    if response.text:
        preview_length = 500
        html_preview = response.text[:preview_length]
        if len(response.text) > preview_length:
            logging.info(f"HTML preview (first {preview_length} chars): {html_preview}...")
        else:
            logging.info(f"HTML content: {html_preview}")
    
    # Log full HTML at DEBUG level (only when DEBUG logging is enabled)
    # This allows developers to enable full HTML logging when needed without polluting production logs
    logging.debug(f"Full HTML response: {response.text}")
    
    # Optionally log full HTML to a separate debug file if environment variable is set
    if os.getenv("LOG_FULL_HTML", "false").lower() == "true":
        debug_logger.debug(f"Full HTML response for URL {url}:\n{response.text}")

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
        - images: List of image URLs (list[str])
        - url: Property URL (str or None)
        - title: Property title (str or None)
        - postal_code: Postal code (str or None)
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    properties = []
    
    # Find all article elements with class "posts_list-one"
    articles = soup.find_all('article', class_='posts_list-one')
    
    for article in articles:
        property_info = {
            'rooms': None,
            'price': None,
            'charges_included': False,
            'images': [],
            'url': None,
            'title': None,
            'postal_code': None
        }
        
        # Extract URL from the link tag
        link_tag = article.find('a', class_='posts_list-one-inner')
        if link_tag:
            property_url = link_tag.get('href')
            if property_url:
                property_info['url'] = property_url
        
        # Extract title from title paragraph
        title_paragraph = article.find('p', class_='title')
        if title_paragraph:
            title_text = title_paragraph.get_text(strip=True)
            if title_text:
                property_info['title'] = title_text
        
        # Extract number of rooms and postal code from info paragraph
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
            
            # Extract postal code (5-digit number, typically at the end)
            # Format: "1 pièce, 44, 44700" where 44700 is the postal code
            postal_code_match = re.search(r'\b(\d{5})\b', info_text)
            if postal_code_match:
                property_info['postal_code'] = postal_code_match.group(1)
        
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
        
        # Extract images from thumbnail div
        thumb_div = article.find('div', class_='posts_list-one-thumb')
        if thumb_div:
            img_tag = thumb_div.find('img')
            if img_tag:
                # Get main image from src attribute
                main_image = img_tag.get('src')
                if main_image:
                    property_info['images'].append(main_image)
                
                # Also check srcset for additional image sizes
                srcset = img_tag.get('srcset')
                if srcset:
                    # Parse srcset format: "url1 size1, url2 size2"
                    srcset_urls = [url.strip().split()[0] for url in srcset.split(',') if url.strip()]
                    # Add unique URLs from srcset that are not already in images list
                    for url in srcset_urls:
                        if url and url not in property_info['images']:
                            property_info['images'].append(url)
        
        properties.append(property_info)
    
    logging.info(f"Extracted {len(properties)} properties from HTML")
    return properties