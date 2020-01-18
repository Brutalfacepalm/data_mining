from bs4 import BeautifulSoup as bs
import requests
import lxml
import re
import json
import pandas as pd
import xml.dom.minidom as minidom


class Parsing_HH():

    def __init__(self):

        self.headers = {'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) \
                                AppleWebKit/537.36 (KHTML, like Gecko) \
                                Chrome/78.0.3904.108 Safari/537.36'}
        #         Атрибуты для парсинга
        self.main_link = 'https://saratov.hh.ru/search/vacancy?L_is_autosearch=false&clusters=true&enable_snippets=true&items_on_page=20&text='
        self.title_findAll_attrs = ['h1', {'class': 'header', 'data-qa': 'page-title'}]
        self.current_page_find_attrs = ['div', {'class': 'vacancy-serp'}]
        self.items_find_attrs = ['div', {'class': 'vacancy-serp-item'}]
        self.pagers_1_find_attrs = ['div', {'data-qa': 'pager-block'}]
        self.pagers_2_find_attrs = ['a', {'data-qa': 'pager-page'}]
        self.name_find_attrs = ['a', {'data-qa': 'vacancy-serp__vacancy-title'}]
        self.href_main = ''
        self.compensation_find_attrs = ['div', {'data-qa': 'vacancy-serp__vacancy-compensation'}]
        self.company_find_attrs = ['a', {'data-qa': 'vacancy-serp__vacancy-employer'}]
        self.city_find_attrs = ['span', {'data-qa': 'vacancy-serp__vacancy-address'}]
        self.source = 'HeadHunter'

    #         Получим курсы валют с ЦБ РФ
    def get_cbrf(self):
        link_cbrf = 'http://www.cbr.ru/scripts/XML_daily.asp'
        resp_cbrf = requests.get(link_cbrf, headers=self.headers).text
        parsing_cbrf = minidom.parseString(resp_cbrf)

        currency = list(map(lambda x: x.childNodes[0].nodeValue, parsing_cbrf.getElementsByTagName('CharCode')))
        course = list(map(lambda x: float(x.childNodes[0].nodeValue.replace(',', '.')),
                          parsing_cbrf.getElementsByTagName('Value')))
        nominal = list(map(lambda x: float(x.childNodes[0].nodeValue.replace(',', '.')),
                          parsing_cbrf.getElementsByTagName('Nominal')))
        courses_cbrf = dict(zip(currency, map(lambda x: x[0]/x[1], zip(course, nominal))))
        courses_cbrf['RUR'] = 1

        return courses_cbrf

    #     Сформируем текст для поиска в адресную строку
    def __text_get(self, text):
        text = '+'.join(text.split())

        return text

    #     Парсинг HTML по заданному адресу link
    def __html_parsed(self, link):
        response = requests.get(link, headers=self.headers)
        if response.status_code != 200:
            print(response.status_code)
            return 'Ошибка GET запроса'
        else:
            parsed = bs(response.text, 'lxml')
            return parsed

    #     Сбор информации о результатах поиска
    def __title(self, html_parsed):
        title = html_parsed.findAll(*self.title_findAll_attrs)
        title = title[0].get_text().replace('\xa0', ' ')

        return title

    #     Получение блока с данными на текущей странице
    def __parsed_current_items_block(self, html_parsed):
        current_page = html_parsed.find(*self.current_page_find_attrs)

        return current_page

    #     Получиение списка элементов для дальнейшего парсинга
    def __get_items(self, current_page):
        items = current_page.findAll(*self.items_find_attrs)

        return items

    #     Получение количества страниц результатов поиска
    def _pages(self, html_parsed):
        pagers = html_parsed.findAll(*self.pagers_1_find_attrs)

        if pagers:
            pagers = pagers[0].findAll(*self.pagers_2_find_attrs)
            p = list(map(lambda x: x.get_text(), pagers))
            p = list(map(int, filter(lambda x: re.match(r'\d+', x), p)))

            return range(min([max(p), self.input_pages]))
        else:
            return [0]

    #     Получение названия каждого элемента
    def _get_name(self, names, hrefs, item):

        name = item.find(*self.name_find_attrs)
        if name:
            names.append(name.get_text())
            href = name['href']
            hrefs.append(href)
        else:
            names.append('NaN')

    #     Получение курса конкретной валюты
    def __get_course(self, courses, currency):
        code = {"USD": "USD",
                "AZN": "AZN",
                "KZT": "KZT",
                "грн.": "UAH",
                "бел. руб.": "BYR",
                "руб.": "RUR",
                '₽': "RUR",
                "EUR": "EUR", }

        course = courses[code[currency]]

        return course

    #     Разбор зарплаты на минимальную и максимальную
    def __max_min_compensation(self, courses, compensation):
        max_min = ''.join(compensation.get_text().split()[:-1:])
        currency = compensation.get_text().split()[-1]

        course = self.__get_course(courses, currency)

        down = re.match(r'от', max_min)
        up = re.match(r'до', max_min)

        max_min = re.findall(r'\d+', max_min)
        max_min = list(map(int, max_min))

        if currency != 'руб.':
            max_min = list(map(lambda x: x * course, max_min))

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

    #     Получение информации о зарплате
    def __get_compensation(self, min_compensation, max_compensation, item, courses):

        compensation = item.find(*self.compensation_find_attrs)

        if compensation and re.match(r'\d+', compensation.get_text()):
            min_c, max_c = self.__max_min_compensation(courses, compensation)
        else:
            min_c, max_c = 'NaN', 'NaN'

        min_compensation.append(min_c)
        max_compensation.append(max_c)

    #     Получение информации о компании
    def __get_company(self, companies, item):

        company = item.find(*self.company_find_attrs)
        if company:
            companies.append(company.get_text())
        else:
            companies.append('NaN')

    #     Получение информации о городе вакансии
    def _get_city(self, cities, item):

        city = item.find(*self.city_find_attrs)
        if city:
            cities.append(city.get_text().split(',')[0])
        else:
            cities.append('NaN')

    #         Входные данные
    def _get_input(self, text, input_pages):
        self.text = '+'.join(text.split())
        self.input_pages = input_pages
        self.title_NaN = f'По запросу «{self.text}» ничего не найдено'

        return self.text, self.input_pages, self.title_NaN

    def search(self, text, input_pages):
        #         Входные данные
        self.text, self.input_pages, self.title_NaN = self._get_input(text, input_pages)

        #         Получаем текст для поиска, запускаем поиск, парсим и смотрим на результаты поиска
        text = self.text
        html_parsed = self.__html_parsed(self.main_link + text)
        title = self.__title(html_parsed)
        #         Формируем список страниц от 0 до заданного значения или максимальных результатов поиска, смотря что меньше
        pages = self._pages(html_parsed)
        #         Запросим курсы всех валют с сайта ЦБ РФ
        courses = self.get_cbrf()

        names = []
        min_compensation = []
        max_compensation = []
        hrefs = []
        sources = []
        companies = []
        cities = []

        #         Если поиск дал результаты, то:
        if title != self.title_NaN:
            for i in pages:
                #         Парсим каждую страницу отдельно, получаем блок элементов и затем список элементов
                link = self.main_link + text + f'&page={i}'
                html_parsed = self.__html_parsed(link)
                current_items_block = self.__parsed_current_items_block(html_parsed)

                items = self.__get_items(current_items_block)

                for item in items:
                    #         Находим название вакансии, минимальную и максимальную зарплаты, название компании, город и сайт, откуда собрана инфа
                    self._get_name(names, hrefs, item)
                    self.__get_compensation(min_compensation, max_compensation, item, courses)
                    self.__get_company(companies, item)
                    self._get_city(cities, item)
                    sources.append(self.source)
            #         Складываем всю информацию в соответсвующие списки - будущие столбцы датафрейма

            vacancies = {'Название вакансии': names,
                         'Ссылка': hrefs,
                         'Минимальная зарплата': min_compensation,
                         'Максимальная зарплата': max_compensation,
                         'Площадка': sources,
                         'Компания': companies,
                         'Город': cities}
            #         Формируем датафрейм для сайта, из словаря
            df = pd.DataFrame(vacancies)
            return df
        else:
            print(f'На сайте {self.source} {self.title_NaN}')


