# -*- coding: utf-8 -*-
from .ParentFilter import *


class GenderFilter(ParentFilter):
    __metaclass__ = ABCMeta

    def __init__(self, desired_gender: str, file_name: str):
        super().__init__(file_name)
        self.desired_gender = desired_gender.lower()

    # Запуск фильтра
    @abstractmethod
    def run(self) -> None:
        super().run()
