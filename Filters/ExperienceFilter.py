# -*- coding: utf-8 -*-
from .ParentFilter import *
from bs4 import BeautifulSoup
from tqdm import tqdm


class ExperienceFilter(ParentFilter):
    __metaclass__ = ABCMeta

    def __init__(self, position: str, min_experience: int, procents: int, file_name: str):
        super().__init__(file_name)
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
        total_links = 0
        result_links = []

        with open(self.file_name, 'r', encoding='utf-8') as file:
            progress = int(file.readline().strip())
            pbar = tqdm(total=progress)
            i = 0
            while i < progress:
                link = file.readline().strip()
                html = super()._get_html(link)
                soup = BeautifulSoup(html, 'lxml')
                if self._young_age(soup, 26):
                    result_links += [link]
                    total_links += 1
                else:
                    if(self._parse_exp_in_resume(soup)):  # cюда @lru_cahe ?
                        result_links += [link]
                        total_links += 1
                i += 1
                pbar.update()
            pbar.close()
        super()._write_result_links(self.file_name, result_links)
