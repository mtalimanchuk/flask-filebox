#!/bin/bash

log='log.txt'
python3 ./filebox.py > $log &
disown &&
echo 'OK.'
