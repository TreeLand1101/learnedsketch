import sys
import numpy as np
import os

def analyze_npz(npz_file):
    # Load the .npz file
    data = np.load(npz_file)
    
    print(f"Analyzing file: {npz_file}")
    print(f"Number of arrays: {len(data.files)}\n")

    # Iterate through the contents of the .npz file
    for i, array_name in enumerate(data.files):
        array_data = data[array_name]
        print(f"Array {i+1}: '{array_name}'")
        print(f"  Shape: {array_data.shape}")
        print(f"  Data type: {array_data.dtype}")
        print(f"  Size: {array_data.size}")
        print(f"  Memory: {array_data.nbytes} bytes\n")
    
    data.close()

def analyze_npy(npy_file):
    # Load the .npy file
    data = np.load(npy_file, allow_pickle=True).item()
    
    print(f"Analyzing file: {npy_file}")

    # Print the keys of the data
    print("Keys of the data:", data.keys())

    # Print the note
    print(">>> data['note']:\n", data['note'])

    # Print the shape of 'x'
    print(">>> data['x'].shape:\n", data['x'].shape)

    # Print the first entry details
    print(">>> data['x'][0][:8] (source and destination IPs):\n", data['x'][0][:8])
    print(">>> data['x'][0][8:10] (source and destination ports):\n", data['x'][0][8:10])
    print(">>> data['x'][0][-1] (protocol type):\n", data['x'][0][-1])

    # Print the number of packets in the first entry of 'y'
    print(">>> data['y'][0] (number of packets):\n", data['y'][0])

if __name__ == "__main__":
    # Check if the file path is provided as a command-line argument
    if len(sys.argv) < 2:
        print("Usage: python npy_npz_analyzer.py <path_to_npy_or_npz_file>")
        sys.exit(1)
    
    # Get the file path from the command-line argument
    file_path = sys.argv[1]
    
    # Check the file extension to determine how to process the file
    if file_path.endswith('.npz'):
        analyze_npz(file_path)
    elif file_path.endswith('.npy'):
        analyze_npy(file_path)
    else:
        print("Unsupported file format. Please provide a .npy or .npz file.")
        sys.exit(1)
