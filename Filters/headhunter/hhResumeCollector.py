# -*- coding: utf-8 -*-
from Filters.ResumeCollector import ResumeCollector
from bs4 import BeautifulSoup
from tqdm import tqdm


class hhResumeCollector(ResumeCollector):

    def __init__(self, position: str, number_of_resumes: int, area: str = '2', file_name: str = "hh_RESULT.txt"):
        super().__init__(position.replace(' ', '+'), number_of_resumes, area, file_name)

    def _get_resumes_links(self, soup) -> tuple:
        # новый объект класса BeutifulSoup
        new_links = []
        link_data = soup.find_all('a', class_='resume-search-item__name', href=True)
        if link_data is None:
            return []
        links = [l['href'] for l in link_data]

        new_links = tuple(''.join(["https://hh.ru", links[i]]) for i in range(len(links)))

        return new_links

    # Функция, которая для данного запроса и региона ищет все страницы с результатами поиска и набирает большой список со всеми ссылками на вакансии возвращает список ссылок по запросу position в регионе с кодом area
    def run(self) -> None:
        print("HeadHunter: Собираем ссылки на резюме...")
        basic_url = "".join(tuple(("https://hh.ru/search/resume?clusters=True", "&area=", self.area,
                                   "&order_by=relevance&logic=normal&pos=position&exp_period=all_time&no_magic=False&st=resumeSearch", "&text=", self.position, "&page=")))
        all_links = []

        i = 0
        # костыль для hh.ru тк на одной глобальной странице 20 резюме
        pbar = tqdm(total=self.number_of_resumes//20)
        while i < self.number_of_resumes//20:
            url = basic_url+str(i)
            html = super()._get_html(url)
            soup = BeautifulSoup(html, 'lxml')
            all_links += self._get_resumes_links(soup)
            i += 1
            pbar.update()
        pbar.close()

        super()._write_result_links(self.file_name, all_links, False)
        print("Проверено", len(all_links), "вакансий.")
