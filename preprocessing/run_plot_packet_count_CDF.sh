#!/bin/sh

prefix=equinix-chicago.dirA.20160121-140000.UTC.anon

# caida
python3 plot_packet_count_CDF.py \
    --log ./caida/log/${prefix}.log \
    --log_scale \
    --save ./caida/plotting