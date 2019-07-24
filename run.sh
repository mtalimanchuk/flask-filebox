#!/bin/bash

chmod u+x filebox.py &&
python3 ./filebox.py &
disown &&
echo 'OK.'
