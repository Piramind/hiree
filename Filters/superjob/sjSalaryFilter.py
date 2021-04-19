# -*- coding: utf-8 -*-
from Filters.SalaryFilter import SalaryFilter
from bs4 import BeautifulSoup
from tqdm import tqdm
from re import sub


class sjSalaryFilter(SalaryFilter):

    def __init__(self, min_salary: int = 60000, max_salary: int = 200000, file_name: str = "sj_RESULT.txt"):
        super().__init__(min_salary, max_salary, file_name)

    def run(self) -> None:
        print("SuperJob: Проверяем желаемую зарплату...")
        result_links = []

        with open(self.file_name, 'r', encoding='utf-8') as file:
            progress = int(file.readline().strip())
            link_ind = 0
            pbar = tqdm(total=progress)
            while link_ind < progress:
                link = file.readline().strip()
                html = super()._get_html(link[:len(link)-4])
                soup = BeautifulSoup(html, 'lxml')
                money = soup.find('span', class_="_3mfro PlM3e _2JVkc _2VHxz")
                if not money:
                    result_links += [link]
                    link_ind += 1
                    pbar.update()
                    continue
                money = str(money)
                if not "руб." in money:
                    result_links += [link]
                    link_ind += 1
                    pbar.update()
                    continue
                money = sub("[^0-9]", "", money)
                if money == "":
                    result_links += [link]
                    link_ind += 1
                    pbar.update()
                    continue
                money = int(money)
                if self.min_salary < money and money < self.max_salary:
                    result_links += [link]
                link_ind += 1
                pbar.update()
            pbar.close()
        super()._write_result_links(self.file_name, result_links)
