# -*- coding: utf-8 -*-

from Filters.ParentFilter import ParentFilter
from Filters.ResumeColector import hhResumeColector
from Filters.ExperienceFilter import hhExperienceFilter
from Filters.ZodiacFilter import hhZodiacFilter
from Filters.GenderFilter import hhGenderFilter
from Filters.SalaryFilter import hhSalaryFilter
from Filters.VerbFilter import hhVerbFilter
from Filters.TagsFilter import hhTagsFilter
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


class hireeApp():
    def __init__(self, resultfile_name: str = "RESULT.txt"):
        self.Filters = []
        self.resultfile_name = resultfile_name
        # потом надо переделать чтобы фильтр работали с одним файлом RESULT.txt

    def add_filter(self, new_filter: ParentFilter) -> None:
        if isinstance(new_filter, ParentFilter):
            self.Filters += [new_filter]

    def add_filters(self, new_filters: list) -> None:
        for new_filter in new_filters:
            self.add_filter(new_filter)

    def execute(self) -> None:
        for filter in self.Filters:
            filter.run()


if __name__ == '__main__':

    my_hiree = hireeApp()

    filters = [
        hhResumeColector("Менеджер по продажам", 1000),
        hhExperienceFilter("Менеджер по продажам",
                           writefile_name="hh_exp_res.txt"),
        hhZodiacFilter("Овен", "hh_exp_res.txt", "hh_zod_res.txt"),
        hhGenderFilter("Мужчина",  "hh_zod_res.txt", "hh_gen_res.txt"),
        hhSalaryFilter(60000, 250000, "hh_gen_res.txt", "hh_sal_res.txt"),
        hhVerbFilter("hh_sal_res.txt", "hh_verb_res.txt"),
        hhTagsFilter("hh_verb_res.txt", "hh_tag_res.txt")]

    my_hiree.add_filters(filters)
    try:
        my_hiree.execute()
    except KeyboardInterrupt as e:
        os._exit(1)
