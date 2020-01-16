# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import HtmlResponse
from jobparser.items import JobparserItem

# 1) Доработать паука в имеющемся проекте, чтобы он формировал item по структуре:
# *Наименование вакансии
# *Зарплата от
# *Зарплата до
# *Ссылку на саму вакансию
# *Сайт откуда собрана вакансия
# И складывал все записи в БД(любую)
#
# 2) Создать в имеющемся проекте второго паука по сбору вакансий с сайта superjob. Паука должен формировать item'ы по аналогичной структуре и складывать данные также в БД


class HhruSpider(scrapy.Spider):
    name = 'hhru'
    allowed_domains = ['hh.ru']
    start_urls = ['https://saratov.hh.ru/search/vacancy?L_is_autosearch=false&clusters=/'
                  'true&enable_snippets=true&items_on_page=20&text=python']

    def parse(self, response:HtmlResponse):
        next_page = response.css('a.HH-Pager-Controls-Next::attr(href)').extract_first()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

        vacansy = response.xpath("//div[@class='vacancy-serp-item__info']//a[@data-qa='vacancy-serp__vacancy-title']/@href").extract()

        if vacansy:
            for link in vacansy:
                yield response.follow(link, callback=self.vacansy_parse)

    def vacansy_parse(self, response:HtmlResponse):
        url = response.url
        name = response.xpath("//div[@class=\'bloko-columns-row\']//h1[@data-qa=\'vacancy-title\']//text()").extract_first()
        salary = response.xpath("//div[@class=\'bloko-columns-row\']//p[@class=\'vacancy-salary\']//text()").extract()
        yield JobparserItem(link=url, name=name, salary=salary)
