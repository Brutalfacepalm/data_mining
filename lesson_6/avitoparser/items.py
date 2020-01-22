# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.loader.processors import MapCompose, TakeFirst


def cleaner_photo(value):
    if value[:2] == '//':
        return f'http:{value}'
    return value


def cleaner_price(value):
    try:
        value = int(value)
        return value
    except Exception as e:
        print(e)


class AvitoparserItem(scrapy.Item):
    _id = scrapy.Field()
    name = scrapy.Field(output_processor=TakeFirst())
    photos = scrapy.Field(input_processor=MapCompose(cleaner_photo))
    param_name = scrapy.Field()
    param_value = scrapy.Field()
    params = scrapy.Field()
    price = scrapy.Field(input_processor=MapCompose(cleaner_price), output_processor=TakeFirst())
