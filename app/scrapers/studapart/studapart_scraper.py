"""
Studapart scraper module.

This module provides functionality to scrape student housing listings
from the Studapart platform (https://www.studapart.com).
"""

import logging
import requests
from typing import List, Dict, Any, Optional
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

# Studapart API endpoints
SEARCH_API_URL = "https://search-api.studapart.com/property"
QUICKFILTER_URL = "https://www.studapart.com/fr/search/quickfilter"

# City to postal codes mapping for major French cities
CITY_POSTAL_CODES = {
    "paris": ["75000", "75001", "75002", "75003", "75004", "75005", "75006", 
              "75007", "75008", "75009", "75010", "75011", "75012", "75013", 
              "75014", "75015", "75016", "75017", "75018", "75019", "75020", "75116"],
    "lyon": ["69000", "69001", "69002", "69003", "69004", "69005", "69006", 
             "69007", "69008", "69009"],
    "marseille": ["13000", "13001", "13002", "13003", "13004", "13005", "13006",
                  "13007", "13008", "13009", "13010", "13011", "13012", "13013",
                  "13014", "13015", "13016"],
    "toulouse": ["31000", "31100", "31200", "31300", "31400", "31500"],
    "bordeaux": ["33000", "33100", "33200", "33300", "33800"],
    "lille": ["59000", "59160", "59260", "59777", "59800"],
    "nantes": ["44000", "44100", "44200", "44300"],
    "montpellier": ["34000", "34070", "34080", "34090"],
    "rennes": ["35000", "35200", "35700"],
    "grenoble": ["38000", "38100"],
    "nice": ["06000", "06100", "06200", "06300"],
    "strasbourg": ["67000", "67100", "67200"],
}


def get_postal_codes_for_city(city_name: str) -> List[str]:
    """
    Get postal codes for a given city name.
    
    Args:
        city_name: Name of the city (case-insensitive)
        
    Returns:
        List of postal codes for the city, or single code if not in mapping
    """
    city_lower = city_name.lower().strip()
    if city_lower in CITY_POSTAL_CODES:
        return CITY_POSTAL_CODES[city_lower]
    # Default: try to find partial match or return empty
    for city, codes in CITY_POSTAL_CODES.items():
        if city in city_lower or city_lower in city:
            return codes
    return []


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
        # Get postal codes for the city
        postal_codes = get_postal_codes_for_city(studapart.city_name)
        
        if not postal_codes:
            logging.warning(f"No postal codes found for city: {studapart.city_name}")
            # Try with the city name directly
            postal_codes = [studapart.city_name]
        
        # Build the search payload
        payload = build_search_payload(studapart, postal_codes)
        
        logging.info(f"Search payload: {payload}")
        
        # Make the API request
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            "Origin": "https://www.studapart.com",
            "Referer": "https://www.studapart.com/"
        }
        
        response = requests.post(
            SEARCH_API_URL,
            json=payload,
            headers=headers,
            timeout=30
        )
        
        if response.status_code != 200:
            logging.error(f"API request failed with status code {response.status_code}")
            logging.error(f"Response: {response.text[:500]}")
            return None
        
        data = response.json()
        logging.info(f"API response received, processing data...")
        
        # Extract and format properties
        properties = extract_properties(data)
        
        logging.info(f"End scraping. Results found: {len(properties)}")
        return properties
        
    except requests.RequestException as e:
        logging.error(f"Network error during scraping: {e}")
        return None
    except Exception as e:
        logging.error(f"Error during scraping: {e}")
        return None


def build_search_payload(studapart: Studapart, postal_codes: List[str]) -> Dict[str, Any]:
    """
    Build the search payload for the Studapart API.
    
    Args:
        studapart: Studapart model containing search parameters
        postal_codes: List of postal codes to search
        
    Returns:
        Dictionary payload for the API request
    """
    payload = {
        "size": studapart.per_page,
        "from": (studapart.page - 1) * studapart.per_page,
        "priceMin": studapart.price_min,
        "priceMax": studapart.price_max,
        "cities": [studapart.city_name.capitalize()],
        "postalCodes": postal_codes,
        "isOpenSearch": True,
        "sort": "relevance"
    }
    
    # Add optional filters
    if studapart.available_from:
        payload["availableFrom"] = studapart.available_from
    
    if studapart.available_to:
        payload["availableTo"] = studapart.available_to
    
    if studapart.property_types:
        payload["propertyTypes"] = studapart.property_types
    
    return payload


