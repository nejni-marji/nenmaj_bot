#!/bin/bash
date +%s.%N | cut -c -18 > private/start.txt
echo '[    0.000000] running'
exec ./main.py $1
