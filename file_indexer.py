#!/usr/bin/python

from subprocess import Popen
import subprocess
import sys
import os.path


dir_path = '.'
jobs = 2
mdsum_bin = '/usr/bin/md5sum'
ls_bin = '/usr/bin/ls'
# Funkce pro psaní na stderr
def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


def arg_parser(argv):
    ...
def html_gen():
    ...

if __name__ == "__main__":
    # načtení listu souborů ke spočítání md5sum
    if len(sys.argv) == 1:
        eprint('Chybí cesta ke složce, jako 1. argument.')
        exit(1)
    else:
        dir_path = sys.argv[1]
    find = Popen(["find", dir_path],
                 stdout=subprocess.PIPE,
                 stderr=subprocess.PIPE,
                 universal_newlines=True
                 )
    output_find, errors_find = find.communicate()
    files = output_find.split(sep='\n')
    files = [f for f in files if os.path.isfile(f)]
    infos = list()
    output_html = """<!doctype html>
<html>
<head>
<title>""" + dir_path + """</title>
</head>
<body>
"""
    for file in files:
        if not os.path.isfile(file):
            continue
        sum = Popen(["md5sum", file],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    universal_newlines=True)
        ls  = Popen(["ls", '-log', '--time-style=+%Y-%m-%d', file],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    universal_newlines=True)
        sum_output, sum_err = sum.communicate()
        ls_output, ls_err = ls.communicate()
        ls_output = ls_output.split()
        # output vars
        file_size = ls_output[2]
        file_date = ls_output[3]
        file_sum = sum_output.split()[0]
        info = (file, ls_output[2], ls_output[3], sum_output.split()[0])
        infos.append(info)
    output_html += '<table style="width:100%">\n'
    output_html += '<tr>\n<th>Soubor</th>\n<th>Velikost</th>\n<th>Datum změny</th>\n<th>md5sum</th>\n</tr>'
    for info in infos:
        output_html += f'<tr>\n<th>{info[0]}</th>\n<th>{info[1]}</th>\n<th>{info[2]}</th>\n<th>{info[3]}</th>\n</tr>'
    print(output_html)
