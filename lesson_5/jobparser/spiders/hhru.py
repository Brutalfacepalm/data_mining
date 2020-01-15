# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import HtmlResponse


class HhruSpider(scrapy.Spider):
    name = 'hhru'
    allowed_domains = ['hh.ru']
    start_urls = [
        'https://hh.ru/search/vacancy?L_save_area=true&clusters=true&enable_snippets=true&text=python&showClusters=true&customDomain=1']

    def parse(self, response: HtmlResponse):
        next_page = response.css('a.HH-Pager-Controls-Next::attr(href)').extract_first()
        yield response.follow(next_page, callback=self.parse)

        vacansy = response.css(
            'div.vacancy-serp__vacancy div.vacancy-serp-item div.vacancy-serp-item__row_header a.bloko-link::attr(href').extract()
        print('!!!!!!!!!!!!!!')
        for link in vacansy:
            yield response.follow(link, callback=self.vacansy_parse)

    def vacansy_parse(self, response: HtmlResponse):
        name = response.xpath('//h1[@class="header"]//span/text()').extract_first()
        salary = response.css('div.vacancy-title p.vacancy-salary::text').extract()
        print(name, salary)
