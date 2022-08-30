from src.lib.orm_util import DBInstance, get_session_from
from configs import DevMysql

class ScraperEngine:

    def __init__(self, scraper):
        self.scraper = scraper
        self.db = None
        self.connect_db()

    def connect_db(self):
        """ 进行数据库连接 """
        self.db = DBInstance(DevMysql)

    def run(self):
        with get_session_from(self.db) as session:
            self.scraper.set_up(session)
            self.scraper.scrape()
