from  scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings
from jobparser import settings
from jobparser.spiders.hhru import HhruSpider
from jobparser.spiders.cbrf import CbrfSpider
from jobparser.spiders.sjru import SjruSpider


if __name__ == '__main__':
    crawler_settings = Settings()
    crawler_settings.setmodule(settings)
    process = CrawlerProcess(settings=crawler_settings)
    process.crawl(CbrfSpider) # паук по сбору катировок с API ЦБ РФ
    process.crawl(HhruSpider) # парсинг HH.ru
    process.crawl(SjruSpider) # парсинг SJ.ru
    process.start()