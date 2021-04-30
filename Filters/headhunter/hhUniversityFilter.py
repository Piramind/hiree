# -*- coding: utf-8 -*-

from Filters.UniversityFilter import UniversityFilter


class hhUniversityFilter(UniversityFilter):
    def __init__(self, desired_university: str = '', file_name: str = "hh_RESULT.txt"):
        super().__init__(desired_university, file_name)

    def _check_university(self, soup) -> bool:
        all_universities = soup.find_all('div', class_="resume-block-education-name")
        if all_universities is None:
            return False
        else:
            if desired_university == '':
                return True
            else:
                for university in all_universities:
                    if desired_university in university.text:
                        return True
                return False

    def run(self) -> None:
        print("HeadHunter: Проверяем высшее образование...")
        super().run()
