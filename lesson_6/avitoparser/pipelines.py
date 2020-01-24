# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
from scrapy.pipelines.images import ImagesPipeline
from pymongo import MongoClient
import scrapy
import os
from hashlib import sha1
from urllib.parse import urlparse


class AvitoPhotosPipeline(ImagesPipeline):

    def file_path(self, request, response=None, info=None):
        return self._image_path + '/' + os.path.basename(urlparse(request.url).path)

    def __params(self, names, values):
        names = [n[:-2] for n in names]
        values = [v.rstrip().replace('\xa0', ' ') for v in values if v != ' ']
        return dict(zip(names, values))

    def get_media_requests(self, item, info):
        self._image_path = sha1(f'{item["name"]}'.encode()).hexdigest()

        if item['param_name'] and item['param_value']:
            item['params'] = self.__params(item['param_name'], item['param_value'])
            del item['param_name']
            del item['param_value']
        else:
            item['params'] = {}

        if item['photos']:
            for img in item['photos']:
                try:
                    yield scrapy.Request(img)
                except Exception as e:
                    print(e)

    def item_completed(self, results, item, info):
        if results:
            item['photos'] = [itm[1] for itm in results if itm[0]]
        return item


class DataBasePipeline(object):
    def __init__(self):
        client = MongoClient('localhost', 27017)
        self.mongo_base = client.avito_photo

    def process_item(self, item, spider):
        collection = self.mongo_base[spider.name]
        collection.insert_one(item)
        return item
