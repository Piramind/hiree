# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup
from time import sleep
import os
from tqdm import tqdm
import subprocess
import re
import pymorphy2


class ParentFilter:
    def __init__(self, readfile_name: str, writefile_name: str):
        self.readfile_name = readfile_name
        self.writefile_name = writefile_name

    def get_html(self, url):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
        html = ""
        try:
            html = requests.get(url, headers=headers).text
        except (requests.exceptions.ReadTimeout, requests.exceptions.ConnectionError) as e:
            print("Обработка исключения в get_html()...")
            sleep(3)
        return html

    # проверяет, есть ли на странице(глобальной) ссылки на вакансии
    def is_empty(self, html):
        soup = BeautifulSoup(html, 'lxml')
        links = soup.find_all('resume-serp_block-result-action')
        if links == []:
            return True
        else:
            return False

    def write_top(self,  some_int: int):
        f = open(self.writefile_name, "r")
        oline = f.readlines()
        oline.insert(0, str(some_int)+'\n')
        f.close()
        f = open(self.writefile_name, "w")
        f.writelines(oline)
        f.close()

    def run(self):
        print("ParentFilter run method")
