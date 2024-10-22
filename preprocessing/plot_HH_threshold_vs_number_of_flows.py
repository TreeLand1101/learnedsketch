import re
import argparse
import numpy as np
import matplotlib.pyplot as plt
import os

def parse_log_file(file_path):
    # Parses the log file to extract total packet count and sorted flow packet counts
    with open(file_path, 'r') as f:
        lines = f.readlines()

    total_packets = 0
    flow_counts_sorted = []

    # Read total packet count and flow counts from the log file
    for line in lines:
        if line.startswith("TotalPackets:"):
            total_packets = int(re.search(r"TotalPackets:\s+(\d+)", line).group(1))
        if line.startswith("All Flows by Packet Count:"):
            # Extract flow packet counts from subsequent lines
            for flow_line in lines[lines.index(line) + 1:]:
                match = re.search(r"Packet Count:\s+(\d+)", flow_line)
                if match:
                    flow_counts_sorted.append(int(match.group(1)))
                else:
                    break 
            break 

    return total_packets, flow_counts_sorted

def calculate_heavy_hitter(total_packets, flow_counts_sorted, thresholds):
    results = []

    # For each threshold percentage, calculate the number of flows that exceed the threshold
    for threshold_percent in thresholds:
        threshold = total_packets * threshold_percent / 100
        num_flows = 0

        # Count the number of flows with packet count above the threshold
        for count in flow_counts_sorted:
            if count < threshold:
                break
            num_flows += 1
        
        results.append((threshold_percent, num_flows))
    
    return results

def plot_results(results, args):
    thresholds = [x[0] for x in results]
    num_flows = [x[1] for x in results]
    
    # Plot the results: threshold percentages vs number of heavy hitters
    plt.figure(figsize=(10, 6))
    plt.plot(thresholds, num_flows, marker='o')
    plt.xlabel('% of the Total Number of Packets')  
    plt.ylabel('Number of Flows')
    plt.title('Heavy Hitter Threshold vs Number of Flows')
    plt.grid(True)
    
    # Save the plot
    base_name = os.path.splitext(os.path.basename(args.log))[0]

    if not os.path.exists(args.save):
        os.makedirs(args.save)
    plt.savefig(os.path.join(args.save, f'{base_name}_HH_threshold_vs_number_of_flows.png'))
    plt.close()

def main():
    parser = argparse.ArgumentParser(description="Analyze heavy hitter threshold.")
    parser.add_argument('--log', type=str, required=True, help="Path to the log file")
    parser.add_argument('--begin', type=float, default=0.001, help="Start threshold percentage (default: 0.01)")
    parser.add_argument('--end', type=float, default=0.005, help="End threshold percentage (default: 0.05)")
    parser.add_argument('--interval', type=float, default=0.001, help="Interval between thresholds (default: 0.005)")
    parser.add_argument('--save', type=str, required=True, help='Directory to save the output plots.')

    args = parser.parse_args()

    # Parse the log file to get the total packet count and sorted flow packet counts
    total_packets, flow_counts_sorted = parse_log_file(args.log)

    # Create a range of threshold percentages based on input parameters
    num_intervals = int((args.end - args.begin) / args.interval) + 1
    thresholds = np.linspace(args.begin, args.end, num_intervals)

    # Calculate the number of flows above each threshold percentage
    results = calculate_heavy_hitter(total_packets, flow_counts_sorted, thresholds)

    # Plot the results
    plot_results(results, args)

if __name__ == '__main__':
    main()
