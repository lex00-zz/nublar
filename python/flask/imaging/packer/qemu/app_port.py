#!/usr/bin/python
import json
import sys
import os

# CHANGE TO SCRIPT DIR
abspath = os.path.abspath(__file__)
script_dir = os.path.dirname(abspath)
os.chdir(script_dir)
os.chdir('../../../variables/qemu')

data = json.load(open('nublar.json'))
app_port = data['app_port']

sys.stdout.write(app_port)

