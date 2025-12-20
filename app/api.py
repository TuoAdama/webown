from fastapi import FastAPI, Query, HTTPException
from typing import Optional
import logging
from app.enums.platform import Platform
from app.models.se_loger import SeLoger
from app.models.espacil import Espacil
from app.enums.type_searching import TypeSearching
import app.scrapers.se_loger.se_loger_scraper as se_loger_scraper
import app.scrapers.espacil.espacil_scraper as espacil_scraper

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler("logs/api.log"),
        logging.StreamHandler()
    ]
)

app = FastAPI(title="Webown Scraping API", version="1.0.0")

@app.get("/scrape")
async def scrape_properties(
    ville: str = Query(..., description="City name"),
    code_postal: Optional[str] = Query(None, description="Postal code"),
    prix_max: Optional[float] = Query(None, description="Maximum price"),
    plateforme: str = Query(..., description="Platform name (SeLoger or Espacil)"),
    surface_min: Optional[float] = Query(None, description="Minimum surface area in m²")
):
    """
    Scrape properties from different platforms based on search criteria.
    
    Parameters:
    - ville: City name (required)
    - code_postal: Postal code (optional)
    - prix_max: Maximum price (optional)
    - plateforme: Platform name - SeLoger or Espacil (required)
    - surface_min: Minimum surface area in m² (optional)
    
    Returns:
    List of properties found on the specified platform
    """
    try:
        # Validate platform
        try:
            platform_enum = Platform[plateforme.upper()]
        except KeyError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid platform. Supported platforms: {[p.value for p in Platform]}"
            )
        
        results = None
        
        if platform_enum == Platform.SELOGER:
            # Create SeLoger model
            se_loger = SeLoger(ville, TypeSearching.RENT)
            
            if code_postal:
                se_loger.set_postal_code(code_postal)
            
            if prix_max:
                se_loger.set_max_price(prix_max)
            
            if surface_min:
                se_loger.set_space_min(surface_min)
            
            # Scrape SeLoger
            results = se_loger_scraper.scrape(se_loger)
            
            # Convert results to dictionaries if needed
            if results:
                results = [result.__dict__ if hasattr(result, '__dict__') else result for result in results]
        
        elif platform_enum == Platform.ESPACIL:
            # Create Espacil model
            espacil = Espacil(ville)
            
            if prix_max:
                espacil.price_max = int(prix_max)
            
            if surface_min:
                espacil.surface_min = surface_min
            
            # Scrape Espacil
            results = espacil_scraper.scrape(espacil)
        
        if results is None:
            return {
                "status": "error",
                "message": "No results found or scraping failed",
                "results": []
            }
        
        return {
            "status": "success",
            "platform": plateforme,
            "count": len(results),
            "results": results
        }
    
    except Exception as e:
        logging.error(f"Error during scraping: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@app.get("/")
async def root():
    """
    Root endpoint with API information
    """
    return {
        "name": "Webown Scraping API",
        "version": "1.0.0",
        "endpoints": {
            "/scrape": "GET - Scrape properties from different platforms"
        }
    }

@app.get("/health")
async def health_check():
    """
    Health check endpoint
    """
    return {"status": "healthy"}

