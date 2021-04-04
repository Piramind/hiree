# -*- coding: utf-8 -*-
from Filters.ResumeCollector import ResumeCollector
from bs4 import BeautifulSoup
from tqdm import tqdm


class superjobResumeCollector(ResumeCollector):
    def __init__(self, position: str, number_of_resumes: int, area: str = 'spb.', file_name: str = "sj_RESULT.txt"):
        pos = translit(position, reversed=True).replace(' ', '-')
        super().__init__(pos, number_of_resumes, area, file_name)

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
        print("SuperJob: Собираем ссылки на резюме...")
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

        super()._write_result_links(self.file_name, all_links, False)
        print("Проверено", total, "вакансий.")
