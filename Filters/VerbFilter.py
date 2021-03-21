from .ParentFilter import *
import pymorphy2
from re import sub

# Класс, который должен отсеивать шаблонные резюме. В шаблонных резюме много (сколько?) глаголов прошедшего времени совершенного вида и существительных в Им. падеже единственного числа.


class VerbFilter(ParentFilter):
    __metaclass__ = ABCMeta

    def __init__(self, readfile_name: str, writefile_name: str):
        super().__init__(readfile_name, writefile_name)

    # Запуск фильтра
    @abstractmethod
    def run(self) -> None:
        super().run()


class hhVerbFilter(VerbFilter):
    def __init__(self, readfile_name="hh_res.txt", writefile_name="hh_verb_res.txt"):
        super().__init__(readfile_name, writefile_name)

    def run(self):
        print("Фильтр по глаголам...")
        with open(self.readfile_name, 'r', encoding='utf-8') as read_file:  # Откуда берём сслыки на резюме
            with open(self.writefile_name, 'w', encoding='utf-8') as write_file:  # Куда записываем
                progress = int(read_file.readline().strip())  # Сколько всего будет ссылок на резюме
                link_ind = 0  # Индекс читаемой ссылки
                pbar = tqdm(total=progress)  # Прогресс-бар
                morph = pymorphy2.MorphAnalyzer()  # Анализатор слов
                total = 0  # Сколько всего подходящих резюме отобралось

                while link_ind < progress:  # По всем резюме
                    link = read_file.readline().strip()  # Прочитали ссылку на резюме
                    html = super()._get_html(link)
                    soup = BeautifulSoup(html, 'lxml')
                    job_dscrptn = soup.find_all(
                        attrs={"data-qa": "resume-block-experience-description"})  # Про каждое место работы
                    if not job_dscrptn:  # Если ничего не нашли, то переходим к следующему резюме
                        link_ind += 1
                        pbar.update()  # Обновляет прогресс-бар
                        continue

                    job = "".join(j.get_text() for j in job_dscrptn)  # Получаем текст
                    job = sub("[^А-Яа-я ]", "", job)  # Оставляем только русские буквы и пробелы
                    job = job.split()  # Дробим по пробелам и получаем list слов
                    word_count = len(job)  # колличество слов
                    bad_words = 0  # Плохие слова: глаголы и существительные
                    bad_resume = False  # Резюме плохое?
                    # Проходим по всем словам во всём резюме
                    i = 0
                    while i < word_count:
                        p = morph.parse(job[i])[0].tag  # Получаем информацию о слове
                        if not "VERB" in p and not "NOUN" in p:  # Если не глагол и не существительное то пропускаем
                            i += 1
                            continue
                        elif "VERB" in p and "past" in p:  # Если слово - глагол прошедшего времени, то это плохое слово
                            bad_words += 1
                        elif "NOUN" in p and "nomn" in p and "neut" in p:  # Если слово - сущ ед числа и среднего рода, то это плохое слово
                            bad_words += 1
                        # Если плохих слов слишком много (больше 20 %)
                        if bad_words/word_count > 0.2:
                            bad_resume = True  # то резюме плохое
                            break  # дальше нет смысла смотреть
                        i += 1
                    if not bad_resume:  # Если хорошее резюме, то записываем его
                        write_file.write(link+'\n')
                        total += 1
                    link_ind += 1
                    pbar.update()
                pbar.close()
        super()._write_top(total)
        print("Найденно", total, "подходящих резюме.")
