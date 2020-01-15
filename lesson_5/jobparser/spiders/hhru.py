# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import HtmlResponse
from jobparser.items import JobparserItem


class HhruSpider(scrapy.Spider):
    name = 'hhru'
    allowed_domains = ['hh.ru']
    start_urls = ['https://saratov.hh.ru/search/vacancy?L_is_autosearch=false&clusters=/'
                  'true&enable_snippets=true&items_on_page=20&text=python']

    def parse(self, response:HtmlResponse):
        next_page = response.css('a.HH-Pager-Controls-Next::attr(href)').extract_first()
        yield response.follow(next_page, callback=self.parse)

        vacansy = response.css('div.vacancy-serp div.vacancy-serp-item div.vacancy-serp-item__row_header a.bloko-link::attr(href)').extract()

        for link in vacansy:
            yield response.follow(link, callback=self.vacansy_parse)

    def vacansy_parse(self, response:HtmlResponse):
        name = response.xpath('//h1[@class=\'header\']//span/text()').extract_first()
        salary = response.css('div.vacancy-title p.vacancy-salary::text').extract()
        yield JobparserItem(name=name, salary=salary)
