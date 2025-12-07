import app.scrapers.se_loger.se_loger_scraper as se_loger_scraper
from app.models.se_loger import SeLoger

se_loger = SeLoger("Bordeau")
se_loger.set_min_price(500)
se_loger.set_max_price(1000)
se_loger_scraper.scrape(se_loger)