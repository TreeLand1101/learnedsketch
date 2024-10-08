#!/bin/sh

prefix=equinix-chicago.dirA.20160121-140000.UTC.anon

# caida
python3 ./pcap2npy.py --pcap ./caida/pcap/${prefix}.pcap \
                      --npy ./caida/npy/${prefix}.npy \
                      --log ./caida/log/${prefix}.log