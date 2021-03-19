# -*- coding: utf-8 -*-

from .ParentFilter import *


class GenderFilter(ParentFilter):
    __metaclass__ = ABCMeta

    def __init__(self, desired_gender: str, readfile_name="all_resumes.txt", writefile_name="gender_resumes.txt"):
        super().__init__(readfile_name, writefile_name)
        self.desired_gender = desired_gender.lower()

    # Запуск фильтра
    @abstractmethod
    def run(self) -> None:
        super().run()


class hhGenderFilter(GenderFilter):

    def run(self):
        print("Проверяем опыт пол (паркетный)...")
        total = 0
        with open(self.readfile_name, 'r', encoding='utf-8') as read_file:
            with open(self.writefile_name, 'w', encoding='utf-8') as write_file:
                progress = int(read_file.readline().strip())
                pbar = tqdm(total=progress)
                i = 0
                while i < progress:
                    link = read_file.readline().strip()
                    try:
                        html = super().get_html(link)
                        soup = BeautifulSoup(html, 'lxml')
                    except (exceptions.ReadTimeout, exceptions.ConnectionError, exceptions.ChunkedEncodingError) as e:
                        print(" Переподключение к страничке с резюме...")
                        sleep(3)
                    personal_gender = soup.find(attrs={"data-qa": "resume-personal-gender"})
                    if not personal_gender:
                        write_file.write(link+'\n')
                        total += 1
                        continue
                    if personal_gender.get_text().strip().lower() == self.desired_gender:
                        write_file.write(link+'\n')
                        total += 1
                    i += 1
                    pbar.update()
                pbar.close()
        super().write_top(total)
        print("Найдено", total, "подходящих резюме.")
