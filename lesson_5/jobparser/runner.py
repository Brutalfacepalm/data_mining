from  scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings
from jobparser import settings
from jobparser.spiders.hhru import HhruSpider
from jobparser.spiders.cbrf import CbrfSpider


if __name__ == '__main__':
    crawler_settings = Settings()
    crawler_settings.setmodule(settings)
    process = CrawlerProcess(settings=crawler_settings)
    process.crawl(CbrfSpider)
    process.crawl(HhruSpider)
    process.start()