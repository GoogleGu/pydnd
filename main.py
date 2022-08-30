import os

from src.scrapers.bestiary_scraper import BestiaryScraper
from src.core.engine import ScraperEngine
from src.lib.log import logger
from configs import FILE_ROOT

if __name__ == '__main__':
    logger.loguru_logger.add(os.path.join(FILE_ROOT, 'bestiary.log'), encoding='utf-8', filter=lambda record: record["level"].name == "ERROR")
    scraper = BestiaryScraper()
    engine = ScraperEngine(scraper=scraper)
    engine.run()
