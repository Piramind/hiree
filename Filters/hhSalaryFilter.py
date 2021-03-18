from .ParentFilter import *


class hhSalaryFilter(ParentFilter):
    def __init__(self, min_salary: int, max_salary: int, readfile_name="all_resumes.txt", writefile_name="salary_resumes.txt"):
        super().__init__(readfile_name, writefile_name)
        self.min_salary = min_salary
        self.max_salary = max_salary

    def run(self):
        print("Проверяем желаемую зарплату...")
        with open(self.readfile_name, 'r', encoding='utf-8') as read_file:
            with open(self.writefile_name, 'w', encoding='utf-8') as write_file:
                progress = int(read_file.readline().strip())
                link_ind = 0
                pbar = tqdm(total=progress)
                total = 0
                while link_ind < progress:
                    link = read_file.readline().strip()
                    try:
                        html = super().get_html(link[:len(link)-4])
                        soup = BeautifulSoup(html, 'lxml')
                    except (requests.exceptions.ReadTimeout, requests.exceptions.ConnectionError) as e:
                        print(" Переподключение к страничке с резюме...")
                        sleep(3)
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
                    money = re.sub("[0-9]", "", money)
                    money = money.replace('\u2009', '')
                    money = int(money)
                    if money > min_salary and money < max_salary:
                        write_file.write(link+'\n')
                        total += 1
                    link_ind += 1
                    pbar.update()
                pbar.close()
        super().write_top(total)
        print("Найденно", total, "подходящих резюме.")
