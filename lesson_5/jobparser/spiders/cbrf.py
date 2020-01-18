# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import HtmlResponse
from jobparser.items import JobparserItem_cbrf


class CbrfSpider(scrapy.Spider):
    name = 'cbrf'
    allowed_domains = ['cbr.ru']
    start_urls = ['http://www.cbr.ru/scripts/XML_daily.asp']

    def parse(self, response):
        api_cbrf = response.css('*').extract_first()
        if api_cbrf:
            yield JobparserItem_cbrf(parse=api_cbrf)