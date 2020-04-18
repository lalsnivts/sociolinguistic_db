import csv

def write_together(paths):
    first_file = 1
    for path in paths:
        with open(path, 'r', encoding='utf-8') as file:
            file = file.readlines()
        with open('NewQuest.csv', 'a', encoding='utf-8') as t:
            if first_file:
                for line in file:
                    t.write(line)
            else:
                for line in file[1:]:
                    t.write(line)
        first_file = 0

#write_together()
bios = ['Tura2014.csv', 'Turukhansk2014.csv', 'Uchami2014.csv', 'XO2011.csv', 'Yukta2014.csv', 'Dudinka2011.csv']


def extract_lang(paths):
    for path in paths:
        origin = path + '.csv'
        destin = path + '_lang.csv'
        with open(origin, 'r', encoding='utf-8') as file:
            header = file.readline().split('\t')
            file = file.readlines()
            with open(destin, 'w', encoding='utf-8') as t:
                for line in file:
                    one_person = []
                    row = line.split('\t')
                    for i in range(2, 7):
                        one_person.append('\t'.join((row[0], row[1], header[i].strip(), row[i])))
                    t.write('\n'.join(one_person))

langs = ['LangTura2014', 'LangTurukhansk2014', 'LangUchami2014', 'LangXO2011',
         'LangYukta2014', 'LangDudinka2011']

extract_lang(langs)