# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class JobparserItem(scrapy.Item):
    # define the fields for your item here like:
    link = scrapy.Field()
    name = scrapy.Field()
    salary = scrapy.Field()
    min_salary = scrapy.Field()
    max_salary = scrapy.Field()
    source = scrapy.Field()
    _id = scrapy.Field()


class JobparserItem_cbrf(scrapy.Item):
    parse = scrapy.Field()
    _id = scrapy.Field()