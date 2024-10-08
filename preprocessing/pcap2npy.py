import numpy as np
from scapy.all import PcapReader
from scapy.layers.inet import IP, TCP, UDP, ICMP
import argparse
import os
import logging
from tqdm import tqdm

def setup_logger():
    logger = logging.getLogger('pcap2npy_logger')
    logger.setLevel(logging.INFO)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    formatter = logging.Formatter('%(message)s')
    console_handler.setFormatter(formatter)

    logger.addHandler(console_handler)

    return logger

def process_packets(pcap_file, logger):
    source_ips = []
    destination_ips = []
    source_ports = []
    destination_ports = []
    protocol_types = []
    flows = {}
    timestamps = []

    with PcapReader(pcap_file) as pcap_reader:
        for packet in tqdm(pcap_reader, desc="Processing packets", unit=" pkt"):
            if IP in packet:
                ip_layer = packet[IP]
                src_ip = ip_layer.src.split('.')
                dst_ip = ip_layer.dst.split('.')

                if TCP in packet:
                    sport = packet[TCP].sport
                    dport = packet[TCP].dport
                    protocol = 6  # TCP protocol number
                elif UDP in packet:
                    sport = packet[UDP].sport
                    dport = packet[UDP].dport
                    protocol = 17  # UDP protocol number
                elif ICMP in packet:
                    sport = 0  # ICMP doesn't have ports
                    dport = 0
                    protocol = 1  # ICMP protocol number
                else:
                    sport = 0
                    dport = 0
                    protocol = ip_layer.proto  # Other protocols

                flow_key = (ip_layer.src, ip_layer.dst, sport, dport, protocol)

                if flow_key in flows:
                    flows[flow_key] += 1
                else:
                    flows[flow_key] = 1
                    source_ips.append([float(octet) for octet in src_ip])
                    destination_ips.append([float(octet) for octet in dst_ip])
                    source_ports.append(float(sport))
                    destination_ports.append(float(dport))
                    protocol_types.append(float(protocol))
            timestamps.append(packet.time) 

    logger.info(f"Total flows captured: {len(flows)}")
    return source_ips, destination_ips, source_ports, destination_ports, protocol_types, flows, timestamps

def process_pcap_to_npy(pcap_file, npy_file, log_file, logger):
    logger.info(f"Starting processing for pcap file: {pcap_file}")
    source_ips, destination_ips, source_ports, destination_ports, protocol_types, flows, timestamps = process_packets(pcap_file, logger)

    source_ips = np.array(source_ips)
    destination_ips = np.array(destination_ips)
    source_ports = np.array(source_ports)
    destination_ports = np.array(destination_ports)
    protocol_types = np.array(protocol_types)
    packet_counts = np.array(list(flows.values()))

    x_data = np.hstack([source_ips, destination_ips, source_ports[:, None], destination_ports[:, None], protocol_types[:, None]])

    data = {
        'x': x_data,
        'y': packet_counts,
        'note': pcap_file
    }

    # Now pass all the required arguments to log_analysis
    log_analysis(sorted(flows.items(), key=lambda x: x[1], reverse=True), timestamps, log_file, logger)

    np.save(npy_file, data)
    logger.info(f"Data saved to {npy_file}")


def log_analysis(sorted_flows, timestamps, log_file, logger):
    duration = max(timestamps) - min(timestamps)
    total_packets = sum(count for _, count in sorted_flows)
    unique_flows = len(sorted_flows)
    min_packet_count = min(count for _, count in sorted_flows)
    max_packet_count = max(count for _, count in sorted_flows)

    if duration > 0: 
        packets_per_second = total_packets / duration  
    else:
        packets_per_second = 0

    # Log these metrics only once
    log_message = (
        f"TotalTime: {duration:.2f} seconds\n"
        f"TotalPackets: {total_packets}\n"
        f"UniqueFlows: {unique_flows}\n"
        f"MinPacketCount: {min_packet_count:.2f}\n"
        f"MaxPacketCount: {max_packet_count:.2f}\n"
        f"PacketsPerSecond: {packets_per_second:.2f} pps"
    )

    # Log to console and file
    logger.info(log_message)

    # Write the detailed analysis to the log file only, including all flows
    with open(log_file, 'a') as f:  # 'a' mode to append
        f.write(log_message + '\n\n')
        f.write("All Flows by Packet Count:\n")
        for idx, (flow, count) in enumerate(sorted_flows, start=1):
            f.write(f"{idx}. Flow: {flow} -> Packet Count: {count}\n")



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process a pcap file and save the data to a npy file.')
    parser.add_argument('--pcap', type=str, required=True, help='The input pcap file')
    parser.add_argument('--npy', type=str, required=True, help='The output npy file')
    parser.add_argument('--log', type=str, required=True, help='Log file path')

    args = parser.parse_args()

    log_dir = os.path.dirname(args.log)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir)

    logger = setup_logger()

    process_pcap_to_npy(args.pcap, args.npy, args.log, logger)
