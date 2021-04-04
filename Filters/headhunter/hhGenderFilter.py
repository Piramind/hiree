# -*- coding: utf-8 -*-
from Filters.GenderFilter import GenderFilter
from bs4 import BeautifulSoup
from tqdm import tqdm


class hhGenderFilter(GenderFilter):

    def __init__(self, desired_gender: str = "мужчина", file_name: str = "hh_RESULT.txt"):
        super().__init__(desired_gender, file_name)

    def run(self):
        print("Проверяем пол...")
        result_links = []
        with open(self.file_name, 'r', encoding='utf-8') as file:
            progress = int(file.readline().strip())
            pbar = tqdm(total=progress)
            i = 0
            while i < progress:
                link = file.readline().strip()
                html = super()._get_html(link)
                soup = BeautifulSoup(html, 'lxml')
                personal_gender = soup.find(attrs={"data-qa": "resume-personal-gender"})
                if not personal_gender:
                    result_links += [link]
                    continue
                if personal_gender.get_text().strip().lower() == self.desired_gender:
                    result_links += [link]
                i += 1
                pbar.update()
            pbar.close()
        super()._write_result_links(self.file_name, result_links)
