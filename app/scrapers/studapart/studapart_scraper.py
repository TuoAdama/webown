"""
Studapart scraper module.

This module provides functionality to scrape student housing listings
from the Studapart platform (https://www.studapart.com).
Extracts property URLs from JSON-LD data and scrapes individual pages.
"""

import logging
import re
import json
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Any, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
from app.models.studapart import Studapart

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler("logs/studapart.log"),
        logging.StreamHandler()
    ]
)

# Studapart base URL
BASE_URL = "https://www.studapart.com"

# City URL slugs mapping for Studapart
CITY_URL_SLUGS = {
    "paris": "paris",
    "lyon": "lyon",
    "marseille": "marseille",
    "toulouse": "toulouse",
    "bordeaux": "bordeaux",
    "lille": "lille",
    "nantes": "nantes",
    "montpellier": "montpellier",
    "rennes": "rennes",
    "grenoble": "grenoble",
    "nice": "nice",
    "strasbourg": "strasbourg",
    "rouen": "rouen",
    "reims": "reims",
    "tours": "tours",
    "angers": "angers",
    "dijon": "dijon",
    "clermont-ferrand": "clermont-ferrand",
    "le havre": "le-havre",
    "saint-etienne": "saint-etienne",
}

# HTTP headers for requests
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "fr-FR,fr;q=0.9,en;q=0.8",
    "Connection": "keep-alive",
}


def get_city_slug(city_name: str) -> str:
    """
    Get the URL slug for a given city name.
    """
    city_lower = city_name.lower().strip()
    
    if city_lower in CITY_URL_SLUGS:
        return CITY_URL_SLUGS[city_lower]
    
    for city, slug in CITY_URL_SLUGS.items():
        if city in city_lower or city_lower in city:
            return slug
    
    return city_lower.replace(" ", "-").replace("'", "-")


def scrape(studapart: Studapart) -> Optional[List[Dict[str, Any]]]:
    """
    Scrape student housing listings from Studapart.
    
    Args:
        studapart: Studapart model containing search parameters
        
    Returns:
        List of property dictionaries containing housing information,
        or None if scraping fails
    """
    logging.info(f"Starting Studapart scraping: {studapart.__dict__}")
    
    try:
        # Build the search URL
        city_slug = get_city_slug(studapart.city_name)
        url = f"{BASE_URL}/fr/logement-etudiant-{city_slug}"
        
        logging.info(f"Scraping URL: {url}")
        
        # Get the listing page
        response = requests.get(url, headers=HEADERS, timeout=30)
        
        if response.status_code != 200:
            logging.error(f"HTTP request failed with status code {response.status_code}")
            return None
        
        logging.info(f"Response received, content length: {len(response.text)} bytes")
        
        # Extract property URLs from JSON-LD
        property_urls = extract_property_urls_from_jsonld(response.text)
        
        logging.info(f"Found {len(property_urls)} property URLs in JSON-LD")
        
        if not property_urls:
            logging.warning("No property URLs found")
            return []
        
        # Limit the number of properties to scrape
        max_properties = min(studapart.per_page, len(property_urls))
        property_urls = property_urls[:max_properties]
        
        # Scrape each property page (with parallel requests)
        properties = []
        
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = {
                executor.submit(scrape_property_page, prop_url, studapart): prop_url 
                for prop_url in property_urls
            }
            
            for future in as_completed(futures):
                try:
                    result = future.result()
                    if result:
                        properties.append(result)
                except Exception as e:
                    logging.warning(f"Error scraping property: {e}")
        
        logging.info(f"End scraping. Results found: {len(properties)}")
        return properties
        
    except requests.RequestException as e:
        logging.error(f"Network error during scraping: {e}")
        return None
    except Exception as e:
        logging.error(f"Error during scraping: {e}")
        import traceback
        logging.error(traceback.format_exc())
        return None


def extract_property_urls_from_jsonld(html_content: str) -> List[str]:
    """
    Extract property URLs from JSON-LD ItemList in the HTML.
    
    Args:
        html_content: HTML content of the search page
        
    Returns:
        List of property URLs
    """
    urls = []
    
    # Find all JSON-LD scripts
    soup = BeautifulSoup(html_content, 'html.parser')
    jsonld_scripts = soup.find_all('script', type='application/ld+json')
    
    for script in jsonld_scripts:
        try:
            if not script.string:
                continue
            data = json.loads(script.string)
            
            # Check if it's an ItemList with property listings
            if data.get('@type') == 'ItemList':
                items = data.get('itemListElement', [])
                logging.info(f"Found ItemList with {len(items)} items")
                for item in items:
                    url = item.get('url', '')
                    # URLs follow pattern: /fr/logement-CITY/... (property or residence)
                    # Include URLs that have /residence/ or /property/ in them
                    if '/residence/' in url or '/property/' in url:
                        if not url.startswith('http'):
                            url = f"{BASE_URL}{url}"
                        urls.append(url)
        except (json.JSONDecodeError, TypeError) as e:
            logging.debug(f"Error parsing JSON-LD: {e}")
            continue
    
    return urls


