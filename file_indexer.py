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
    else:
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
    files = [f for f in files if os.path.isfile(f)]
    infos = list()
    print("""<!doctype html>
<html>
\t<head>
\t\t<title>""" + dir_path + """</title>
\t\t<style>
\t\t\ttable, th, td {
\t\t\t\ttext-align:left
\t\t\t}
\t\t\ttable { width:100%}
\t\t</style>
\t</head>
\t<body>""")
    for file in files:
        if not os.path.isfile(file):
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
        info = (file, ls_output[2], ls_output[3], sum_output.split()[0])
        infos.append(info)
    print('\t\t<table>')
    print('\t\t\t<tr>\n\t\t\t\t<th>Soubor</th>\n\t\t\t\t<th>Velikost [B]</th>\n\t\t\t\t<th>Datum změny</th>\n\t\t\t\t<th>md5sum</th>\n\t\t\t</tr>')
    for info in infos:
        path_n_name_of_file = info[0]
        path_n_name_of_file = path_n_name_of_file.replace(dir_path, '', 1)
        path_n_name_of_file = re.sub(r'^/', '', path_n_name_of_file, 1)
        print(
            f'\t\t\t<tr>\n\t\t\t\t<th>{path_n_name_of_file}</th>\n\t\t\t\t<th>{info[1]}</th>\n\t\t\t\t<th>{info[2]}</th>\n\t\t\t\t<th>{info[3]}</th>\n\t\t\t</tr>')

    print('\t\t</table>')
    print('\t</body>\n</html>')
