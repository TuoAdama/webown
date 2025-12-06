import app.scrapers.se_loger_scraper as se_loger_scraper
from app.models.se_loger import SeLoger

se_loger = SeLoger("Rennes")
se_loger.set_min_price(10)
se_loger.set_max_price(200)

se_loger_scraper.scrape(se_loger)