import json
import requests
from os import path, environ
from mailer import Mailer
from datetime import datetime
from dotenv import load_dotenv, find_dotenv


class Bowling(object):
    def __init__(self):
        try:
            load_dotenv(find_dotenv())
        except Exception:
            print("Could not find .env, rename .env.example and set values")
            exit()

        self.url = environ.get("URL")
        self.save_dir = environ.get("SAVE_DIR")
        self.results_changed = False
        self.results = dict()
        self.get_results()

        self.send_results_email()

    def load(self):
        if not path.isfile(self.save_dir):
            self.results_changed = True
            return None

        with open(self.save_dir) as data_file:
            results = json.load(data_file)

        return results

    def save(self, results):
        previous = self.load()

        if previous:
            results = self.diff_results(previous, results)

        self.results = results

        with open(self.save_dir, 'w') as out:
            out.write(json.dumps(results))

    def diff_results(self, old_results, new_results):
        results = old_results

        for result in new_results.items():
            if not result[0] in results:
                self.results_changed = True
                results[result[0]] = result[1]

        return results

    def get_results(self):
        raw_data = self.get_raw_data()
        data = self.sort_data(raw_data)
        self.save(data)

    def sort_data(self, raw):
        raw = raw.split('<tr')
        raw = raw[1:]

        data = dict()

        for row in raw:
            row_array = row.split('<td>')

            date = row_array[2][:-5]
            game1 = row_array[4][:-5].replace('*', '')
            game2 = row_array[5][:-5].replace('*', '')
            game3 = row_array[6][:-5].replace('*', '')

            if game1.isdigit() and game2.isdigit() and game3.isdigit():
                data[date] = [game1, game2, game3]

        return data

    def get_raw_data(self):
        page = requests.get(self.url)
        content = str(page.content)

        player = self.url[len(self.url) - 7:]
        player = player.replace('#', '')

        top_section = content.find('name={}'.format(player))
        if top_section == -1: exit()

        content = content[top_section:]

        bottom_section = content.find('</table>')
        if bottom_section == -1: exit()

        content = content[:bottom_section]

        tbody = content.find('<tbody>')
        if tbody == -1: exit()

        content = content[tbody:]

        tbody_end = content.find('</tbody>')
        if tbody_end == -1: exit()

        content = content[:tbody_end]

        return content

    def average(self):
        total = 0
        count = 0

        for scores in self.results.items():
            total += (int(scores[1][0]) + int(scores[1][1]) + int(scores[1][2]))
            count += 3

        average = int((total / count))
        return "Average score of {} with a total of {} games. \n" \
               "Total pin count is {}.".format(average, count, total)

    def high_game(self):
        highest = 0
        week = ''

        for scores in self.results.items():
            for game in scores[1]:
                if int(game) > highest:
                    highest = int(game)
                    week = scores[0]

        return "Highest game on {} with a score of {}.".format(week, highest)

    def high_series(self):
        highest = 0
        week = ''

        for scores in self.results.items():
            total = (int(scores[1][0]) + int(scores[1][1]) + int(scores[1][2]))
            if int(total) > highest:
                highest = int(total)
                week = scores[0]

        return "Highest series on {} with a total of {}.".format(week, highest)

    def latest_game(self):
        date = datetime.strptime('01/01/1990', "%d/%m/%Y").date()

        for week in self.results.items():
            week_date = datetime.strptime(week[0], "%d/%m/%Y").date()

            if week_date > date:
                date = week_date

        key = date.strftime('%d/%m/%Y')
        results = self.results[key]
        total = int(results[0]) + int(results[1]) + int(results[2])

        return "Latest game on {}, with scores of {}, {}, {}. Series total of {}".format(key, results[0], results[1], results[2], total)

    def send_results_email(self):
        body = ''
        methods = {
            'latest_game',
            'average',
            'high_game',
            'high_series'
        }

        for method in methods:
            body += getattr(self, method)() + "\n\n"

        if environ.get("MAIL_SEND", False) != 'False' and self.results_changed:
            Mailer(body)
        else:
            print(body)


if __name__ == '__main__':
    bowling = Bowling()
