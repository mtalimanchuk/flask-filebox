#!/bin/bash

nohup python3 ./filebox.py &
disown &&
echo 'OK.'
