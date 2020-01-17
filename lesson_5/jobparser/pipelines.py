# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
from pymongo import MongoClient
import xml.dom.minidom as minidom
import numpy as np
import re


class JobparserPipeline(object):

    def __init__(self):
        client = MongoClient('localhost', 27017)
        self.mongo_base = client.vacansy
        self.headers = {'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) \
                                        AppleWebKit/537.36 (KHTML, like Gecko) \
                                        Chrome/78.0.3904.108 Safari/537.36'}
        self.code = {"USD": "USD",
                     "AZN": "AZN",
                     "KZT": "KZT",
                     "грн.": "UAH",
                     "бел. руб.": "BYN",
                     "бел.руб.": "BYN",
                     "руб.": "RUR",
                     '₽': "RUR",
                     "EUR": "EUR",
                     "сум": "UZS", }

        self.courses = ''

    def process_item(self, item, spider):
        if spider.name == 'cbrf':
            cbrf_courses = self.__get_cbrf(item)
            cbrf = self.mongo_base[spider.name]
            for cbrf_course in cbrf_courses:
                cbrf.update_one({'course': cbrf_course['course']}, {'$set': cbrf_course}, upsert=True)
            return item
        if spider.name == 'hhru':
            item = self.__split_salary(item)
            item['source'] = 'HeadHunter'
            collection = self.mongo_base[spider.name]
            collection.update_one({'link': item['link']}, {'$set': item}, upsert=True)
        if spider.name == 'sjru':
            item = self.__split_salary(item)
            item['source'] = 'SuperJob'
            collection = self.mongo_base[spider.name]
            collection.update_one({'link': item['link']}, {'$set': item}, upsert=True)
        return item

    # обработать xml от api цб рф и загрузить в бд 'код валюты':'курс к рублю'
    def __get_cbrf(self, item):
        link_cbrf = item['parse']
        parsing_cbrf = minidom.parseString(link_cbrf)

        currency = list(map(lambda x: x.childNodes[0].nodeValue, parsing_cbrf.getElementsByTagName('CharCode')))
        nominal = np.array(
            list(map(lambda x: int(x.childNodes[0].nodeValue), parsing_cbrf.getElementsByTagName('Nominal'))))
        course = np.array(list(map(lambda x: float(x.childNodes[0].nodeValue.replace(',', '.')),
                                   parsing_cbrf.getElementsByTagName('Value'))))

        course = list(course / nominal)
        courses_cbrf = [{'currency': currency[i], 'course': course[i]} for i, v in enumerate(currency)]
        courses_cbrf.append({'currency': 'RUR', 'course': 1})

        return courses_cbrf

    # выгрузка из бд 'код валюты':'курс к рублю'
    # выгружается один раз для каждого паука
    def __get_courses(self):
        try:
            self.courses = self.mongo_base['cbrf'].find()
            self.courses = {c['currency']: c['course'] for c in self.courses}
        except:
            pass

    # получить ставку конкретной валюты
    def __get_course(self, courses, currency):
        course = courses[self.code[currency]]

        return course

    def __split_salary(self, item_max_min):
        # если словаря с валютами еще нет, то выгружаем его из бд
        if not self.courses:
            self.__get_courses()

        courses = self.courses

        salary = item_max_min['salary']

        # если в поле зарплаты нашли цифры, предположительно это и есть зарплата, значит надо ее преобразовать
        if salary and re.search(r'\d+', ''.join(salary)):
            min_c, max_c = self.__max_min_compensation(courses, salary)
        else:
            min_c, max_c = 'NaN', 'NaN'
        # сложим max и min в item и удалим оттуда исходные данные о зарплате
        item_max_min['min_salary'] = min_c
        item_max_min['max_salary'] = max_c
        del item_max_min['salary']

        return item_max_min

    def __max_min_compensation(self, courses, salary):
        # бывает в salary попадает информация о зарплате одной строкой, а бывает списком
        # нам нужен гарантированный список
        if len(salary) == 1:
            if type(salary[0]) != 'list':
                salary = salary[0].split()
            else:
                salary = salary[0]
        # уберем люшнюю информацию
        for i, c in enumerate(salary):
            c = c.strip()
            c = c.replace('\xa0', '')
            salary[i] = c
            # слева на право как только наткнемся на наименование валюты окончание отбросим
            if c != '' and c in self.code.keys():
                salary = ' '.join(salary[:i + 1:])
                break
        # разделим на показателях зп и валюте
        max_min = ''.join(salary.split()[:-1:])
        currency = salary.split()[-1]
        # получим конкретную котировку
        course = self.__get_course(courses, currency)

        down = re.match(r'от', max_min)
        up = re.match(r'до', max_min)
        # найдем границы зп
        max_min = re.findall(r'\d+', max_min)
        max_min = list(map(int, max_min))

        if currency != 'руб.':
            max_min = list(map(lambda x: x * course, max_min))
        # определим максимальную и минимальную зп
        if len(max_min) > 1:
            max_compensation = max(max_min)
            min_compensation = min(max_min)
        else:
            if down:
                min_compensation = max_min[0]
                max_compensation = 'NaN'
            elif up:
                min_compensation = 'NaN'
                max_compensation = max_min[0]
            elif not down and not up:
                max_compensation = max_min[0]
                min_compensation = max_min[0]

        return min_compensation, max_compensation
