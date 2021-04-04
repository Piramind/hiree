# -*- coding: utf-8 -*-
from .ParentFilter import *

# Класс, который должен отсеивать шаблонные резюме. В шаблонных резюме много (сколько?) глаголов прошедшего времени совершенного вида и существительных в Им. падеже единственного числа.


class VerbFilter(ParentFilter):
    __metaclass__ = ABCMeta

    def __init__(self, file_name: str):
        super().__init__(file_name)

    # Запуск фильтра
    @abstractmethod
    def run(self) -> None:
        super().run()
