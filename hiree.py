# -*- coding: utf-8 -*-

from Filters.ParentFilter import ParentFilter
from Filters.ResumeColector import hhResumeColector
from Filters.ExperienceFilter import hhExperienceFilter
from Filters.ZodiacFilter import hhZodiacFilter
from Filters.GenderFilter import hhGenderFilter
from Filters.SalaryFilter import hhSalaryFilter
from Filters.VerbFilter import hhVerbFilter
from Filters.TagsFilter import hhTagsFilter


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
    def __init__(self):
        self.Filters = []

    def add_filter(self, new_filter: ParentFilter) -> None:
        self.Filters += [new_filter]

    def add_filters(self, new_filters: list) -> None:
        for new_filter in new_filters:
            # if type(new_filter) == type(ParentFilter):
            self.add_filter(new_filter)

    def execute(self) -> None:
        for filter in self.Filters:
            filter.run()


if __name__ == '__main__':

    my_hiree = hireeApp()

    hhcol = hhResumeColector("Менеджер", 200)
    filters = [hhcol,
               hhExperienceFilter(hhcol.position, writefile_name="exp_res.txt"),
               hhZodiacFilter("Овен", "exp_res.txt", "zod_res.txt"),
               hhGenderFilter("Мужчина", "zod_res.txt", "gen_res.txt"),
               hhSalaryFilter(60000, 250000, "gen_res.txt", "sal_res.txt"),
               hhVerbFilter("sal_res.txt", "verb_res.txt"),
               hhTagsFilter("verb_res.txt", "tag_res.txt")]

    my_hiree.add_filters(filters)
    my_hiree.execute()
