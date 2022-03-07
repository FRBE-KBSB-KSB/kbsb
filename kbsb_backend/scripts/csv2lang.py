import csv
import json
import enum


def csv2lang():
    with open("share/data/i18n.csv", newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        allrows = []
        for r in reader:
            allrows.append(r)
    for l in ['en', 'fr', 'nl', 'de']:
        with open(f'frontend/src/util/{l}.js', 'w', encoding='utf8') as f:
            f.write(f'const {l} = {{\n')
            for r in allrows:
                value = r[l].replace('\n', '').replace('\r', '')
                f.write(f'"{r["key"]}": "{value}",\n')
            f.write('}\n')
            f.write(f'export default {l}')

if __name__ == '__main__':
    csv2lang()
    print('done')

