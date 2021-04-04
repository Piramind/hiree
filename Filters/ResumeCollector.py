# -*- coding: utf-8 -*-

from .ParentFilter import *
from transliterate import translit
# from abc import ABCMeta, abstractmethod


class ResumeCollector(ParentFilter):
    __metaclass__ = ABCMeta

    def __init__(self, position: str, number_of_resumes: int, area: str, file_name: str):
        super().__init__(file_name)
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


'''
---------------------------------------------------- в доработке ----------------------------------------------------
'''


class rabotaResumeCollector(ResumeCollector):  # для Rabota.ru не получается искать больше 20 резюме
    def __init__(self, position: str, number_of_resumes: int, area=4, file_name="rabota_res.txt"):
        super().__init__(position, number_of_resumes, area, file_name)

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

        with open(self.file_name, 'w', encoding='utf-8') as f:
            total = len(all_links)
            f.write(str(total) + '\n')
            i = 0
            while i < total:
                f.write(all_links[i] + '\n')
                i += 1

# https://rabota.ru/v3_searchResumeByParamsResults.html?action=search&area=v3_searchResumeByParamsResults&qk[0]=self.position&krl[]=self.area
# krl[]=4 номер города

# https://rabota.ru/resume20218457.html?res_page=view
