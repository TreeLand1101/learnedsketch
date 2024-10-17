#!/bin/sh

prefix=equinix-chicago.dirA.20160121-140000.UTC.anon

# caida
python3 plot_packet_count_distribution.py \
    --log ./caida/log/${prefix}.log \
    --top_k 10 \
    --rank 1500 \
    --save ./caida/plotting