def extract_properties(data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Extract property information from API response.
    
    Args:
        data: Raw API response data
        
    Returns:
        List of formatted property dictionaries
    """
    properties = []
    
    # Handle different response formats
    items = data.get("hits", data.get("results", data.get("items", [])))
    
    if not items:
        logging.warning("No items found in API response")
        return properties
    
    for item in items:
        try:
            property_info = extract_single_property(item)
            if property_info:
                properties.append(property_info)
        except Exception as e:
            logging.warning(f"Error extracting property: {e}")
            continue
    
    return properties


def extract_single_property(item: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Extract information from a single property item.
    
    Args:
        item: Single property item from API response
        
    Returns:
        Formatted property dictionary or None if extraction fails
    """
    # Handle nested source structure (ElasticSearch format)
    source = item.get("_source", item)
    
    # Extract basic information
    property_id = item.get("_id") or source.get("id") or source.get("propertyId")
    
    # Extract price
    price = source.get("price") or source.get("rent") or source.get("monthlyRent")
    if isinstance(price, dict):
        price = price.get("value") or price.get("amount")
    
    # Extract title
    title = source.get("title") or source.get("name") or source.get("description", "")[:100]
    
    # Extract images
    images = []
    image_data = source.get("images", source.get("photos", source.get("pictures", [])))
    if isinstance(image_data, list):
        for img in image_data:
            if isinstance(img, str):
                images.append(img)
            elif isinstance(img, dict):
                img_url = img.get("url") or img.get("src") or img.get("path")
                if img_url:
                    # Construct full URL if needed
                    if not img_url.startswith("http"):
                        img_url = f"https://media.studapart.com/{img_url}"
                    images.append(img_url)
    
    # Extract main image if available
    main_image = source.get("mainImage") or source.get("coverImage") or source.get("thumbnail")
    if main_image and isinstance(main_image, str):
        if not main_image.startswith("http"):
            main_image = f"https://media.studapart.com/{main_image}"
        if main_image not in images:
            images.insert(0, main_image)
    
    # Extract location information
    location = source.get("location", {})
    if isinstance(location, dict):
        postal_code = location.get("postalCode") or location.get("zipCode")
        city = location.get("city") or location.get("cityName")
        address = location.get("address") or location.get("street")
    else:
        postal_code = source.get("postalCode") or source.get("zipCode")
        city = source.get("city") or source.get("cityName")
        address = source.get("address")
    
    # Extract property details
    rooms = source.get("rooms") or source.get("numberOfRooms") or source.get("nbRooms")
    surface = source.get("surface") or source.get("area") or source.get("size")
    property_type = source.get("propertyType") or source.get("type") or source.get("category")
    
    # Check if charges are included
    charges_included = source.get("chargesIncluded", False)
    if not charges_included:
        charges_included = "CC" in str(source.get("priceLabel", "")).upper()
    
    # Build property URL
    slug = source.get("slug") or source.get("urlSlug")
    if slug:
        url = f"https://www.studapart.com/fr/logement/{slug}"
    elif property_id:
        url = f"https://www.studapart.com/fr/logement/{property_id}"
    else:
        url = None
    
    return {
        "id": str(property_id) if property_id else None,
        "title": title,
        "price": float(price) if price else None,
        "charges_included": charges_included,
        "rooms": int(rooms) if rooms else None,
        "space": float(surface) if surface else None,
        "postal_code": postal_code,
        "city": city,
        "address": address,
        "property_type": property_type,
        "images": images,
        "url": url
    }


def get_available_cities() -> List[str]:
    """
    Get list of available cities with predefined postal codes.
    
    Returns:
        List of city names
    """
    return list(CITY_POSTAL_CODES.keys())
