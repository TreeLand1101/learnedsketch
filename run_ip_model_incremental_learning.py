import os
import sys
import time
import argparse
import random
import datetime
import numpy as np
import tensorflow as tf

from utils.utils import get_stat, git_log, AverageMeter, keep_latest_files, get_data, get_data_list
from utils.nn_utils import fc_layers, write_summary

from run_ip_model import construct_graph, train, evaluate, run_training, calculate_model_memory_size, evaluate
from collections import defaultdict
import hashlib
import math

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3' 
os.environ['CUDA_VISIBLE_DEVICES'] = '-1'
tf.compat.v1.logging.set_verbosity(tf.compat.v1.logging.ERROR)

def binary_to_decimal_ip(binary_list):
    ip_bin_str = ''.join([str(int(b)) for b in binary_list])
    ip_decimal = [str(int(ip_bin_str[i:i+8], 2)) for i in range(0, 32, 8)]
    return '.'.join(ip_decimal)

def binary_to_decimal_port(binary_list):
    port_bin_str = ''.join([str(int(b)) for b in binary_list])
    return str(int(port_bin_str, 2))

def restore_flow(flow):
    binary_src_ip = flow[:32]
    binary_dst_ip = flow[32:64]
    binary_src_port = flow[64:80]
    binary_dst_port = flow[80:96]

    src_ip = binary_to_decimal_ip(binary_src_ip)
    dst_ip = binary_to_decimal_ip(binary_dst_ip)
    src_port = binary_to_decimal_port(binary_src_port)
    dst_port = binary_to_decimal_port(binary_dst_port)
    protocol = flow[-1]

    return src_ip, dst_ip, src_port, dst_port, protocol


def inference(model, x, y, args, width=10000, depth=5):
    cm_sketch = np.zeros((depth, width), dtype=np.int32)
    unique_bucket = defaultdict(int)
    not_heavy_flows_count = 0
    heavy_flows_count = 0
    underestimated_flows_count = 0

    with tf.Session() as sess:
        sess.run(tf.global_variables_initializer())

        saver = tf.train.Saver()
        
        saver.restore(sess, args.resume_model)  
        print("Model restored.")

        _, output_all = evaluate(model, x, y, args, sess)

        total_flows = output_all.shape[0]

        for i in range(total_flows):
            flow_output = output_all[i]
            flow_id = restore_flow(x[i])
            if flow_output < args.heavy_hitter_threshold:
                not_heavy_flows_count += 1
                for d in range(depth):
                    hash_index = hash(flow_id) % width
                    cm_sketch[d, hash_index] += 1
            else:
                heavy_flows_count += 1
                unique_bucket[flow_id] += 1


        for i in range(total_flows):
            flow_output = output_all[i]
            flow_id = restore_flow(x[i])
            if flow_output < args.heavy_hitter_threshold:
                estimated_count = min(cm_sketch[d, hash(flow_id) % width] for d in range(depth))
                if estimated_count > args.heavy_hitter_threshold:
                    underestimated_flows_count += 1
        

        # print(f"Unique bucket entries:")
        # for flow, count in unique_bucket.items():
        #     print(f"Flow: {flow}, Count: {count}")

        not_heavy_flows_ratio = not_heavy_flows_count / total_flows
        heavy_flows_threshold_ratio = heavy_flows_count / total_flows
        underestimated_flows_ratio = underestimated_flows_count / total_flows

        print(f"Number of not heavy flows: {not_heavy_flows_count}")
        print(f"Number of heavy flows: {heavy_flows_count}")
        print(f"Number of underestimated flows: {underestimated_flows_count}")
        print(f"Proportion of not heavy flows: {not_heavy_flows_ratio:.2%}")
        print(f"Proportion of heavy flows: {heavy_flows_threshold_ratio:.2%}")
        print(f"Proportion of underestimated flows: {underestimated_flows_ratio:.2%}")

