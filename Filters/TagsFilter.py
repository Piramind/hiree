from .ParentFilter import *
from re import sub
import os
from openpyxl import load_workbook


class TagsFilter(ParentFilter):
    __metaclass__ = ABCMeta

    def __init__(self, readfile_name: str, writefile_name: str, wb_name: str):
        super().__init__(readfile_name, writefile_name)

        # wb_path = os.path.abspath(os.path.join(os.getcwd(), os.pardir)) + '/' + wb_name
        wb_path = os.getcwd() + '/' + wb_name
        wb = load_workbook(filename=wb_path, read_only=True)
        ws = wb["Лист2"]  # временный костыль

        self.keywords1 = self._get_keywords(ws['A2':'A100'])
        self.keywords2 = self._get_keywords(ws['B2':'B100'])
        self.keywords3 = self._get_keywords(ws['C2':'C100'])
        self.keywords4 = self._get_keywords(ws['D2':'D100'])
        self.keywords5 = self._get_keywords(ws['E2':'E100'])

    def _get_keywords(self, cell_range: tuple) -> tuple:
        keywords = ()
        for row in cell_range:
            for cell in row:
                cell_value = cell.value
                if not cell_value:
                    break
                keywords += (cell_value,)
        return keywords

    # Запуск фильтра
    @abstractmethod
    def run(self) -> None:
        super().run()


class hhTagsFilter(TagsFilter):
    def __init__(self, readfile_name="hh_res.txt", writefile_name="hh_tagged_res.txt", wb_name="tags.xlsx"):
        super().__init__(readfile_name, writefile_name, wb_name)

    def run(self):
        print("Проверяем теги...")

        data = dict()

        with open(self.readfile_name, 'r', encoding='utf-8') as read_file:
            progress = int(read_file.readline().strip())
            link_ind = 0
            pbar = tqdm(total=progress)
            while link_ind < progress:
                link = read_file.readline().strip()
                html = super()._get_html(link)
                soup = BeautifulSoup(html, 'lxml')

                job_dscrptn = soup.find_all(
                    attrs={"data-qa": "resume-block-experience-description"})
                if not job_dscrptn:
                    link_ind += 1
                    pbar.update()
                    continue

                job = "".join(j.get_text() for j in job_dscrptn)
                job = sub("[^А-Яа-я .]", "", job)

                total_value = 0.1*any(k5 in job for k5 in self.keywords5)

                job = job.split('.')
                i = 0
                while i < len(job):
                    j = job[i]
                    sentence_value = 1 * any(k1 in j for k1 in self.keywords1)
                    sentence_value += 1 * any(k2 in j for k2 in self.keywords2)
                    sentence_value += 1 * any(k3 in j for k3 in self.keywords3)
                    sentence_value += 1 * any(k4 in j for k4 in self.keywords4)
                    if sentence_value > 0:
                        total_value += sentence_value
                    i += 1
                if(total_value > 1):
                    data[link] = total_value
                link_ind += 1
                pbar.update()
        pbar.close()
        print("Найдено", len(data), "подходящих резюме.")
        with open(self.writefile_name, 'w', encoding='utf-8') as f:
            f.write(str(len(data)) + '\n')
            for k in sorted(data, key=data.get, reverse=True):
                f.write(k + ' ' + str(data[k]) + '\n')
