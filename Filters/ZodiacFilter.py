# -*- coding: utf-8 -*-

from .ParentFilter import *
from re import sub


class ZodiacFilter(ParentFilter):
    __metaclass__ = ABCMeta

    def __init__(self, desired_sign: str, readfile_name="all_resumes.txt", writefile_name="zodiac_resumes.txt"):
        super().__init__(readfile_name, writefile_name)
        self.desired_sign = desired_sign.lower()

    def get_zodiac(self, day_month: str):  # строка вида "день месяц" (20 января)
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

    # Запуск фильтра
    @abstractmethod
    def run(self) -> None:
        super().run()


class hhZodiacFilter(ZodiacFilter):

    def run(self):
        print("Проверяем знак зодиака...")
        total = 0
        with open(self.readfile_name, 'r', encoding='utf-8') as read_file:
            with open(self.writefile_name, 'w', encoding='utf-8') as write_file:
                progress = int(read_file.readline().strip())
                link_ind = 0
                pbar = tqdm(total=progress)
                while link_ind < progress:
                    link = read_file.readline().strip()
                    try:
                        html = super().get_html(link[:len(link)-4])
                        soup = BeautifulSoup(html, 'lxml')
                    except (exceptions.ReadTimeout, exceptions.ConnectionError, exceptions.ChunkedEncodingError) as e:
                        print(" Переподключение к страничке с резюме...")
                        sleep(3)

                    date_of_birth = soup.find(attrs={"data-qa": "resume-personal-birthday"})
                    if not date_of_birth:
                        link_ind += 1
                        pbar.update()
                        continue

                    date_of_birth = sub("[^А-Яа-я0-9] ", "", date_of_birth.get_text())
                    if self.desired_sign == self.get_zodiac(str(date_of_birth)[:len(date_of_birth)-5]):
                        write_file.write(link + '\n')
                        total += 1
                    link_ind += 1
                    pbar.update()
                pbar.close()
        super().write_top(total)
        print("Найденно", total, "подходящих резюме.")
