import numpy as np
from scapy.all import PcapReader
from scapy.layers.inet import IP, TCP, UDP
import argparse
import os
from tqdm import tqdm

def process_packets(pcap_file):
    # Initialize lists to hold our data
    source_ips = []
    destination_ips = []
    source_ports = []
    destination_ports = []
    protocol_types = []
    flows = {}
    
    # Open the pcap file
    with PcapReader(pcap_file) as pcap_reader:
        for packet in tqdm(pcap_reader, desc="Processing packets", unit=" pkt"):
            if IP in packet:
                ip_layer = packet[IP]
                src_ip = ip_layer.src.split('.')
                dst_ip = ip_layer.dst.split('.')
                
                # Handle TCP/UDP ports and protocol type
                if TCP in packet:
                    sport = packet[TCP].sport
                    dport = packet[TCP].dport
                    protocol = 6  # TCP protocol number
                elif UDP in packet:
                    sport = packet[UDP].sport
                    dport = packet[UDP].dport
                    protocol = 17  # UDP protocol number
                else:
                    sport = 0
                    dport = 0
                    protocol = ip_layer.proto
                
                # Create a flow key
                flow_key = (ip_layer.src, ip_layer.dst, sport, dport, protocol)
                
                # If flow already exists, increment the packet count
                if flow_key in flows:
                    flows[flow_key] += 1
                else:
                    flows[flow_key] = 1
                    source_ips.append([float(octet) for octet in src_ip])
                    destination_ips.append([float(octet) for octet in dst_ip])
                    source_ports.append(float(sport))
                    destination_ports.append(float(dport))
                    protocol_types.append(float(protocol))
    
    return source_ips, destination_ips, source_ports, destination_ports, protocol_types, flows

def process_pcap_to_npy(pcap_file):
    # Process all packets
    source_ips, destination_ips, source_ports, destination_ports, protocol_types, flows = process_packets(pcap_file)
    
    # Convert lists to numpy arrays
    source_ips = np.array(source_ips)
    destination_ips = np.array(destination_ips)
    source_ports = np.array(source_ports)
    destination_ports = np.array(destination_ports)
    protocol_types = np.array(protocol_types)
    packet_counts = np.array(list(flows.values()))
    
    # Combine all data into a single numpy array
    x_data = np.hstack([source_ips, destination_ips, source_ports[:, None], destination_ports[:, None], protocol_types[:, None]])
    
    # Create the final data dictionary
    data = {
        'x': x_data,
        'y': packet_counts,
        'note': pcap_file
    }
    
    # Generate the output file name
    npy_file = os.path.splitext(pcap_file)[0] + '.npy'
    
    # Save the data to a npy file
    np.save(npy_file, data)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process a pcap file and save the data to a npy file.')
    parser.add_argument('pcap_file', type=str, help='The input pcap file')

    args = parser.parse_args()
    process_pcap_to_npy(args.pcap_file)
