
# === Internet Traffic ===

## inference

python3 run_ip_model_incremental_learning.py \
    --train ./data/caida/equinix-chicago.dirA.20160121-140000.UTC.anon_00000_20160121220000.npy \
    --resume_model ./model/binary_ip_20241007-225716_ep5.69 --save binary_ip --rnn_hiddens 64 --port_hiddens 16 8 --hiddens 32 32 --batch_size 512 --n_epoch 30 --eval_n_epochs 15 --lr 0.0001 --regress_min 65 --heavy_hitter_threshold 100