class Parsing_SJ(Parsing_HH):

    def __init__(self):
        self.headers = {'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) \
                                AppleWebKit/537.36 (KHTML, like Gecko) \
                                Chrome/78.0.3904.108 Safari/537.36'}
        #         Атрибуты для парсинга
        self.main_link = 'https://www.superjob.ru/vacancy/search/?geo%5Bc%5D%5B0%5D=1&keywords='
        self.title_findAll_attrs = ['span', {
            'class': ['_3mfro _1ZlLP _2JVkc _2VHxz', '_3mfro _1hP6a _2JVkc _2VHxz']}]
        self.current_page_find_attrs = ['div', {'class': '_1Ttd8 _2CsQi'}]
        self.items_find_attrs = ['div', {'class': '_3syPg _3P0J7 _9_FPy'}]
        self.pagers_1_find_attrs = ['div', {'class': 'L1p51'}]
        self.pagers_2_find_attrs = ['span', {'class': '_23m0W'}]
        self.name_find_attrs = ['div', {'class': '_3mfro CuJz5 PlM3e _2JVkc _3LJqf'}]
        self.href_main = 'https://www.superjob.ru'
        self.compensation_find_attrs = ['span', {
            'class': '_3mfro _2Wp8I f-test-text-company-item-salary PlM3e _2JVkc _2VHxz'}]
        self.company_find_attrs = ['a', {'class': 'Vm5jz'}]
        self.city_find_attrs = ['span',
                                {'class': '_3mfro f-test-text-company-item-location _9fXTd _2JVkc _3e53o'}]
        self.source = 'SuperJob'

    #         Входные данные
    def _get_input(self, text, input_pages):
        self.text = '%20'.join(text.split())
        self.input_pages = input_pages
        self.title_NaN = 'Вакансий не найдено'

        return self.text, self.input_pages, self.title_NaN

    #     Переопределяем поиск названия и ссылки для SuperJob, так как структура сайта отличается от HeadHunter
    def _get_name(self, names, hrefs, item):

        name = item.find(*self.name_find_attrs)
        if name:
            names.append(name.get_text())
            href = self.href_main + name.find_parent('div').findChild('a')['href']
            hrefs.append(href)
        else:
            names.append('NaN')

    #     Нумерация страниц на SuperJob отличается от HeadHunter. На SJ начинается с 1, на HH с 0
    def _pages(self, html_parsed):
        pagers = html_parsed.findAll(*self.pagers_1_find_attrs)

        if pagers:
            pagers = pagers[0].findAll(*self.pagers_2_find_attrs)
            p = list(map(lambda x: x.get_text(), pagers))
            p = list(map(int, filter(lambda x: re.match(r'\d+', x), p)))

            return range(1, min([max(p), self.input_pages]) + 1)
        else:
            return [1]

    #     Переопределяем поиск города, т.к. на SJ название города стоит в середине блока или в конце, а на HH в начале
    def _get_city(self, cities, item):

        city = item.find(*self.city_find_attrs)
        if city:
            cities.append(city.findChildren('span')[1].get_text().split(',')[0].split(' ')[0])
        else:
            cities.append('NaN')
