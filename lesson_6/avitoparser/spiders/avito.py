# -*- coding: utf-8 -*-

import scrapy
from scrapy.http import HtmlResponse
from avitoparser.items import AvitoparserItem
from scrapy.loader import ItemLoader


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
        loader = ItemLoader(item=AvitoparserItem(), response=response)
        loader.add_css('name', 'h1.title-info-title span.title-info-title-text::text')
        loader.add_xpath('photos',
                         '//div[contains(@class, "gallery-img-wrapper")]//div[contains(@class, "gallery-img-frame")]/@data-url')
        loader.add_xpath('param_name', '//div[@class="item-params"]//li[@class="item-params-list-item"]//span/text()')
        loader.add_xpath('param_value',
                         '//div[@class="item-params"]//li[@class="item-params-list-item"]/text() | //div[@class="item-params"]//li[@class="item-params-list-item"]//a/text()')
        loader.add_xpath('price', '//div[@class="item-price-value-wrapper"]//span[@class="js-item-price"]/@content')
        yield loader.load_item()
