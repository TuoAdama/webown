from fastapi import FastAPI, Query, HTTPException, Depends
from typing import Optional
import logging
from app.enums.platform import Platform
from app.models.se_loger import SeLoger
from app.models.espacil import Espacil
from app.models.studapart import Studapart
from app.enums.type_searching import TypeSearching
from app.dto.scrape_request import ScrapeRequestDTO
from app.dto.scrape_response import ScrapeResponseDTO, PropertyDTO
import app.scrapers.se_loger.se_loger_scraper as se_loger_scraper
import app.scrapers.espacil.espacil_scraper as espacil_scraper
import app.scrapers.studapart.studapart_scraper as studapart_scraper

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler("logs/api.log"),
        logging.StreamHandler()
    ]
)

app = FastAPI(title="Webown Scraping API", version="1.0.0")

def get_scrape_request(
    ville: str = Query(..., description="City name"),
    code_postal: Optional[str] = Query(None, description="Postal code"),
    prix_max: Optional[float] = Query(None, description="Maximum price"),
    plateforme: str = Query(..., description="Platform name (SeLoger, Espacil, or Studapart)"),
    surface_min: Optional[float] = Query(None, description="Minimum surface area in m²")
) -> ScrapeRequestDTO:
    """Dependency function to create ScrapeRequestDTO from query parameters"""
    return ScrapeRequestDTO(
        ville=ville,
        code_postal=code_postal,
        prix_max=prix_max,
        plateforme=plateforme,
        surface_min=surface_min
    )

@app.get("/scrape", response_model=ScrapeResponseDTO)
async def scrape_properties(
    request: ScrapeRequestDTO = Depends(get_scrape_request)
):
    """
    Scrape properties from different platforms based on search criteria.
    
    Parameters:
    - ville: City name (required)
    - code_postal: Postal code (optional)
    - prix_max: Maximum price (optional)
    - plateforme: Platform name - SeLoger, Espacil, or Studapart (required)
    - surface_min: Minimum surface area in m² (optional)
    
    Returns:
    ScrapeResponseDTO with list of properties found on the specified platform
    """
    try:
        # Get platform enum
        platform_enum = Platform[request.plateforme.upper()]
        
        results = None
        
        if platform_enum == Platform.SELOGER:
            # Create SeLoger model
            se_loger = SeLoger(request.ville, TypeSearching.RENT)
            
            if request.code_postal:
                se_loger.set_postal_code(request.code_postal)
            
            if request.prix_max:
                se_loger.set_max_price(request.prix_max)
            
            if request.surface_min:
                se_loger.set_space_min(request.surface_min)
            
            # Scrape SeLoger
            results = se_loger_scraper.scrape(se_loger)
            
            # Convert results to PropertyDTO
            if results:
                property_dtos = []
                for result in results:
                    try:
                        if hasattr(result, '__dict__'):
                            result_dict = result.__dict__
                        else:
                            result_dict = result
                        property_dtos.append(PropertyDTO(**result_dict))
                    except Exception as e:
                        logging.warning(f"Error converting result to PropertyDTO: {str(e)}, result: {result}")
                        continue
                results = property_dtos
        
        elif platform_enum == Platform.ESPACIL:
            # Create Espacil model
            espacil = Espacil(request.ville)
            
            if request.prix_max:
                espacil.price_max = int(request.prix_max)
            
            if request.surface_min:
                espacil.surface_min = request.surface_min
            
            # Scrape Espacil
            raw_results = espacil_scraper.scrape(espacil)
            
            # Convert results to PropertyDTO
            if raw_results:
                property_dtos = []
                for result in raw_results:
                    try:
                        property_dtos.append(PropertyDTO(**result))
                    except Exception as e:
                        logging.warning(f"Error converting result to PropertyDTO: {str(e)}, result: {result}")
                        continue
                results = property_dtos
        
        elif platform_enum == Platform.STUDAPART:
            # Create Studapart model
            studapart = Studapart(request.ville)
            
            if request.prix_max:
                studapart.price_max = int(request.prix_max)
            
            # Scrape Studapart
            raw_results = studapart_scraper.scrape(studapart)
            
            # Convert results to PropertyDTO
            if raw_results:
                property_dtos = []
                for result in raw_results:
                    try:
                        property_dtos.append(PropertyDTO(**result))
                    except Exception as e:
                        logging.warning(f"Error converting result to PropertyDTO: {str(e)}, result: {result}")
                        continue
                results = property_dtos
        
        if results is None or len(results) == 0:
            return ScrapeResponseDTO(
                status="error",
                message="No results found or scraping failed",
                platform=request.plateforme,
                count=0,
                results=[]
            )
        
        return ScrapeResponseDTO(
            status="success",
            platform=request.plateforme,
            count=len(results),
            results=results
        )
    
    except ValueError as e:
        logging.error(f"Validation error: {str(e)}")
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
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

