# -*- coding: utf-8 -*-
from Filters.GenderFilter import GenderFilter
from bs4 import BeautifulSoup
from tqdm import tqdm
import pymorphy2


class sjGenderFilter(GenderFilter):

    def __init__(self, desired_gender: str = "мужчина", file_name: str = "sj_RESULT.txt"):
        super().__init__(desired_gender, file_name)

    def run(self) -> None:
        print("SuperJob: Проверяем пол...")
        result_links = []
        morph = pymorphy2.MorphAnalyzer()  # Анализатор слов
        with open(self.file_name, 'r', encoding='utf-8') as file:
            progress = int(file.readline().strip())
            pbar = tqdm(total=progress)
            i = 0
            while i < progress:
                link = file.readline().strip()
                html = super()._get_html(link)
                soup = BeautifulSoup(html, 'lxml')
                gender_data = soup.find('span', class_="_3mfro _3EQE7 _2JVkc _2VHxz")

                if not gender_data:
                    result_links += [link]
                    continue

                # на sj пол не указан прямо, но можно посмотреть на род слова.
                for word in gender_data:
                    p = morph.parse(word)[0]
                    if p.tag.POS == 'ADJS':
                        if p.tag.gender == 'masc' and desired_gender == "мужчина":
                            result_links += [link]
                        elif p.tag.gender == 'femn' and desired_gender == "женщина":
                            result_links += [link]
                i += 1
                pbar.update()
            pbar.close()
        super()._write_result_links(self.file_name, result_links)
