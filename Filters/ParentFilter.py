# -*- coding: utf-8 -*-

from requests import get, exceptions
from time import sleep
from abc import ABCMeta, abstractmethod


class ParentFilter():
    __metaclass__ = ABCMeta

    def __init__(self, file_name: str):
        self.file_name = file_name

    def _get_html(self, url) -> str:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
        html = ""
        for i in range(5):
            try:
                html = get(url, headers=headers).text
                error = False
            except:
                error = True
            if error:
                print("Обработка исключения в _get_html...")
                sleep(2)
            else:
                break
        return html

    def _write_top(self,  some_int: int) -> None:
        f = open(self.writefile_name, "r")
        all_lines = f.readlines()
        all_lines.insert(0, str(some_int)+'\n')
        f.close()
        f = open(self.writefile_name, "w")
        f.writelines(all_lines)
        f.close()

    def _write_result_links(self, file_name: str, result_links: list, display_msg: bool = True) -> None:
        open(file_name, 'w', encoding='utf-8').close()
        with open(file_name, 'w', encoding='utf-8') as f:
            f.write(str(len(result_links)) + '\n')
            for link in result_links:
                f.write(link + '\n')
        if display_msg:
            print("Найдено", len(result_links), "подходящих резюме.")

    @abstractmethod
    def run(self) -> None:
        raise NotImplementedError
