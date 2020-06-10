#!/usr/bin/python3

from subprocess import Popen, TimeoutExpired
import subprocess
import sys
import os
import stat
import os.path
import re
import signal

dir_path = '.'

# Funkce pro psaní na stderr
def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

# Funkce pro ověření práv pro čtení souboru
def isgroupreadable(filepath):
  st = os.stat(filepath)
  return bool(st.st_mode & stat.S_IRGRP)

# Funkce pro zpracování signálu SIGINT (ctrl + c)
def signal_handler(sig, frame):
    eprint('Odchycen signál pro ukončení!')
    print('        </table>')
    print('    </body>\n</html>')
    sys.exit(0)

# Funkce vymění speciální znaky v řetězci za escape sekvence pro XML
sanitize_string_for_xml = lambda s : (s.replace('&', '&amp;')).replace('"', '&quot;').replace('\'', '&apos;').replace('<', '&lt;').replace('>', '&gt;')

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
    output_find, errors_find = '', ''
    try:
        output_find, errors_find = find.communicate(timeout=600)
    except TimeoutExpired:
        eprint('Příkaz find běžel moc dlouho (600s)')
        exit(1)
    if find.returncode != 0:
        eprint(f'Chyba při provádění příkazu find\n\t{errors_find}\n Pokračuji ve spracování dobrých souborů')
    files = output_find.split(sep='\n')
    files = [f for f in files if os.path.isfile(f)]     # odstranění složek z výpisu find
    infos = list()
    # kostra html
    dir_path = sanitize_string_for_xml(dir_path)
    print("""<?xml version="1.0" encoding="UTF-8" ?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN"
"http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
    <head>
        <title>""" + dir_path + """</title>
        <style type="text/css">
            table, th, td {
                border: 1px solid black;
                border-collapse: collapse;
                padding: 5px;
                text-align:left; }
            table {width:100%}
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
                <th>Identifikátor MD5</th>\n\
            </tr>')
    signal.signal(signal.SIGINT, signal_handler)
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
            sum_output, sum_err = md5sum.communicate(timeout=150)
            ls_output, ls_err = ls.communicate(timeout=5)
        except TimeoutExpired:
            md5sum.kill()
            ls.kill()
            sum_output, sum_err = md5sum.communicate(timeout=10)
            ls_output, ls_err = ls.communicate(timeout=10)
            eprint(f'Přeskakuji soubor, kvůli překročení timeout limitu {file}\n\t{sum_err}\n\n{ls_err}')
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
        path_n_name_of_file = sanitize_string_for_xml(path_n_name_of_file)
        print(f'\
            <tr>\n\
                <td>{path_n_name_of_file}</td>\n\
                <td>{info[0]}</td>\n\
                <td>{info[1]}</td>\n\
                <td>{info[2]}</td>\n\
            </tr>')
    # konec výpisu
    print('        </table>')
    print('    </body>\n</html>')
