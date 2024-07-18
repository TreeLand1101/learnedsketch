import sys
import numpy as np

# Check if the file path is provided as a command-line argument
if len(sys.argv) < 2:
    print("Usage: python script.py <path_to_npy_file>")
    sys.exit(1)

# Load the data from the file provided as an argument
file_path = sys.argv[1]
data = np.load(file_path, allow_pickle=True).item()

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
