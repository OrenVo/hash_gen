#!/usr/bin/python

from subprocess import Popen, TimeoutExpired
import subprocess
import sys
import os
import stat
import os.path
import re

dir_path = '.'

# Funkce pro psaní na stderr
def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

# Funkce pro ověření práv pro čtení souboru
def isgroupreadable(filepath):
  st = os.stat(filepath)
  return bool(st.st_mode & stat.S_IRGRP)

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
    try:
        output_find, errors_find = find.communicate(timeout=600)
    except TimeoutExpired:
        eprint('Příkaz find běžel moc dlouho (600s)')
        exit(1)
    if find.returncode != 0:
        eprint(f'Chyba při provádění příkazu find\n\t{errors_find}\n Pokračuji ve spracování dobrých souborů')
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
        # Pro kontrolu přístupových práv k souboru odkomentujte následující řádky (vypnuto kvůli optimalizaci systémových volání)
        #if not isgroupreadable(file):
        #   continue
        md5sum = Popen(["md5sum", file],
                       stdout=subprocess.PIPE,
                       stderr=subprocess.PIPE,
                       universal_newlines=True)
        ls = Popen(["ls", '-log', '--time-style=+%Y-%m-%d', file],
                   stdout=subprocess.PIPE,
                   stderr=subprocess.PIPE,
                   universal_newlines=True)
        try:
            sum_output, sum_err = md5sum.communicate(timeout=30)
            ls_output, ls_err = ls.communicate(timeout=30)
        except TimeoutExpired:
            md5sum.kill()
            ls.kill()
            sum_output, sum_err = md5sum.communicate(timeout=10)
            ls_output, ls_err = ls.communicate(timeout=10)
            eprint(f'Přeskakuji soubor {file}\n\t{sum_err}\n\n{ls_err}')
            continue
        ls_output = ls_output.split()
        # output vars
        if md5sum.returncode != 0:
            eprint(f'Přeskakuji soubor {file}\n\t{sum_err}')
            continue
        if ls.returncode != 0:
            eprint(f'Přeskakuji soubor {file}\n\t{ls_err}')
            continue
        try:
            info = (ls_output[2], ls_output[3], sum_output.split()[0])
        except IndexError:
            eprint(f'Chyba při zpracování výstupu md5sum, nebo ls. Přeskakuji soubor {file}')
            continue
        path_n_name_of_file = file.replace(dir_path, '', 1)
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
