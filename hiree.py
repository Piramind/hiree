# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup
from time import sleep
import os
from tqdm import tqdm
import subprocess
import re
import pymorphy2
# достает html код по указанной ссылке

local_proc = 0


def get_html(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
    html = ""
    try:
        html = requests.get(url, headers=headers).text
    except (requests.exceptions.ReadTimeout, requests.exceptions.ConnectionError) as e:
        print("Обработка исключения в get_html()...")
        sleep(3)
    return html


# проверяет, есть ли на странице(глобальной) ссылки на вакансии
def is_empty(html):
    soup = BeautifulSoup(html, 'lxml')
    links = soup.find_all('resume-serp_block-result-action')
    if links == []:
        return True
    else:
        return False

# функция, которая собирает все ссылки на вакансии на странице поиска
# принимает список, который уже может быть не пустой, возвращает дополненный список


def get_resumes_links(html):
    # новый объект класса BeutifulSoup
    soup = BeautifulSoup(html, 'lxml')
    new_links = ()
    links = soup.find_all('a', class_='resume-search-item__name')
    i = 0
    while i < len(links):
        new_links += ("".join(tuple(("http://hh.ru", links[i].get('href')))),)
        i += 1
    return new_links

# функция, которая для данного запроса и региона ищет все страницы с результатами поиска и набирает большой список со всеми ссылками на вакансии
# возвращает список ссылок по запросу query в регионе с кодом area


def get_all_resumes(query, area, number_of_links):
    print("Собираем глобальные ссылки...")
    # headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
    # https://hh.ru/search/resume?clusters=True&area=1&order_by=relevance&logic=normal&pos=position&exp_period=all_time&no_magic=False&st=resumeSearch&text=менеджер+по+продажам&page=0
    basic_url = "".join(tuple(("https://hh.ru/search/resume?clusters=True", "&area=", area,
                               "&order_by=relevance&logic=normal&pos=position&exp_period=all_time&no_magic=False&st=resumeSearch", "&text=", query, "&page=")))
    # когда не найдем с помощью bs4 нужный элемент, то выставим его False
    # нужен для остановки цикла перебора всех страниц
    # page_is_not_empty = True

    all_links = ()
    # page = 1

    i = 0
    pbar = tqdm(total=number_of_links//20)
    while i < number_of_links//20:
        url = basic_url+str(i)  # "".join(tuple((basic_url, str(i))))
        try:
            html = get_html(url)
        except (requests.exceptions.ReadTimeout, requests.exceptions.ConnectionError) as e:
            print(" Переподключение к глобальной странице...")
            sleep(3)
        all_links += get_resumes_links(html)
        i += 1
        pbar.update()
        '''
        if not is_empty(html):
            all_links = get_resumes_links(html, all_links)

            page += 1
        else:
            page_is_not_empty = False
        '''
    pbar.close()
    print("Проверено", len(all_links), "вакансий.")
    with open("all_resumes.txt", 'w', encoding='utf-8') as f:
        f.write(str(len(all_links)) + '\n')
        i = 0
        while i < len(all_links):
            f.write(all_links[i] + '\n')
            i += 1


# Функция, которая парсит блок с опытом работы
def parse_exp_in_resume(soup, demanded_exp: int, procents: int, position):
    # находим общий опыт работы
    all_exp = soup.find_all('div', class_="bloko-text-tertiary")
    total_exp_str = soup.find(
        'span', class_="resume-block__title-text resume-block__title-text_sub")
    if total_exp_str == None:
        return False
    total_exp_str = total_exp_str.get_text()
    if "Опыт работы" not in total_exp_str:  # если человек вообще не работал
        # print("=========")
        return False
    total_exp_tuple = tuple(total_exp_str.split())
    total_exp_value = 0  # Общий опыт работы в месяцах
    # Считам общий стаж
    if(len(total_exp_tuple) == 6):
        total_exp_value = int(total_exp_tuple[2])*12 + int(total_exp_tuple[4])
    elif(total_exp_tuple[3] == "год" or total_exp_tuple[3] == "лет" or total_exp_tuple[3] == "года"):
        total_exp_value = int(total_exp_tuple[2])*12
    else:
        total_exp_value = int(total_exp_tuple[2])

    # Рассматриваем каждый опыт работы
    good_exp = 0
    cur_positions = soup.find_all(attrs={"data-qa": "resume-block-experience-position"})
    i = 0
    # os.system("g++ exp.cpp -o exp")
    while i < (len(cur_positions)):
        # os.system("./exp " + position + " " +
        #           cur_positions[i].get_text().lower().partition(' ')[0] + " " +
        #           '+'.join(all_exp[i].get_text().split()))
        if position in cur_positions[i].get_text().lower():
            cur_exp_tuple = tuple(all_exp[i].get_text().split())
            if(len(cur_exp_tuple) == 4):
                cur_exp = int(cur_exp_tuple[0])*12 + int(cur_exp_tuple[2])
            elif(cur_exp_tuple[1] == "год" or cur_exp_tuple[1] == "лет" or cur_exp_tuple[1] == "года"):
                cur_exp = int(cur_exp_tuple[0])*12
            else:
                cur_exp = int(cur_exp_tuple[0])
            # проверяем опыт
            if(cur_exp >= demanded_exp):
                good_exp += cur_exp
        i += 1
    if(float(good_exp)/total_exp_value >= procents/100):
        return True
    else:
        return False


def demanded_sex(soup, sex: str):
    personal_sex = soup.find(attrs={"data-qa": "resume-personal-gender"})
    if personal_sex == None:
        return True
    return personal_sex.get_text().strip().lower() == sex


def young_age(soup, age_limit: int):
    age = soup.find(attrs={"data-qa": "resume-personal-age"})
    if age == None:
        return True
    return int(age.get_text().strip().split()[0]) < age_limit


def sexperience_filter():
    print("Проверяем опыт работы...")
    good_resumes = 0
    with open("all_resumes.txt", 'r', encoding='utf-8') as read_file:
        with open("good_resumes.txt", 'w', encoding='utf-8') as write_file:
            progress = int(read_file.readline().strip())
            pbar = tqdm(total=progress)
            i = 0
            while i < progress:
                link = read_file.readline().strip()
                try:
                    html = get_html(link)
                    soup = BeautifulSoup(html, 'lxml')
                except (requests.exceptions.ReadTimeout, requests.exceptions.ConnectionError) as e:
                    print(" Переподключение к страничке с резюме...")
                    sleep(3)
                if not demanded_sex(soup, "мужчина"):
                    i += 1
                    pbar.update()
                    continue
                if young_age(soup, 26):
                    write_file.write(link+'\n')
                    good_resumes += 1
                else:
                    if(parse_exp_in_resume(soup, 24, 60, "менеджер")):  # !
                        write_file.write(link+'\n')
                        good_resumes += 1
                i += 1
                pbar.update()
    f = open("good_resumes.txt", "r")
    oline = f.readlines()
    oline.insert(0, str(good_resumes)+'\n')
    f.close()
    f = open("good_resumes.txt", "w")
    f.writelines(oline)
    f.close()
    pbar.close()
    print("Найдено", good_resumes, "подходящих резюме.")


'''
def sort_relevant_jobs(keyword):  # сортирует резюме по кол-ву релевантных мест работы
    with open("good_resumes.txt", 'r', encoding='utf-8') as f:
        data = dict()
        for link in f:
            html = get_html(link)
            soup = BeautifulSoup(html, 'lxml')
            jobs = soup.find_all(attrs={"data-qa": "resume-block-experience-position"})
            ans = 0
            for job in jobs:
                if(keyword in job.get_text().lower()):
                    ans += 1
            data[link] = ans
    # open("good_resumes.txt", "w").close()
    with open("sorted_good_resumes.txt", 'w', encoding='utf-8') as f:
        for k in sorted(data, key=data.get, reverse=True):
            f.write(k + ' ' + str(data[k]) + '\n')
'''


def get_zodiac(day_month: str):  # строка вида "день месяц" (20 января)
    day, month = int(day_month.split()[0]), day_month.split()[1]
    astro_sign = ""
    if month == "декабря":
        astro_sign = "стрелец" if (day < 22) else "козерог"

    elif month == "января":
        astro_sign = "козерог" if (day < 20) else "водолей"

    elif month == "февраля":
        astro_sign = "водолей" if (day < 19) else "рыба"

    elif month == "марта":
        astro_sign = "рыба" if (day < 21) else "овен"

    elif month == "апреля":
        astro_sign = "овен" if (day < 20) else "телец"

    elif month == "мая":
        astro_sign = "телец" if (day < 21) else "близнецы"

    elif month == "июня":
        astro_sign = "близнецы" if (day < 21) else "рак"

    elif month == "июля":
        astro_sign = "рак" if (day < 23) else "лев"

    elif month == "августа":
        astro_sign = "лев" if (day < 23) else "дева"

    elif month == "сентября":
        astro_sign = "дева" if (day < 23) else "весы"

    elif month == "октября":
        astro_sign = "весы" if (day < 23) else "скорпион"

    elif month == "ноября":
        astro_sign = "скорпион" if (day < 22) else "стрелец"

    return astro_sign


def zodiac_filter(desired_sign: str):
    print("Проверяем знак зодиака...")
    # data = ()
    total = 0
    with open("good_resumes.txt", 'r', encoding='utf-8') as read_file:
        with open("zodiac_resumes.txt", 'w', encoding='utf-8') as write_file:
            progress = int(read_file.readline().strip())
            link_ind = 0
            pbar = tqdm(total=progress)
            while link_ind < progress:
                link = read_file.readline().strip()
                try:
                    html = get_html(link[:len(link)-4])
                    soup = BeautifulSoup(html, 'lxml')
                except (requests.exceptions.ReadTimeout, requests.exceptions.ConnectionError) as e:
                    print(" Переподключение к страничке с резюме...")
                    sleep(3)
                date_of_birth = soup.find(attrs={"data-qa": "resume-personal-birthday"})
                if date_of_birth == None:
                    link_ind += 1
                    pbar.update()
                    continue
                date_of_birth = str(date_of_birth).replace("</span>", "")
                date_of_birth = date_of_birth.replace(
                    "<span data-qa=\"resume-personal-birthday\">", "")
                if desired_sign == get_zodiac(str(date_of_birth)[:len(date_of_birth)-5]):
                    write_file.write(link + '\n')
                    total += 1
                link_ind += 1
                pbar.update()
    pbar.close()
    f = open("zodiac_resumes.txt", "r")
    oline = f.readlines()
    oline.insert(0, str(total)+'\n')
    f.close()
    f = open("zodiac_resumes.txt", "w")
    f.writelines(oline)
    f.close()
    print("Найденно", total, "подходящих резюме.")


def salary_filter(min_salary: int, max_salary: int):
    print("Проверяем желаемую зарплату...")
    with open("zodiac_resumes.txt", 'r', encoding='utf-8') as read_file:
        with open("salary_resumes.txt", 'w', encoding='utf-8') as write_file:
            progress = int(read_file.readline().strip())
            link_ind = 0
            pbar = tqdm(total=progress)
            total = 0
            while link_ind < progress:
                link = read_file.readline().strip()
                try:
                    html = get_html(link[:len(link)-4])
                    soup = BeautifulSoup(html, 'lxml')
                except (requests.exceptions.ReadTimeout, requests.exceptions.ConnectionError) as e:
                    print(" Переподключение к страничке с резюме...")
                    sleep(3)
                mny = soup.find(
                    'span', class_="resume-block__salary resume-block__title-text_salary")
                if mny == None:
                    write_file.write(link+'\n')
                    total += 1
                    link_ind += 1
                    pbar.update()
                    continue
                mny = str(mny)
                if not "руб." in mny:
                    write_file.write(link+'\n')
                    total += 1
                    link_ind += 1
                    pbar.update()
                    continue
                shit = "<span class=\"resume-block__salary resume-block__title-text_salary\" data-qa=\"resume-block-salary\">"
                mny = mny.replace(shit, '')
                mny = mny.replace("<!-- --> <!-- -->руб.</span>", '')
                mny = mny.replace('\u2009', '')
                mny = int(mny)
                if mny > min_salary and mny < max_salary:
                    write_file.write(link+'\n')
                link_ind += 1
                pbar.update()
    pbar.close()
    f = open("salary_resumes.txt", "r")
    oline = f.readlines()
    oline.insert(0, str(total)+'\n')
    f.close()
    f = open("salary_resumes.txt", "w")
    f.writelines(oline)
    f.close()
    print("Найденно", total, "подходящих резюме.")


def apply_tags():
    print("Проверяем теги...")
    keywords11, keywords12, keywords13, keywords21 = [], [], [], []

    with open("1-1_condition.txt", 'r', encoding='utf-8') as f:
        keywords11 = [word.strip() for word in f]

    with open("1-2_condition.txt", 'r', encoding='utf-8') as f:
        keywords12 = [word.strip() for word in f]

    with open("1-3_condition.txt", 'r', encoding='utf-8') as f:
        keywords13 = [word.strip() for word in f]

    with open("2-1_condition.txt", 'r', encoding='utf-8') as f:
        keywords21 = [word.strip() for word in f]

    data = dict()

    with open("salary_resumes.txt", 'r', encoding='utf-8') as read_file:
        progress = int(read_file.readline().strip())
        link_ind = 0
        pbar = tqdm(total=progress)
        while link_ind < progress:
            link = read_file.readline().strip()
            try:
                html = get_html(link)
                soup = BeautifulSoup(html, 'lxml')
            except (requests.exceptions.ReadTimeout, requests.exceptions.ConnectionError) as e:
                print(" Переподключение к страничке с резюме...")
                sleep(3)

            job_dscrptn = soup.find_all(attrs={"data-qa": "resume-block-experience-description"})
            if not job_dscrptn:
                link_ind += 1
                pbar.update()
                continue
            job = "".join(str(j) for j in job_dscrptn)
            job = job.replace("</div>", "")
            job = job.replace("<div data-qa=\"resume-block-experience-description\">", "")
            job = job.replace(';', '')
            job = job.replace('-', '')

            total_value = 0.1*any(k21 in job for k21 in keywords21)

            job = job.split('.')
            i = 0
            while i < len(job):
                j = job[i]
                sentence_value = 1 * any(k11 in j for k11 in keywords11)
                sentence_value += 1 * any(k12 in j for k12 in keywords12)
                sentence_value += 1 * any(k13 in j for k13 in keywords13)
                if sentence_value > 0:
                    total_value += sentence_value
                i += 1
            if(total_value > 1):
                data[link] = total_value
            link_ind += 1
            pbar.update()
    pbar.close()
    print("Найдено", len(data), "подходящих резюме.")
    with open("tagged_good_resumes.txt", 'w', encoding='utf-8') as f:
        f.write(str(len(data)) + '\n')
        for k in sorted(data, key=data.get, reverse=True):
            f.write(k + ' ' + str(data[k]) + '\n')


def verb_filter():
    with open("salary_resumes.txt", 'r', encoding='utf-8') as read_file:
        with open("verb_resumes.txt", 'w', encoding='utf-8') as write_file:
            progress = int(read_file.readline().strip())
            link_ind = 0
            pbar = tqdm(total=progress)
            morph = pymorphy2.MorphAnalyzer()
            total = 0
            while link_ind < progress:
                link = read_file.readline().strip()
                try:
                    html = get_html(link)
                    soup = BeautifulSoup(html, 'lxml')
                except (requests.exceptions.ReadTimeout, requests.exceptions.ConnectionError) as e:
                    print(" Переподключение к страничке с резюме...")
                    sleep(3)
                job_dscrptn = soup.find_all(
                    attrs={"data-qa": "resume-block-experience-description"})
                if not job_dscrptn:
                    link_ind += 1
                    pbar.update()
                    continue
                job = "".join(str(j) for j in job_dscrptn)
                job = re.sub("[^А-Яа-я ]", "", job)
                job = job.strip().split()
                word_count = len(job)
                bad_words = 0
                bad_resume = False
                i = 0
                while i < word_count:
                    p = morph.parse(job[i])[0].tag
                    if not "VERB" in p and not "NOUN" in p:
                        i += 1
                        continue
                    elif "VERB" in p and "past" in p:
                        bad_words += 1
                    elif "NOUN" in p and "nomn" in p and "neut" in p:
                        bad_words += 1
                    if bad_words/word_count > 0.2:  # !!
                        bad_resume = True
                        break
                    i += 1
                # print(bad_words/word_count)
                if not bad_resume:
                    write_file.write(link+'\n')
                    total += 1
                link_ind += 1
                pbar.update()
    pbar.close()
    f = open("verb_resumes.txt", "r")
    oline = f.readlines()
    oline.insert(0, str(total)+'\n')
    f.close()
    f = open("verb_resumes.txt", "w")
    f.writelines(oline)
    f.close()
    print("Найденно", total, "подходящих резюме.")


if __name__ == '__main__':
    # print("Введите запрос:")
    # query = input().lower().replace(' ', '+')
    query = "менеджер+по+продажам"
    area = '2'  # СПБ
    # сначала вытащим все ссылки на резюме по данному запросу и региону
    get_all_resumes(query, area, 1000)
    теперь распарсим информацию по каждой ссылке, полученной выше
    sexperience_filter()  # по опыту работы и полу
    zodiac_filter("овен")
    salary_filter(60000, 250000)
    # verb_filter() # теститься (нужно правильное число на 460 строку)
    apply_tags()  # тэги
