# -*- coding: utf-8 -*-
from Filters.GenderFilter import GenderFilter
from bs4 import BeautifulSoup
from tqdm import tqdm
# import pymorphy2


class sjGenderFilter(GenderFilter):

    def __init__(self, desired_gender: str = "мужчина", file_name: str = "sj_RESULT.txt"):
        super().__init__(desired_gender, file_name)

    def run(self) -> None:
        print("SuperJob: Проверяем пол...")
        result_links = []

        with open(self.file_name, 'r', encoding='utf-8') as file:
            progress = int(file.readline().strip())
            pbar = tqdm(total=progress)
            i = 0
            while i < progress:
                link = file.readline().strip()
                html = super()._get_html(link)
                soup = BeautifulSoup(html, 'lxml')
                gender_data = soup.find('span', class_="_1h3Zg _2GvXy _2hCDz _2ZsgW")

                if gender_data is None:
                    print('None')
                    result_links += [link]
                    i += 1
                    pbar.update()
                    continue

                if "готов" in gender_data.text and self.desired_gender == "мужчина":
                    result_links += [link]
                elif "готова" in gender_data.text and self.desired_gender == "женщина":
                    result_links += [link]

                i += 1
                pbar.update()
            pbar.close()
        super()._write_result_links(self.file_name, result_links)
