# -*- coding: utf-8 -*-
from Filters.ZodiacFilter import ZodiacFilter
from bs4 import BeautifulSoup
from tqdm import tqdm
from re import sub


class hhZodiacFilter(ZodiacFilter):

    def __init__(self, desired_sign: str, file_name: str = "hh_RESULT.txt"):
        super().__init__(desired_sign, file_name)

    def run(self):
        print("Проверяем знак зодиака...")
        total = 0
        result_links = []
        with open(self.file_name, 'r', encoding='utf-8') as file:

            progress = int(file.readline().strip())
            link_ind = 0
            pbar = tqdm(total=progress)

            while link_ind < progress:

                link = file.readline().strip()
                html = super()._get_html(link[:len(link)-4])
                soup = BeautifulSoup(html, 'lxml')

                date_of_birth = soup.find(attrs={"data-qa": "resume-personal-birthday"})
                if not date_of_birth:
                    link_ind += 1
                    pbar.update()
                    continue

                date_of_birth = sub("[^А-Яа-я0-9] ", "", date_of_birth.get_text())
                if self.desired_sign == self._get_zodiac(str(date_of_birth)[:len(date_of_birth)-5]):
                    result_links += [link]
                link_ind += 1
                pbar.update()

            pbar.close()
        super()._write_result_links(self.file_name, result_links)
