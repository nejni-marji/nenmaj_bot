#!/usr/bin/env python3
from os.path import dirname
from os import execl
from sys import argv

text = 'rebooting'
num = len(text)

resp = []
resp.append('*' * (num + 6))
resp.append('== %s ==' % text.upper())
resp.append('*' * (num + 6))

print('\n'.join(resp))

data = [str(argv[1]), str(argv[2])]
execl(dirname(__file__) + '/main.py', '--', *data)
