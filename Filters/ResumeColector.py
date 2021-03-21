# -*- coding: utf-8 -*-

from .ParentFilter import *
# from abc import ABCMeta, abstractmethod


class ResumeColector(ParentFilter):
    __metaclass__ = ABCMeta

    def __init__(self, position: str, number_of_resumes: int, area: int, writefile_name: str):
        super().__init__(writefile_name,  writefile_name)
        self.position = position.lower().replace(' ', '+')
        self.number_of_resumes = number_of_resumes
        self.area = str(area)

    # Собирает ссылки на резюме с глобальной страницы
    @abstractmethod
    def _get_resumes_links(self, html) -> tuple:
        raise NotImplementedError

    # Запуск фильтра
    @abstractmethod
    def run(self):
        super().run()


class hhResumeColector(ResumeColector):

    def __init__(self, position: str, number_of_resumes: int, area: int = 2, writefile_name: str = "hh_res.txt"):
        super().__init__(position, number_of_resumes, area, writefile_name)

    def _get_resumes_links(self, html) -> tuple:
        # новый объект класса BeutifulSoup
        soup = BeautifulSoup(html, 'lxml')
        new_links = ()
        links = soup.find_all('a', class_='resume-search-item__name')
        i = 0
        while i < len(links):
            new_links += ("".join(tuple(("http://hh.ru", links[i].get('href')))),)
            i += 1
        return new_links

    # Функция, которая для данного запроса и региона ищет все страницы с результатами поиска и набирает большой список со всеми ссылками на вакансии возвращает список ссылок по запросу position в регионе с кодом area
    def run(self) -> None:
        print("Собираем глобальные ссылки...")
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


'''
class rabotaResumeColector(ResumeColector):
    def __init__(self, position: str, number_of_resumes: int, area=2, writefile_name="rabota_resumes.txt"):
        super().__init__(position, number_of_resumes, area, writefile_name)

    def get_resumes_links_rabot(html):
        # новый объект класса BeutifulSoup
    soup = BeautifulSoup(html, 'lxml')
    new_links_rab = []
    links = soup.find_all('a', class_='search-title vm ')
    for link in links:
        link_parsed = ("http://rabota.ru") + link.get('href')
        new_links_rab += [link_parsed]
    return new_links_rab
'''
