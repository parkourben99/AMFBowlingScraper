import json
import requests
import os


class Bowling(object):
    def __init__(self):
        self.url = 'http://results.amfbowling.com.au/league-bowling.php?centre=44&results=6/bowlers.htm#plyr47'
        self.save_dir = 'results.json'
        self.results = dict()
        self.get_results()

    def load(self):
        if not os.path.isfile(self.save_dir):
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
        return new_results
        results = self.merge_dicts(old_results, new_results)

        return list({v[0]:v for v in results}.values())

    def merge_dicts(self, *dict_args):
        """
        Given any number of dicts, shallow copy and merge into a new dict,
        precedence goes to key value pairs in latter dicts.
        http://stackoverflow.com/questions/38987/how-to-merge-two-python-dictionaries-in-a-single-expression
        """
        result = {}
        for dictionary in dict_args:
            result.update(dictionary)
        return result

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

        average = (total / count)
        print(average)


if __name__ == '__main__':
    bowling = Bowling()
    bowling.average()