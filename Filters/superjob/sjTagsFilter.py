# -*- coding: utf-8 -*-
from Filters.TagsFilter import TagsFilter
from bs4 import BeautifulSoup
from tqdm import tqdm
from re import sub


class sjTagsFilter(TagsFilter):
    def __init__(self, file_name: str = "sj_RESULT.txt", wb_name: str = "tags.xlsx", main: bool = True, about_myself: bool = False):
        super().__init__(file_name, wb_name, main, about_myself)

    def run(self) -> None:
        print("SuperJob: Проверяем теги...")
        if not self.main and not self.about_myself:
            return

        data = dict()

        with open(self.file_name, 'r', encoding='utf-8') as file:
            progress = int(file.readline().strip())
            link_ind = 0
            pbar = tqdm(total=progress)
            while link_ind < progress:
                link = file.readline().strip()
                html = super()._get_html(link)
                soup = BeautifulSoup(html, 'lxml')
                job_dscrptn = ''
                if self.main:
                    job1_dscrptn = soup.find_all(
                        'div', class_="_3mfro _2VtGa _1hP6a _2JVkc _2VHxz _3LJqf _15msI")
                    if job1_dscrptn:
                        job_dscrptn += job1_dscrptn
                # if self.about_myself:
                    # div class="_2g1F-"><div class="_3mfro _2VtGa _1hP6a _2JVkc _2VHxz _3LJqf _15msI
                if job_dscrptn == '':
                    link_ind += 1
                    pbar.update()
                    continue

                # Склеиваем всё в одно
                job = "".join(j.get_text() for j in job_dscrptn)
                job = sub("[^А-Яа-я .]", "", job)
                # print(job)

                total_value = 0.1*any(k5 in job for k5 in self.keywords5)

                job = job.split('.')
                i = 0
                while i < len(job):
                    j = job[i]
                    sentence_value = 1 * any(k1 in j for k1 in self.keywords1)
                    sentence_value += 1 * any(k2 in j for k2 in self.keywords2)
                    sentence_value += 1 * any(k3 in j for k3 in self.keywords3)
                    sentence_value += 1 * any(k4 in j for k4 in self.keywords4)
                    if sentence_value > 0:
                        total_value += sentence_value
                    i += 1
                if(total_value > 1):
                    data[link] = total_value
                link_ind += 1
                pbar.update()
        pbar.close()

        open(self.file_name, 'w', encoding='utf-8').close()
        with open(self.file_name, 'w', encoding='utf-8') as f:
            f.write(str(len(data)) + '\n')
            for k in sorted(data, key=data.get, reverse=True):
                f.write(k + ' ' + str(data[k]) + '\n')
        print("Найдено", len(data), "подходящих резюме.")
