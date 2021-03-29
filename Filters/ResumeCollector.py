# -*- coding: utf-8 -*-

from .ParentFilter import *
from transliterate import translit
# from abc import ABCMeta, abstractmethod


class ResumeCollector(ParentFilter):
    __metaclass__ = ABCMeta

    def __init__(self, position: str, number_of_resumes: int, area: str, writefile_name: str):
        super().__init__(writefile_name,  writefile_name)
        self.position = position.lower()
        self.number_of_resumes = number_of_resumes
        self.area = area

    # Собирает ссылки на резюме с глобальной страницы
    @abstractmethod
    def _get_resumes_links(self, html) -> tuple:
        raise NotImplementedError

    # Запуск фильтра
    @abstractmethod
    def run(self):
        super().run()


class hhResumeCollector(ResumeCollector):

    def __init__(self, position: str, number_of_resumes: int, area: str = '2', writefile_name: str = "hh_res.txt"):
        super().__init__(position.replace(' ', '+'), number_of_resumes, area, writefile_name)

    def _get_resumes_links(self, html) -> tuple:
        # новый объект класса BeutifulSoup
        soup = BeautifulSoup(html, 'lxml')
        new_links = ()
        links = soup.find_all('a', class_='resume-search-item__name')
        i = 0
        while i < len(links):
            new_links += (''.join(tuple(("http://hh.ru", links[i].get('href')))),)
            i += 1
        return new_links

    # Функция, которая для данного запроса и региона ищет все страницы с результатами поиска и набирает большой список со всеми ссылками на вакансии возвращает список ссылок по запросу position в регионе с кодом area
    def run(self) -> None:
        print("Собираем ссылки на резюме...")
        basic_url = "".join(tuple(("https://hh.ru/search/resume?clusters=True", "&area=", self.area,
                                   "&order_by=relevance&logic=normal&pos=position&exp_period=all_time&no_magic=False&st=resumeSearch", "&text=", self.position, "&page=")))
        all_links = ()

        i = 0
        # костыль для hh.ru тк на одной глобальной странице 20 резюме
        pbar = tqdm(total=self.number_of_resumes//20)
        while i < self.number_of_resumes//20:
            url = basic_url+str(i)
            html = super()._get_html(url)
            all_links += self._get_resumes_links(html)
            i += 1
            pbar.update()
        pbar.close()
        print("Проверено", len(all_links), "вакансий.")

        with open(self.writefile_name, 'w', encoding='utf-8') as f:
            total = len(all_links)
            f.write(str(total) + '\n')
            i = 0
            while i < total:
                f.write(all_links[i] + '\n')
                i += 1


class superjobResumeCollector(ResumeCollector):
    def __init__(self, position: str, number_of_resumes: int, area='spb.', writefile_name="superjob_res.txt"):
        pos = translit(position, reversed=True).replace(' ', '-')
        super().__init__(pos, number_of_resumes, area, writefile_name)

    def _get_resumes_links(self, html) -> tuple:
        # новый объект класса BeutifulSoup
        soup = BeautifulSoup(html, 'lxml')
        links = soup.select('a.icMQ_.YYC5F')
        new_links = ()
        i = 0
        while i < len(links):
            new_links += (''.join(tuple(("https://", self.area,
                                         "superjob.ru", links[i].get('href')))),)
            i += 1
        return new_links

    def run(self) -> None:
        print("Собираем ссылки на резюме...")
        # basic_url = ''.join({"https://", self.area, "superjob.ru/resume/",
        #                      self.position, ".html?page="})
        basic_url = "https://"+self.area+"superjob.ru/resume/"+self.position+".html?page="

        all_links = ()

        # костыль для hh.ru тк на одной глобальной странице 30 резюме
        pbar = tqdm(total=self.number_of_resumes//30)
        i: int = 1
        while i <= self.number_of_resumes//30:
            url = basic_url+str(i)
            html = super()._get_html(url)
            all_links += self._get_resumes_links(html)
            i += 1
            pbar.update()
        pbar.close()
        total = len(all_links)
        print("Проверено", total, "вакансий.")

        with open(self.writefile_name, 'w', encoding='utf-8') as f:
            f.write(str(total) + '\n')
            i = 0
            while i < total:
                f.write(all_links[i] + '\n')
                i += 1


'''
---------------------------------------------------- в доработке ----------------------------------------------------
'''


class rabotaResumeCollector(ResumeCollector):  # для Rabota.ru не получается искать больше 20 резюме
    def __init__(self, position: str, number_of_resumes: int, area=4, writefile_name="rabota_res.txt"):
        super().__init__(position, number_of_resumes, area, writefile_name)

    def _get_resumes_links(self, html) -> tuple:
        # новый объект класса BeutifulSoup
        soup = BeautifulSoup(html, 'lxml')
        new_links = ()
        links = tuple(link.get('href') for link in soup.find_all(
            'a', class_='js-follow-link-ignore box-wrapper__resume-name'))
        print("found=", len(links), type(links))
        return links

    def run(self) -> None:
        print("Собираем ссылки на резюме...")
        url = "".join(tuple(
            ("https://rabota.ru/v3_searchResumeByParamsResults.html?action=search&area=v3_searchResumeByParamsResults&qk[0]=", self.position, "&krl[]=", self.area)))
        all_links = ()

        i = 0
        pbar = tqdm(total=self.number_of_resumes//20)  # кол-во глобальных ссылок
        while i < self.number_of_resumes//20:
            html = super()._get_html(url)
            all_links += self._get_resumes_links(html)
            i += 1
            pbar.update()
        pbar.close()
        print("Проверено", len(all_links), "вакансий.")

        with open(self.writefile_name, 'w', encoding='utf-8') as f:
            total = len(all_links)
            f.write(str(total) + '\n')
            i = 0
            while i < total:
                f.write(all_links[i] + '\n')
                i += 1

# https://rabota.ru/v3_searchResumeByParamsResults.html?action=search&area=v3_searchResumeByParamsResults&qk[0]=self.position&krl[]=self.area
# krl[]=4 номер города

# https://rabota.ru/resume20218457.html?res_page=view
