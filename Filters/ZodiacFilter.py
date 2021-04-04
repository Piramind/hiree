# -*- coding: utf-8 -*-
from .ParentFilter import *


class ZodiacFilter(ParentFilter):
    __metaclass__ = ABCMeta

    def __init__(self, desired_sign: str, file_name: str):
        super().__init__(file_name)
        self.desired_sign = desired_sign.lower()

    def _get_zodiac(self, day_month: str):  # строка вида "день месяц" (20 января)
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
