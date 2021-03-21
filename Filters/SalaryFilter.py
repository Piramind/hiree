from .ParentFilter import *
from re import sub


class SalaryFilter(ParentFilter):
    __metaclass__ = ABCMeta

    def __init__(self, min_salary: int, max_salary: int, readfile_name: str, writefile_name: str):
        super().__init__(readfile_name, writefile_name)
        self.min_salary = min_salary
        self.max_salary = max_salary

    # Запуск фильтра
    @abstractmethod
    def run(self) -> None:
        super().run()


class hhSalaryFilter(SalaryFilter):

    def __init__(self, min_salary, max_salary, readfile_name="hh_res.txt", writefile_name="hh_salary_res.txt"):
        super().__init__(min_salary, max_salary, readfile_name, writefile_name)

    def run(self) -> None:
        print("Проверяем желаемую зарплату...")
        with open(self.readfile_name, 'r', encoding='utf-8') as read_file:
            with open(self.writefile_name, 'w', encoding='utf-8') as write_file:
                progress = int(read_file.readline().strip())
                link_ind = 0
                pbar = tqdm(total=progress)
                total = 0
                while link_ind < progress:
                    link = read_file.readline().strip()
                    html = super()._get_html(link[:len(link)-4])
                    soup = BeautifulSoup(html, 'lxml')
                    money = soup.find(
                        'span', class_="resume-block__salary resume-block__title-text_salary")
                    if not money:
                        write_file.write(link+'\n')
                        total += 1
                        link_ind += 1
                        pbar.update()
                        continue
                    money = str(money)
                    if not "руб." in money:
                        write_file.write(link+'\n')
                        total += 1
                        link_ind += 1
                        pbar.update()
                        continue
                    money = sub("[^0-9]", "", money)
                    # money = money.replace('\u2009', '')
                    if money == "":
                        write_file.write(link+'\n')
                        total += 1
                        link_ind += 1
                        pbar.update()
                        continue
                    money = int(money)
                    if self.min_salary < money and money < self.max_salary:
                        write_file.write(link+'\n')
                        total += 1
                    link_ind += 1
                    pbar.update()
                pbar.close()
        super()._write_top(total)
        print("Найденно", total, "подходящих резюме.")
