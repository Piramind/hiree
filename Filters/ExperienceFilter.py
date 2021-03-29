# -*- coding: utf-8 -*-

from .ParentFilter import *
# from abc import ABCMeta, abstractmethod


class ExperienceFilter(ParentFilter):
    __metaclass__ = ABCMeta

    def __init__(self, position: str, min_experience: int, procents: int, readfile_name: str, writefile_name: str):
        super().__init__(readfile_name, writefile_name)
        self.position = position.lower()
        self.min_experience = min_experience
        self.procents = procents

    # Возвращает False если человеку больше чем age_limit лет
    @abstractmethod
    def _young_age(self, soup, age_limit: int) -> bool:
        raise NotImplementedError

    # Функция, которая парсит блок с опытом работы
    @abstractmethod
    def _parse_exp_in_resume(self, soup) -> bool:
        raise NotImplementedError

    # Запуск фильтра
    def run(self) -> None:
        print("Проверяем опыт работы...")
        total = 0
        with open(self.readfile_name, 'r', encoding='utf-8') as read_file:
            with open(self.writefile_name, 'w', encoding='utf-8') as write_file:
                progress = int(read_file.readline().strip())
                pbar = tqdm(total=progress)
                i = 0
                while i < progress:
                    link = read_file.readline().strip()
                    html = super()._get_html(link)
                    soup = BeautifulSoup(html, 'lxml')
                    if self._young_age(soup, 26):
                        write_file.write(link+'\n')
                        total += 1
                    else:
                        if(self._parse_exp_in_resume(soup)):  # !
                            write_file.write(link+'\n')
                            total += 1
                    i += 1
                    pbar.update()
                pbar.close()
        super()._write_top(total)
        print("Найдено", total, "подходящих резюме.")


class hhExperienceFilter(ExperienceFilter):
    def __init__(self, position: str, min_experience: int = 24, procents: int = 60, readfile_name: str = "hh_res.txt", writefile_name: str = "hh_experience_res.txt"):
        super().__init__(position, min_experience, procents, readfile_name, writefile_name)

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


class superjobExperienceFilter(ExperienceFilter):
    def __init__(self, position: str, min_experience: int = 24, procents: int = 60, readfile_name: str = "superjob_res.txt",
                 writefile_name: str = "superjob_experience_res.txt"):
        super().__init__(position, min_experience, procents, readfile_name, writefile_name)

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
