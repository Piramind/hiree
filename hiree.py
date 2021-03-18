# -*- coding: utf-8 -*-

from Filters.hhResumeColector import hhResumeColector
from Filters.hhExperienceFilter import hhExperienceFilter
from Filters.hhZodiacFilter import hhZodiacFilter
from Filters.hhGenderFilter import hhGenderFilter
from Filters.hhSalaryFilter import hhSalaryFilter
from Filters.hhVerbFilter import hhVerbFilter
from Filters.hhTagsFilter import hhTagsFilter


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


if __name__ == '__main__':
    hhcol = hhResumeColector("Менеджер", 2000)
    filters = [hhcol,
               hhExperienceFilter(hhcol.position, writefile_name="exp_res.txt"),
               hhZodiacFilter("Овен", "exp_res.txt", "zod_res.txt"),
               hhGenderFilter("Мужчина", "zod_res.txt", "gen_res.txt"),
               hhSalaryFilter(60000, 250000, "gen_res.txt", "sal_res.txt"),
               hhVerbFilter("sal_res.txt", "verb_res.txt"),
               hhTagsFilter("verb_res.txt", "tag_res.txt")]
    for filter in filters:
        filter.run()
