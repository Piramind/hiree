# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup
from time import sleep
import os
from tqdm import tqdm
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
    # url_base = 'https://hh.ru/search/resume?clusters=True'
    # url_area = '&area='+area
    # url_base2 = '&order_by=relevance&logic=normal&pos=position&exp_period=all_time&no_magic=False&st=resumeSearch'
    # url_text = '&text='+query
    # url_page = '&page='

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
def parse_exp_in_resume(soup, demanded_exp, procents, position):
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
    # print("Общий стаж:", total_exp, "месяцев")
    # cur_exp = 0  # Опыт на одном из мест
    # s *= 0
    # Рассматриваем каждый опыт работы
    good_exp = 0
    cur_positions = soup.find_all(attrs={"data-qa": "resume-block-experience-position"})
    i = 0
    while i < (len(cur_positions)):
        if position in cur_positions[i].get_text().lower():
            # exp = all_exp[i]
            # print(exp.get_text())
            # получаем время
            cur_exp_tuple = tuple(all_exp[i].get_text().split())
            if(len(cur_exp_tuple) == 4):
                cur_exp = float(cur_exp_tuple[0])*12 + float(cur_exp_tuple[2])
            elif(cur_exp_tuple[1] == "год" or cur_exp_tuple[1] == "лет" or cur_exp_tuple[1] == "года"):
                cur_exp = float(cur_exp_tuple[0])*12
            else:
                cur_exp = float(cur_exp_tuple[0])
            # проверяем опыт
            if(cur_exp >= demanded_exp):
                good_exp += cur_exp
        i += 1
    if(good_exp/total_exp_value >= procents/100):
        return True
    else:
        return False


def parse_resumes():
    print("Ищем подходящие резюме(фильтр по опыту)...")
    good_resumes = 0
    with open("all_resumes.txt", 'r', encoding='utf-8') as f:
        progress = int(f.readline().strip())
        pbar = tqdm(total=progress)
        i = 0
        all_links = ()
        while i < progress:
            link = f.readline().strip()
            try:
                html = get_html(link)
                soup = BeautifulSoup(html, 'lxml')
            except (requests.exceptions.ReadTimeout, requests.exceptions.ConnectionError) as e:
                print(" Переподключение к страничке с резюме...")
                sleep(3)
            if(parse_exp_in_resume(soup, 24, 60, "менеджер")):  # !
                all_links += (link,)
                good_resumes += 1
            i += 1
            pbar.update()
    pbar.close()
    with open("good_resumes.txt", 'w', encoding='utf-8') as f:
        f.write(str(good_resumes) + '\n')
        i = 0
        while i < good_resumes:
            f.write(all_links[i] + '\n')
            i += 1
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


def apply_tags():
    print("Проверяем теги первого и второго блока...")
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

    with open("good_resumes.txt", 'r', encoding='utf-8') as f:
        progress = int(f.readline())
        link_ind = 0
        pbar = tqdm(total=progress)
        while link_ind < progress:
            link = f.readline().strip()
            try:
                html = get_html(link)
                soup = BeautifulSoup(html, 'lxml')
            except (requests.exceptions.ReadTimeout, requests.exceptions.ConnectionError) as e:
                print(" Переподключение к страничке с резюме...")
                sleep(3)

            job_dscrptn = soup.find_all(attrs={"data-qa": "resume-block-experience-description"})
            job = "".join(str(j) for j in job_dscrptn)
            job = job.replace("</div>", "")
            job = job.replace("<div data-qa=\"resume-block-experience-description\">", "")
            job = job.replace(';', '.')

            total = 0.1*any(k21 in job for k21 in keywords21)

            job = job.split('.')
            max_sentence_value = 0.0
            i = 0
            while i < len(job):
                j = job[i]
                sentence_value = 1 * any(k11 in j for k11 in keywords11)
                sentence_value += 1 * any(k12 in j for k12 in keywords12)
                sentence_value += 1 * any(k13 in j for k13 in keywords13)
                if max_sentence_value < sentence_value:
                    max_sentence_value = sentence_value
                    if max_sentence_value == 3:
                        break
                i += 1
            total += max_sentence_value
            if(total > 0.1):
                data[link] = total
            link_ind += 1
            pbar.update()
    pbar.close()
    print("Найдено", len(data), "подходящих резюме.")
    with open("tagged_good_resumes.txt", 'w', encoding='utf-8') as f:
        for k in sorted(data, key=data.get, reverse=True):
            f.write(k + ' ' + str(data[k]) + '\n')


if __name__ == '__main__':
    # print("Введите запрос:")
    # query = input().lower().replace(' ', '+')
    query = "менеджер+по+продажам"
    area = '2'
    # # сначала вытащим все ссылки на резюме по данному запросу и региону
    # get_all_resumes(query, area, 500)
    # # теперь распарсим информацию по каждой ссылке, полученной выше
    # parse_resumes()  # по опыту работы
    apply_tags()
