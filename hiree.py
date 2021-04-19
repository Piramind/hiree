# -*- coding: utf-8 -*-
from Filters.ParentFilter import ParentFilter
# Фильтры HeadHunter
from Filters.headhunter.hhResumeCollector import hhResumeCollector
from Filters.headhunter.hhSalaryFilter import hhSalaryFilter
from Filters.headhunter.hhGenderFilter import hhGenderFilter
from Filters.headhunter.hhZodiacFilter import hhZodiacFilter
from Filters.headhunter.hhExperienceFilter import hhExperienceFilter
from Filters.headhunter.hhVerbFilter import hhVerbFilter
from Filters.headhunter.hhTagsFilter import hhTagsFilter
# Фильтры SuperJob
from Filters.superjob.sjResumeCollector import sjResumeCollector
from Filters.superjob.sjExperienceFilter import sjExperienceFilter
from Filters.superjob.sjSalaryFilter import sjSalaryFilter
from Filters.superjob.sjGenderFilter import sjGenderFilter
from Filters.superjob.sjZodiacFilter import sjZodiacFilter
from Filters.superjob.sjVerbFilter import sjVerbFilter
from Filters.superjob.sjTagsFilter import sjTagsFilter
#
import os


'''
def sort_relevant_jobs(keyword):  # сортирует резюме по кол-ву релевантных мест работы
    with open("good_resumes.txt", 'r', encoding='utf-8') as f:
        data = dict()
        for link in f:
            html = get_html(link)
            soup = BeautifulSoup(html, 'lxml')
            jobs = soup.find_all(attrs={"data-qa": "resume-block-experience-position"})
            ans = 0
            for job in jobs:
                if(keyword in job.get_text().lower()):
                    ans += 1
            data[link] = ans
    # open("good_resumes.txt", "w").close()
    with open("sorted_good_resumes.txt", 'w', encoding='utf-8') as f:
        for k in sorted(data, key=data.get, reverse=True):
            f.write(k + ' ' + str(data[k]) + '\n')
'''


class HireeApp:
    def __init__(self, resultfile_name: str = "RESULT.txt"):
        self.Filters = []
        self.resultfile_name = resultfile_name
        # потом надо переделать чтобы фильтры работали с одним файлом RESULT.txt

    def add_filter(self, new_filter: ParentFilter) -> None:
        if isinstance(new_filter, ParentFilter):
            self.Filters += [new_filter]

    def add_filters(self, new_filters: tuple) -> None:
        for new_filter in new_filters:
            self.add_filter(new_filter)

    def del_filters(self) -> None:
        self.Filters = []

    def execute(self) -> None:
        for filter in self.Filters:
            filter.run()


if __name__ == '__main__':

    my_hiree = HireeApp()

    hhFilters = [hhResumeCollector("Менеджер по продажам", 1000),
                 hhSalaryFilter(),
                 hhGenderFilter("мужчина"),
                 hhZodiacFilter("овен"),
                 hhExperienceFilter("Менеджер по продажам"),
                 hhVerbFilter(),
                 hhTagsFilter()]

    sjFilters = [sjResumeCollector("Менеджер по продажам", 1000),
                 sjSalaryFilter(),
                 sjGenderFilter("мужчина"),
                 sjExperienceFilter("Менеджер по продажам"),
                 sjVerbFilter(),
                 sjTagsFilter()]
    '''
    ВАЖНО! Python не разрешает делать импорт из папок, находящихся вместе в одной директории. Это можно решить, но пока это не особо будет мешать тк все агрегаторы тестятся отдельно. Если решить эту проблему, то можно будет разные фильтры хранить в общем tuple.
    Вот решение: https://stackoverflow.com/questions/6323860/sibling-package-imports
    '''

    my_hiree.add_filters(hhFilters)
    my_hiree.add_filters(sjFilters)
    try:
        my_hiree.execute()
    except KeyboardInterrupt as e:
        os._exit(1)
