from .ParentFilter import *


class MakeReport(ParentFilter):
    __metaclass__ = ABCMeta

    def __init__(self, file_name: str, wb_name: str):
        super().__init__(file_name)
        self.wb_name = wb_name

    # Запуск фильтра
    @abstractmethod
    def run(self) -> None:
        super().run()
