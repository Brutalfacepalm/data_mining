# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import HtmlResponse
from jobparser.items import JobparserItem


class SjruSpider(scrapy.Spider):
    name = 'sjru'
    allowed_domains = ['superjob.ru']
    start_urls = ['https://www.superjob.ru/vacancy/search/?geo%5Bc%5D%5B0%5D=1&keywords=python']

    def parse(self, response: HtmlResponse):
        next_page = response.css('a.f-test-button-dalshe::attr(href)').extract_first()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

        vacansy = response.xpath("//div[@class='_3syPg _3P0J7 _9_FPy']/div[1]/a/@href").extract()

        if vacansy:
            for link in vacansy:
                yield response.follow(link, callback=self.vacansy_parse)

    def vacansy_parse(self, response: HtmlResponse):
        url = response.url
        name = response.xpath("//h1[@class='_3mfro rFbjy s1nFK _2JVkc']//text()").extract_first()
        salary = response.xpath("//span[@class='_3mfro _2Wp8I ZON4b PlM3e _2JVkc']//text()").extract()
        yield JobparserItem(link=url, name=name, salary=salary)
