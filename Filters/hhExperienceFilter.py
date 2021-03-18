# -*- coding: utf-8 -*-

from .ParentFilter import *


class hhExperienceFilter(ParentFilter):
    def __init__(self, position: str, min_experience=24, procents=60, readfile_name="all_resumes.txt", writefile_name="exp_resumes.txt"):
        super().__init__(readfile_name, writefile_name)
        self.position = position
        self.min_experience = min_experience
        self.procents = procents

    def young_age(self, soup, age_limit: int):  # Возвращает False если человеку больше чем age_limit лет
        age = soup.find(attrs={"data-qa": "resume-personal-age"})
        if not age:
            return True
        return int(age.get_text().strip().split()[0]) < age_limit

    # Функция, которая парсит блок с опытом работы
    def parse_exp_in_resume(self, soup):
        # находим общий опыт работы
        all_exp = soup.find_all('div', class_="bloko-text-tertiary")
        total_exp_str = soup.find(
            'span', class_="resume-block__title-text resume-block__title-text_sub")
        if not total_exp_str:
            return False
        total_exp_str = total_exp_str.get_text()
        if "Опыт работы" not in total_exp_str:  # если человек вообще не работал
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
        while i < (len(cur_positions)):
            if self.position in cur_positions[i].get_text().lower():
                cur_exp_tuple = tuple(all_exp[i].get_text().split())
                if(len(cur_exp_tuple) == 4):
                    cur_exp = int(cur_exp_tuple[0])*12 + int(cur_exp_tuple[2])
                elif(cur_exp_tuple[1] == "год" or cur_exp_tuple[1] == "лет" or cur_exp_tuple[1] == "года"):
                    cur_exp = int(cur_exp_tuple[0])*12
                else:
                    cur_exp = int(cur_exp_tuple[0])
                # проверяем опыт
                if(cur_exp >= self.min_experience):
                    good_exp += cur_exp
            i += 1
        if(float(good_exp)/total_exp_value >= self.procents/100):
            return True
        else:
            return False

    def run(self):
        print("Проверяем опыт работы...")
        total = 0
        with open(self.readfile_name, 'r', encoding='utf-8') as read_file:
            with open(self.writefile_name, 'w', encoding='utf-8') as write_file:
                progress = int(read_file.readline().strip())
                pbar = tqdm(total=progress)
                i = 0
                while i < progress:
                    link = read_file.readline().strip()
                    try:
                        html = super().get_html(link)
                        soup = BeautifulSoup(html, 'lxml')
                    except (requests.exceptions.ReadTimeout, requests.exceptions.ConnectionError) as e:
                        print(" Переподключение к страничке с резюме...")
                        sleep(3)
                    if self.young_age(soup, 26):
                        write_file.write(link+'\n')
                        total += 1
                    else:
                        if(self.parse_exp_in_resume(soup)):  # !
                            write_file.write(link+'\n')
                            total += 1
                    i += 1
                    pbar.update()
                pbar.close()
        super().write_top(total)
        print("Найдено", total, "подходящих резюме.")
