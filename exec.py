#!/usr/bin/env python3
from os.path import dirname
from datetime import datetime
from os import execl

start = open(dirname(__file__) + '/private/start.txt', 'w')
start.write(datetime.now().strftime('%s.%f'))
start.close()
print('[    0.000000] running')
execl(dirname(__file__) + '/main.py', '--')
