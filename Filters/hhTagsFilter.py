from .ParentFilter import *


class hhTagsFilter(ParentFilter):
    def __init__(self, readfile_name="all_resumes.txt", writefile_name="tagged_resumes.txt"):
        super().__init__(readfile_name, writefile_name)

    def run(self):
        print("Проверяем теги...")
        keywords11, keywords12, keywords13, keywords21 = [], [], [], []

        with open("1-1_condition.txt", 'r', encoding='utf-8') as f:
            keywords11 = [word.strip() for word in f]

        with open("1-2_condition.txt", 'r', encoding='utf-8') as f:
            keywords12 = [word.strip() for word in f]

        with open("1-3_condition.txt", 'r', encoding='utf-8') as f:
            keywords13 = [word.strip() for word in f]

        with open("2-1_condition.txt", 'r', encoding='utf-8') as f:
            keywords21 = [word.strip() for word in f]

        data = dict()

        with open(self.readfile_name, 'r', encoding='utf-8') as read_file:
            progress = int(read_file.readline().strip())
            link_ind = 0
            pbar = tqdm(total=progress)
            while link_ind < progress:
                link = read_file.readline().strip()
                try:
                    html = get_html(link)
                    soup = BeautifulSoup(html, 'lxml')
                except (requests.exceptions.ReadTimeout, requests.exceptions.ConnectionError) as e:
                    print(" Переподключение к страничке с резюме...")
                    sleep(3)

                job_dscrptn = soup.find_all(
                    attrs={"data-qa": "resume-block-experience-description"})
                if not job_dscrptn:
                    link_ind += 1
                    pbar.update()
                    continue

                job = "".join(j.get_text() for j in job_dscrptn)
                job = re.sub("[^А-Яа-я .]", "", job)

                total_value = 0.1*any(k21 in job for k21 in keywords21)

                job = job.split('.')
                i = 0
                while i < len(job):
                    j = job[i]
                    sentence_value = 1 * any(k11 in j for k11 in keywords11)
                    sentence_value += 1 * any(k12 in j for k12 in keywords12)
                    sentence_value += 1 * any(k13 in j for k13 in keywords13)
                    if sentence_value > 0:
                        total_value += sentence_value
                    i += 1
                if(total_value > 1):
                    data[link] = total_value
                link_ind += 1
                pbar.update()
        pbar.close()
        print("Найдено", len(data), "подходящих резюме.")
        with open(self.writefile_name, 'w', encoding='utf-8') as f:
            f.write(str(len(data)) + '\n')
            for k in sorted(data, key=data.get, reverse=True):
                f.write(k + ' ' + str(data[k]) + '\n')
