import sys
import numpy as np
import argparse

def print_npy(npy_file):
    data = np.load(npy_file, allow_pickle=True).item()
    print(f"File name: {npy_file}")
    print("Keys of the data:", data.keys())
    print(">>> data['note']:\n", data['note'])
    print(">>> data['x'].shape:\n", data['x'].shape)
    print(">>> data['x'][0][:8] (source and destination IPs):\n", data['x'][0][:8])
    print(">>> data['x'][0][8:10] (source and destination ports):\n", data['x'][0][8:10])
    print(">>> data['x'][0][-1] (protocol type):\n", data['x'][0][-1])
    print(">>> data['y'][0] (number of packets):\n", data['y'][0])

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Print a npy file.')
    parser.add_argument('--npy', type=str, required=True, help='The input npy file')
    args = parser.parse_args()

    file_path = args.npy

    if file_path.endswith('.npy'):
        print_npy(file_path)
    else:
        print("Unsupported file format. Please provide a .npy file.")
        sys.exit(1)
