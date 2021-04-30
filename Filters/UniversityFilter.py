# -*- coding: utf-8 -*-

from .ParentFilter import *
from tqdm import tqdm
from bs4 import BeautifulSoup


class UniversityFilter(ParentFilter):
    __metaclass__ = ABCMeta

    def __init__(self, desired_university: str, file_name: str):
        super().__init__(file_name)
        self.desired_university = desired_university

    # Проверяет есть ли желаемый университет или высшее образование вообще
    @abstractmethod
    def _check_university(self, soup) -> bool:
        raise NotImplementedError

    # Запуск фильтра
    @abstractmethod
    def run(self) -> None:
        result_links = []
        with open(self.file_name, 'r', encoding='utf-8') as file:
            progress = int(file.readline().strip())
            link_ind = 0
            pbar = tqdm(total=progress)
            while link_ind < progress:
                link = file.readline().strip()
                html = super()._get_html(link[:len(link)-4])
                soup = BeautifulSoup(html, 'lxml')

                if self._check_university(soup, desired_university):
                    result_links += [link]
                    total_links += 1

                i += 1
                pbar.update()
            pbar.close()
        super()._write_result_links(self.file_name, result_links)