def scrape_property_page(url: str, studapart: Studapart) -> Optional[Dict[str, Any]]:
    """
    Scrape details from a single property page.
    
    Args:
        url: Property page URL
        studapart: Studapart model for filtering
        
    Returns:
        Property dictionary or None
    """
    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        
        if response.status_code != 200:
            logging.warning(f"Failed to fetch property page: {url}")
            return None
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        property_info = {
            'id': None,
            'title': None,
            'price': None,
            'charges_included': False,
            'rooms': None,
            'space': None,
            'postal_code': None,
            'city': None,
            'address': None,
            'property_type': None,
            'images': [],
            'url': url
        }
        
        # Extract ID from URL
        match = re.search(r'/(?:property|residence)/([^/\?]+)', url)
        if match:
            property_info['id'] = match.group(1)
        
        # Extract title from page title or h1
        title_elem = soup.find('h1')
        if title_elem:
            property_info['title'] = title_elem.get_text(strip=True)
        else:
            title_tag = soup.find('title')
            if title_tag:
                property_info['title'] = title_tag.get_text(strip=True).split(' - ')[0]
        
        # Get page text for extraction
        page_text = soup.get_text(separator=' ')
        
        # Extract price
        price_patterns = [
            r'(\d[\d\s,\.]*)\s*€\s*/\s*mois',
            r'(\d[\d\s,\.]*)\s*€/mois',
            r'Loyer\s*:\s*(\d[\d\s,\.]*)\s*€',
            r'(\d[\d\s,\.]*)\s*€',
        ]
        
        for pattern in price_patterns:
            price_match = re.search(pattern, page_text)
            if price_match:
                try:
                    price_str = price_match.group(1).replace(' ', '').replace(',', '.')
                    price = float(price_str)
                    # Validate price range (ignore unrealistic prices)
                    if 100 <= price <= 10000:
                        property_info['price'] = price
                        break
                except ValueError:
                    continue
        
        # Check if charges included
        property_info['charges_included'] = bool(
            re.search(r'(CC|charges\s*(comprises|incluses))', page_text, re.IGNORECASE)
        )
        
        # Extract surface
        surface_match = re.search(r'(\d+)\s*m[²2]', page_text)
        if surface_match:
            property_info['space'] = float(surface_match.group(1))
        
        # Extract rooms
        rooms_match = re.search(r'(\d+)\s*(pièce|chambre|room)', page_text, re.IGNORECASE)
        if rooms_match:
            property_info['rooms'] = int(rooms_match.group(1))
        
        # Determine property type from URL and content
        url_lower = url.lower()
        text_lower = page_text.lower()
        
        if '/residence/' in url_lower:
            property_info['property_type'] = 'Résidence'
        elif 'studio' in text_lower:
            property_info['property_type'] = 'Studio'
        elif 'colocation' in text_lower:
            property_info['property_type'] = 'Colocation'
        elif 'chambre' in text_lower:
            property_info['property_type'] = 'Chambre'
        elif 'appartement' in text_lower:
            property_info['property_type'] = 'Appartement'
        
        # Extract postal code
        postal_match = re.search(r'\b(\d{5})\b', page_text)
        if postal_match:
            property_info['postal_code'] = postal_match.group(1)
        
        # Extract city from URL
        city_match = re.search(r'/logement-([^/]+)/', url)
        if city_match:
            property_info['city'] = city_match.group(1).replace('-', ' ').title()
        
        # Extract images
        img_tags = soup.find_all('img')
        for img in img_tags:
            src = img.get('src') or img.get('data-src')
            if src and 'media.studapart.com' in src:
                if not any(x in src.lower() for x in ['logo', 'icon', 'avatar', 'placeholder']):
                    if src not in property_info['images']:
                        property_info['images'].append(src)
        
        # Also check for background images and srcset
        for elem in soup.find_all(style=True):
            style = elem.get('style', '')
            bg_match = re.search(r'url\(["\']?([^"\')\s]+media\.studapart\.com[^"\')\s]+)["\']?\)', style)
            if bg_match:
                src = bg_match.group(1)
                if src not in property_info['images']:
                    property_info['images'].append(src)
        
        # Apply price filter
        if property_info['price']:
            if property_info['price'] < studapart.price_min or property_info['price'] > studapart.price_max:
                return None
        
        return property_info
        
    except Exception as e:
        logging.warning(f"Error scraping property page {url}: {e}")
        return None


def get_available_cities() -> List[str]:
    """
    Get list of available cities.
    
    Returns:
        List of city names
    """
    return list(CITY_URL_SLUGS.keys())
