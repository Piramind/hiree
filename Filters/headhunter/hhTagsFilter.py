# -*- coding: utf-8 -*-
from Filters.TagsFilter import TagsFilter
from bs4 import BeautifulSoup
from tqdm import tqdm
from re import sub


class hhTagsFilter(TagsFilter):
    def __init__(self, file_name: str = "hh_RESULT.txt", wb_name: str = "tags.xlsx", main: bool = True, about_myself: bool = True):
        super().__init__(file_name, wb_name, main, about_myself)

    def run(self) -> None:
        print("HeadHunter: Проверяем теги...")
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
                        attrs={"data-qa": "resume-block-experience-description"})
                    if job1_dscrptn is not None:
                        job_dscrptn += str(job1_dscrptn)

                if self.about_myself:
                    job2_dscrptn = soup.find(attrs={"data-qa": "resume-block-skills-content"})
                    if job2_dscrptn is not None:
                        job_dscrptn += str(job2_dscrptn)

                if job_dscrptn == '':
                    link_ind += 1
                    pbar.update()
                    continue

                # Склеиваем всё в одно
                job = "".join(str(j) for j in job_dscrptn)
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
                f.write(k + '\n')  # + ' ' + str(data[k])
        print("Найдено", len(data), "подходящих резюме.")
