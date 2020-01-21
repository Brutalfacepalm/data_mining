# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import HtmlResponse
from avitoparser.items import AvitoparserItem


class AvitoSpider(scrapy.Spider):
    name = 'avito'
    allowed_domains = ['avito.ru']
    start_urls = ['https://avito.ru/rossiya/']

    def __init__(self, section):
        super(AvitoSpider, self).__init__()
        self.start_urls = [f'https://avito.ru/rossiya/{section}']

    def parse(self, response: HtmlResponse):
        ads_links = response.xpath('//a[@class="snippet-link"]/@href').extract()
        for link in ads_links:
            yield response.follow(link, callback=self.parse_ads)

    def parse_ads(self, response: HtmlResponse):
        name = response.css('h1.title-info-title span.title-info-title-text::text').extract_first()
        photos = response.xpath('//div[contains(@class, "gallery-img-wrapper")]//div[contains(@class, "gallery-img-frame")]/@data-url').extract()
        yield AvitoparserItem(name=name, photos=photos)

