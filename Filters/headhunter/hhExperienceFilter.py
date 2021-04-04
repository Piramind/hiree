# -*- coding: utf-8 -*-
from Filters.ExperienceFilter import ExperienceFilter


class hhExperienceFilter(ExperienceFilter):
    def __init__(self, position: str, min_experience: int = 24, procents: int = 60, file_name: str = "hh_RESULT.txt",):
        super().__init__(position, min_experience, procents, file_name)

    def _young_age(self, soup, age_limit: int) -> bool:
        age = soup.find(attrs={"data-qa": "resume-personal-age"})
        if not age:
            return True
        return int(age.get_text().strip().split()[0]) < age_limit

    # Функция, которая парсит блок с опытом работы
    def _parse_exp_in_resume(self, soup) -> bool:
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
        elif(total_exp_tuple[3] in ("год", "года", "лет")):
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
                elif(cur_exp_tuple[1] in ("год", "года", "лет")):
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
