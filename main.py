import app.scrapers.se_loger_scraper as se_loger_scraper
from app.models.se_loger import SeLoger

se_loger_scraper.scrape(SeLoger("Paris", "44700"))