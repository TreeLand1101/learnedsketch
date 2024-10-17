#!/bin/sh

prefix=equinix-chicago.dirA.20160121-140000.UTC.anon

# caida
python3 plot_HH_threshold_vs_number_of_flows.py \
    --log ./caida/log/${prefix}.log \
    --begin 0.01 \
    --end 0.05 \
    --interval 0.005 \
    --save ./caida/plotting