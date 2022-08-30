import os
import re

from tqdm import tqdm
from bs4 import BeautifulSoup
import requests

from src.lib.log import logger
from src.lib.exception import ScraperException, ParseError
from configs import BESTIARY_INDEX, TIMEOUT, BESTIARY_FILE_ROOT, INBOX_FILE_ROOT
from src.models.bestiary_model import Bestiary

# NEW_LINE = "\n"
OFFENSE_TITLES = ["攻击能力", "进攻能力", "攻击", "进攻"]
DEFENSE_TITLES = [ "防御能力", "防御",]
STAT_TITLES = ["基础数据", "数据", "属性值", "属性", "状态", "统计"]
ECOLOGY_TITLES = ["生态环境", "生态Ecology", "环境", "生态"]
SPECIAL_ABILITY_TITLES = ["特殊能力", "特殊能力Special Abilities"]


class BestiaryScraper:

    def set_up(self, session):
        self.session = session
        self.error_count = 0

    def scrape(self) -> None:
        logger.info("开始{}的爬取任务".format(self.__class__.__name__))
        links = self._get_bestiary_links()

        count = 0
        for name, link in tqdm(links.items()):
            count += 1
            if count < 0:
                continue
            try:
                # print(name)
                bestiary = Bestiary()
                page = self._get_bestiary_bs(name, link, bestiary)
                bestiary, text_remaining = self._parse_page(page, bestiary)
                self._save(bestiary, text_remaining)
            except ScraperException as e:
                logger.exception(e)
        logger.info("完成{}的爬取任务，有{}个处理异常".format(self.__class__.__name__, self.error_count))


    def _get_bestiary_links(self, source='local') -> dict:
        links = dict()
        if source == 'web':
            response = requests.get(BESTIARY_INDEX, timeout=TIMEOUT)
            bs = BeautifulSoup(response.text, 'html5lib')
            tables = bs.find_all("table", {"class", "bbc_table"})
            for table in tables:
                for a in table.find_all("a"):
                    link = a.attrs['href']
                    link_name = re.sub('/', '|', a.text)
                    link_name = re.sub('[^（）()]*?，', '', link_name)
                    if not re.search("模板|绪论", link_name):
                        links[link_name] = link
        else:
            files = [f for f in os.listdir(INBOX_FILE_ROOT) if f.endswith('.txt')]
            for file in files:
                link_name = re.sub('\.txt', '', file)
                links[link_name] = ''
        return links

    def _get_bestiary_bs(self, link_name: str, link: str, bestiary):
        bestiary.file_name = link_name+".txt"
        bestiary.identifier = re.sub("（.*）", "", link_name)
        file_path = os.path.join(INBOX_FILE_ROOT, bestiary.file_name)

        if os.path.exists(file_path):
            # 如果已经下载过页面html了，直接读取
            with open(file_path, 'r', encoding='utf-8') as f:
                bs = BeautifulSoup(f.read(), 'html5lib')
        else:
            # 否则下载html并存储
            response = requests.get(link, timeout=TIMEOUT)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(response.text)
            bs = BeautifulSoup(response.text, 'html5lib')
        divs = bs.find_all("div", {"class", "post"})
        for div in divs:
            # 检查当前这个是否是需要的div
            div_text = div.text
            if len(div_text) > 300 and re.search(bestiary.identifier, div_text[:200]):
                # 获取贴主信息
                post_a = div.parent.parent.div.h4.find_all("a")[-1]
                bestiary.translator = post_a.text
                return div
        logger.error("没有找到对应的post，识别名：{}，链接：{}".format(bestiary.identifier, link))

    def _parse_page(self, page, bestiary):
        # 文本准备
        for br in page.find_all("br"):
            br.replace_with("\n"+br.text)
        for hr in page.find_all("hr"):
            hr.replace_with("~~")
        for strong in page.find_all("strong"):
            strong.replace_with("~~"+strong.text+"~~")
        text = page.get_text()
        text = re.sub("[─－—=-]{2,}", "~~", text)
        # text = re.sub("~{4,}", "~~", text)
        # if bestiary.identifier == "星海巨兽":
            # print("***")

        # 获取各个块的标题
        offense_title, text = BestiaryScraper._get_and_convert_title(text, OFFENSE_TITLES)
        defense_title, text = BestiaryScraper._get_and_convert_title(text, DEFENSE_TITLES)
        stat_title, text = BestiaryScraper._get_and_convert_title(text, STAT_TITLES)
        try:
            ecology_title, text = BestiaryScraper._get_and_convert_title(text, ECOLOGY_TITLES)
        except ParseError as e:
            ecology_title = None
        try:
            special_ability_title, text = BestiaryScraper._get_and_convert_title(text, SPECIAL_ABILITY_TITLES)
        except ParseError as e:
            special_ability_title = None

        # 抽取各个块的内容
        bestiary.basic, text = BestiaryScraper._re_extract("((?s:.*?))(?=EOB)", text)
        bestiary.defense, text = BestiaryScraper._re_extract("(?<=EOB){}((?s:.*?))(?=EOB)".format(defense_title), text)
        bestiary.offense, text = BestiaryScraper._re_extract("(?<=EOB){}((?s:.*?))(?=EOB)".format(offense_title), text)
        bestiary.statistics, text = BestiaryScraper._re_extract("(?<=EOB){}((?s:.*?))(?=EOB)".format(stat_title), text)
        if ecology_title:
            bestiary.ecology, text = BestiaryScraper._re_extract("(?<=EOB){}((?s:.*?))(?=(EOB)|$)".format(ecology_title), text)
        if special_ability_title:
            bestiary.special_ability, text = BestiaryScraper._re_extract("(?<=EOB){}((?s:.*?))(?=(EOB)|$)".format(special_ability_title), text)

        # print(text)
        # 处理遗留文本的转义符号
        text = re.sub("EOB", "", text)
        return bestiary, text

    def _save(self, bestiary, text_remaining):
        if re.fullmatch("\s*", text_remaining):
            os.rename(os.path.join(INBOX_FILE_ROOT, bestiary.file_name), os.path.join(BESTIARY_FILE_ROOT, bestiary.file_name))
        else:
            self.error_count += 1

    @staticmethod
    def _get_and_convert_title(text, titles) -> (str, str):
        for title in titles:
            for regex in ["~~\s*{}\s*~~\n", "~~\s*{}\s*~~", "{}\s*~~", "~~\s*{}"]:
                title_regex = regex.format(title)
                if re.search(title_regex, text):
                    text = re.sub(title_regex, "\n\nEOB{}".format(title), text)
                    return title, text
        for title in titles:
            for regex in ["\n{}\s"]:
                title_regex = regex.format(title)
                if re.search(title_regex, text):
                    text = re.sub(title_regex, "\n\nEOB{}\n\n".format(title), text)
                    return title, text
        raise ParseError("在文本中未能找到{}，文本内容：{}".format(titles, text))

    @staticmethod
    def _re_extract(regex, text):
        matched = re.search(regex, text)
        if not matched:
            raise ParseError("在文本中未能找到正则表达式 {} 匹配的内容，文本内容：{}".format(regex, text))
        matched = matched.group(1)
        matched = re.sub("~~", "**", matched)
        text = re.sub(regex, "", text, count=1)
        return matched, text
