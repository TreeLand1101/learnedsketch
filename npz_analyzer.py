import numpy as np
import argparse

# Parse command-line arguments
parser = argparse.ArgumentParser(description='Load and print contents of an .npz file.')
parser.add_argument('file_path', type=str, help='Path to the .npz file')

args = parser.parse_args()

# Load the .npz file
data = np.load(args.file_path)

# Print the names and sizes of arrays in the .npz file
print("Keys in the npz file:", data.files)

# Print the contents and size of each array
for key in data.files:
    array = data[key]
    print(f"\nData for {key} (size: {array.size}):")
    print(array)
