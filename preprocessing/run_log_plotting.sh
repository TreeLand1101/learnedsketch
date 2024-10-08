#!/bin/sh

prefix=equinix-chicago.dirA.20160121-140000.UTC.anon_00000_20160121220000

# caida
python3 log_plotting.py --log ./caida/log/${prefix}.log \
                        --top_k 20 \
                        --rank 1000 \
                        --save ./caida/plotting