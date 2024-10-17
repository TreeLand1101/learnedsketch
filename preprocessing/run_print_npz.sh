#!/bin/sh

prefix=binary_ip_20241007-125313_ep30.69

# caida
python3 print_npz.py \
    --npz ./caida/npz/${prefix}.npz