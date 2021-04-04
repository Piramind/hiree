# -*- coding: utf-8 -*-
from .ParentFilter import *


class SalaryFilter(ParentFilter):
    __metaclass__ = ABCMeta

    def __init__(self, min_salary: int, max_salary: int, file_name: str):
        super().__init__(file_name)
        self.min_salary = min_salary
        self.max_salary = max_salary

    # Запуск фильтра
    @abstractmethod
    def run(self) -> None:
        super().run()
