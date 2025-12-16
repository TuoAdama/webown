import app.scrapers.se_loger.se_loger_scraper as se_loger_scraper
from app.models.se_loger import SeLoger

se_loger = SeLoger("Paris")
se_loger.set_min_price(500)
se_loger.set_max_price(1000)
results = se_loger_scraper.scrape(se_loger)

if results is not None:
    for result in results:
        if result is not None:
            print(result.__dict__)
else:
    print("No results found")