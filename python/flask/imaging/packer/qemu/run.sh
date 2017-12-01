#!/bin/bash

APP_PORT=$(./app_port.py)

cd packer_output
qemu-system-x86_64 flask-github-jobs.qcow2 -m 2048 \
-net user,hostfwd=tcp::22222-:22,hostfwd=tcp::${APP_PORT}-:${APP_PORT} \
-net nic  \
-machine accel=kvm \
-nographic \

