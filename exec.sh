#!/bin/bash
date +%s.%N | cut -c -18 > private/start.txt
exec ./main.py $1
