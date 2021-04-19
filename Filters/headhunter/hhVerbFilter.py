# -*- coding: utf-8 -*-
from Filters.VerbFilter import VerbFilter
from bs4 import BeautifulSoup
from tqdm import tqdm
from re import sub
import pymorphy2


class hhVerbFilter(VerbFilter):
    def __init__(self, file_name: str = "hh_RESULT.txt", main: bool = True, about_myself: bool = True):
        super().__init__(file_name, main, about_myself)

    def run(self):
        if not (self.main or self.about_myself):
            return
        print("HeadHunter: Фильтр по глаголам...")
        result_links = []
        with open(self.file_name, 'r', encoding='utf-8') as file:  # Откуда берём сслыки на резюме
            progress = int(file.readline().strip())  # Сколько всего будет ссылок на резюме
            link_ind = 0  # Индекс читаемой ссылки
            pbar = tqdm(total=progress)  # Прогресс-бар
            morph = pymorphy2.MorphAnalyzer()  # Анализатор слов

            while link_ind < progress:  # По всем резюме
                link = file.readline().strip()  # Прочитали ссылку на резюме
                html = super()._get_html(link)
                soup = BeautifulSoup(html, 'lxml')
                job_dscrptn = ''
                if self.main:
                    job1_dscrptn = soup.find_all(
                        attrs={"data-qa": "resume-block-experience-description"})  # Про каждое место работы
                    if job1_dscrptn:
                        job_dscrptn += str(job1_dscrptn)
                if self.about_myself:
                    job2_dscrptn = soup.find(attrs={"data-qa": "resume-block-skills-content"})
                    if job2_dscrptn:
                        job_dscrptn += str(job2_dscrptn)
                if job_dscrptn == '':  # Если ничего не нашли, то переходим к следующему резюме
                    link_ind += 1
                    pbar.update()  # Обновляет прогресс-бар
                    continue

                job = ''.join(str(j) for j in job_dscrptn)  # Получаем текст
                job = sub("[^А-Яа-я ]", "", job)  # Оставляем только русские буквы и пробелы
                job = job.split()  # Дробим по пробелам и получаем list слов
                word_count = len(job)  # колличество слов
                bad_words = 0  # Плохие слова: глаголы и существительные
                bad_resume = False  # Резюме плохое?
                # Проходим по всем словам во всём резюме
                i = 0
                while i < word_count:
                    p = morph.parse(job[i])[0].tag  # Получаем информацию о слове
                    if not "VERB" in p and not "NOUN" in p:  # Если не глагол и не существительное то пропускаем
                        i += 1
                        continue
                    elif "VERB" in p and "past" in p:  # Если слово - глагол прошедшего времени, то это плохое слово
                        bad_words += 1
                    elif "NOUN" in p and "nomn" in p and "neut" in p:  # Если слово - сущ ед числа и среднего рода, то это плохое слово
                        bad_words += 1
                    # Если плохих слов слишком много (больше 20 %)
                    if bad_words/word_count > 0.2:
                        bad_resume = True  # то резюме плохое
                        break  # дальше нет смысла смотреть
                    i += 1
                if not bad_resume:  # Если хорошее резюме, то записываем его
                    result_links += [link]
                link_ind += 1
                pbar.update()
            pbar.close()
        super()._write_result_links(self.file_name, result_links)
