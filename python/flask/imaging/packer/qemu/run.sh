#!/bin/bash
cd packer_output
qemu-system-x86_64 flask-github-jobs.qcow2 -m 2048 \
-net user,hostfwd=tcp::22222-:22,hostfwd=tcp::3000-:3000 \
-net nic  \
-machine accel=kvm \
-nographic \

