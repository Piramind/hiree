# -*- coding: utf-8 -*-

from requests import get, exceptions
from bs4 import BeautifulSoup
from time import sleep
from tqdm import tqdm
from abc import ABCMeta, abstractmethod


class ParentFilter():
    __metaclass__ = ABCMeta

    def __init__(self, readfile_name: str, writefile_name: str):
        self.readfile_name = readfile_name
        self.writefile_name = writefile_name

    def _get_html(self, url) -> str:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
        html = ""
        for i in range(5):
            try:
                html = get(url, headers=headers).text
                str_err = None
            except Exception as str_err:
                pass
            if str_err:
                print("Обработка исключения в _get_html...")
                sleep(2)
            else:
                break
        return html

    def _write_top(self,  some_int: int) -> None:
        f = open(self.writefile_name, "r")
        oline = f.readlines()
        oline.insert(0, str(some_int)+'\n')
        f.close()
        f = open(self.writefile_name, "w")
        f.writelines(oline)
        f.close()

    @abstractmethod
    def run(self) -> None:
        raise NotImplementedError