if __name__ == '__main__':
    argparser = argparse.ArgumentParser(sys.argv[0])
    argparser.add_argument("--train", type=str, nargs='*', help="train data (.npy file)", default="")
    # argparser.add_argument("--valid", type=str, nargs='*', help="validation data (.npy file)", default="")
    # argparser.add_argument("--test", type=str, nargs='*', help="testing data (.npy file)", required=True)
    argparser.add_argument("--save_name", type=str, help="name for the save results", required=True)
    argparser.add_argument("--seed", type=int, help="random seed", default=69)
    argparser.add_argument("--n_examples", type=int, help="# of examples to use per .npy file", default=10000000)
    argparser.add_argument("--n_epochs", type=int, help="number of epochs for training", default=1)
    argparser.add_argument("--eval_n_epochs", type=int, help="inference on validation and test set every eval_n_epochs epochs", default=20)
    argparser.add_argument("--batch_size", type=int, help="batch size for training", default=512)
    argparser.add_argument('--keep_probs', type=float, nargs='*', default=[], help="dropout probabilities for the final layers")
    argparser.add_argument("--lr", type=float, default = 0.0001, help="learning rate")
    argparser.add_argument("--memory", type=float, default = 1.0, help="GPU memory fraction used for model training")
    argparser.add_argument('--resume_model', type=str, default="", help="Path to a model checkpoint.")
    argparser.add_argument('--start_epoch', type=int, default=0, help="For checkpoint and summary logging. Specify this to be the epoch number of the loaded checkpoint +1.")
    argparser.add_argument('--activation', type=str, default="LeakyReLU", help="activation for FC layers")
    argparser.add_argument('--evaluate', action='store_true', default=False, help="Run model evaluation without training.")
    argparser.add_argument("--regress_min", type=float, default=1, help="minimum cutoff for regression")
    argparser.add_argument('--rnn_hiddens', type=int, nargs='*', default=[64], help="# of hidden units for the ip RNN layers")
    argparser.add_argument('--port_hiddens', type=int, nargs='*', default=[16, 8], help="# of hidden units for the port FC layers")
    argparser.add_argument('--hiddens', type=int, nargs='*', default=[32, 32], help="# of hidden units for the final layers")
    argparser.add_argument('--decimal_ip', action='store_true', default=False, help="Keep the decimal format of IP addresses")
    argparser.add_argument('--reverse_ip', action='store_true', default=False, help="Reversing the order of IP addresses in RNN timestamp features")
    argparser.add_argument('--heavy_hitter_threshold',  type=int, default=100 , help="heavy hitter threshold")
    args = argparser.parse_args()


    if not args.keep_probs:
        args.keep_probs = np.ones(len(args.hiddens)+1)
    assert len(args.hiddens)+1 == len(args.keep_probs)

    np.random.seed(args.seed)
    random.seed(args.seed)
    tf.set_random_seed(args.seed)
    np.set_printoptions(precision=3)
    np.set_printoptions(suppress=True)


    feat_idx = np.arange(11)

    if args.decimal_ip:
        args.n_feat = 2*4+2*16+1    # ip-> 2*4, port-> 2*16, protocol->1
    else:
        args.n_feat = 8*8+2*16+1    # ip-> 8*8, port-> 2*16, protocol->1

    args.heavy_hitter_threshold = math.log(args.heavy_hitter_threshold)

    start_t = time.time()

    train_x, train_y = get_data(args.train, feat_idx, args.n_examples, args.decimal_ip, args.reverse_ip)
    data_stat = get_stat('train before log', train_x, train_y)
    train_y = np.log(train_y)
    rmin = np.log(args.regress_min)
    data_stat += get_stat('train before rmin', train_x, train_y)
    s = 'rmin %.2f, # train_y < min %.2f\n\n' % (rmin, np.sum(train_y < rmin))

    model = construct_graph(args)

    inference(model, train_x, train_y, args)