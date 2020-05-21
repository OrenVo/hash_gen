#!/usr/bin/python

from subprocess import Popen
import subprocess
import sys
import os.path
import re

dir_path = '.'

# Funkce pro psaní na stderr
def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

if __name__ == "__main__":
    # načtení listu souborů ke spočítání md5sum
    if len(sys.argv) == 1:
        eprint('Chybí cesta ke složce, jako 1. argument.')
        exit(1)
    else:   # kontrola vstupní složky, jestli je složka
        dir_path = sys.argv[1]
        if not os.path.isdir(dir_path):
            eprint(f'Uvedená cesta {dir_path}, není složkou.')
            exit(1)
    find = Popen(["find", dir_path],
                 stdout=subprocess.PIPE,
                 stderr=subprocess.PIPE,
                 universal_newlines=True
                 )
    output_find, errors_find = find.communicate()
    files = output_find.split(sep='\n')
    files = [f for f in files if os.path.isfile(f)]     # odstranĚní složek z výpisu find
    infos = list()
    # kostra html
    print("""<!doctype html>
<html>
    <head>
        <title>""" + dir_path + """</title>
        <style>
            table, th, td {
                text-align:left
            }
            table { width:100%}
        </style>
    </head>
    <body>""")
    # generování tabulky
    print('        <table>')
    print('\
            <tr>\n\
                <th>Soubor</th>\n\
                <th>Velikost [B]</th>\n\
                <th>Datum změny</th>\n\
                <th>md5sum</th>\n\
            </tr>')
    for file in files:
        if not os.path.isfile(file):    # přeskočení složek
            continue
        md5sum = Popen(["md5sum", file],
                       stdout=subprocess.PIPE,
                       stderr=subprocess.PIPE,
                       universal_newlines=True)
        ls = Popen(["ls", '-log', '--time-style=+%Y-%m-%d', file],
                   stdout=subprocess.PIPE,
                   stderr=subprocess.PIPE,
                   universal_newlines=True)
        sum_output, sum_err = md5sum.communicate()
        ls_output, ls_err = ls.communicate()
        ls_output = ls_output.split()
        # output vars
        file_size = ls_output[2]
        file_date = ls_output[3]
        file_sum = sum_output.split()[0]
        info = (ls_output[2], ls_output[3], sum_output.split()[0])
        path_n_name_of_file = file
        path_n_name_of_file = path_n_name_of_file.replace(dir_path, '', 1)
        path_n_name_of_file = re.sub(r'^/', '', path_n_name_of_file, 1)
        print(f'\
            <tr>\n\
                <th>{path_n_name_of_file}</th>\n\
                <th>{info[0]}</th>\n\
                <th>{info[1]}</th>\n\
                <th>{info[2]}</th>\n\
            </tr>')
    # konec výpisu
    print('        </table>')
    print('    </body>\n</html>')
