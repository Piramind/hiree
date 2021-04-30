# -*- coding: utf-8 -*-
from Filters.ExperienceFilter import ExperienceFilter


class sjExperienceFilter(ExperienceFilter):
    def __init__(self, position: str, min_experience: int = 24, procents: int = 60, file_name: str = "sj_RESULT.txt"):
        super().__init__(position, min_experience, procents, file_name)

    def _young_age(self, soup, age_limit: int) -> bool:
        # Почему-то find ничего не возвращает, а find_all возвращает 1 элемент
        description = soup.find_all('meta', attrs={"name": "description"})
        if not description:
            return True
        description = description[0]["content"].split()
        age = int(description[description.index("Возраст:")+1])
        return age < age_limit

    def _parse_exp_in_resume(self, soup) -> bool:
        # находим общий опыт работы
        # .get_text().replace('\xa0', ' ')
        all_exp = [exp for exp in soup.find_all(
            'div', class_="_3mfro _9fXTd _2JVkc _2VHxz _3LJqf _15msI")[2::2]]
        total_exp_str = soup.find('h2', class_="_3mfro _3jlnz PlM3e _2JVkc _2VHxz")
        if not total_exp_str or not all_exp:
            return False
        total_exp_str = total_exp_str.get_text()
        if "Опыт работы" not in total_exp_str:  # если человек вообще не работал
            return False
        total_exp_tuple = tuple(total_exp_str.split())
        total_exp_value = 0  # Общий опыт работы в месяцах
        # Считам общий стаж
        if(len(total_exp_tuple) == 7):
            total_exp_value = int(total_exp_tuple[2])*12 + int(total_exp_tuple[5])
        elif(total_exp_tuple[3] in ("год", "года", "лет")):
            total_exp_value = int(total_exp_tuple[2])*12
        else:
            total_exp_value = int(total_exp_tuple[2])

        # Рассматриваем каждый опыт работы
        good_exp = 0
        cur_positions = soup.find_all('h3', class_="_3mfro _1ZlLP _2JVkc _2VHxz _3LJqf _15msI")
        i = 0
        while i < (len(cur_positions)):
            if self.position in cur_positions[i].get_text().lower():
                cur_exp_tuple = tuple(all_exp[i].get_text().split())
                if(len(cur_exp_tuple) == 5):
                    cur_exp = int(cur_exp_tuple[0])*12 + int(cur_exp_tuple[3])
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

    def run(self) -> None:
        print("SuperJob: Проверяем опыт работы...")
        super().run()
