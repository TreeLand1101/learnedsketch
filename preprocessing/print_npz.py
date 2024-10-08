import sys
import numpy as np
import argparse

def print_npz(npz_file):
    data = np.load(npz_file, allow_pickle=True)
    print(f"File name: {npz_file}")
    print(f"Number of arrays: {len(data.files)}\n")
    
    for i, array_name in enumerate(data.files):
        array_data = data[array_name]
        print(f"Array {i+1}: '{array_name}'")
        print(f"  Shape: {array_data.shape}")
        print(f"  Data type: {array_data.dtype}")
        print(f"  Size: {array_data.size}")
        print(f"  Memory: {array_data.nbytes} bytes")
        if array_data.size > 0:
            print(f"  array_data.flat[0]: {array_data.flat[0]}\n")
        else:
            print("  Array is empty\n")
    
    data.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Print a npz file.')
    parser.add_argument('--npz', type=str, required=True, help='The input npz file')
    args = parser.parse_args()

    file_path = args.npz

    if file_path.endswith('.npz'):
        print_npz(file_path)
    else:
        print("Unsupported file format. Please provide a .npz file.")
        sys.exit(1)
