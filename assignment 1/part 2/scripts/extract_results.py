import os
import re
import csv

def extract_stats(stats_file):
    if not os.path.exists(stats_file) or os.path.getsize(stats_file) < 1024:
        return None
    try:
        with open(stats_file, "r") as f:
            stat_text = f.read()
            time_pattern = re.search(r"simSeconds\s+([0-9\.e\-]+)", stat_text)
            exec_time = time_pattern.group(1) if time_pattern else "N/A"
            
            ticks_pattern = re.search(r"simTicks\s+([0-9]+)", stat_text)
            sim_ticks = ticks_pattern.group(1) if ticks_pattern else "0"
            
            # Extract IPC
            ipc_pattern = re.search(r"system\.cpu\.ipc\s+([0-9\.e\-]+)", stat_text)
            ipc_val = ipc_pattern.group(1) if ipc_pattern else "0"

            # Extract miss rates (handling both naming conventions)
            l1_miss_pattern = re.search(r"system\.(?:cpu\.dcache|l1d)\.overallMissRate::total\s+([0-9\.e\-]+)", stat_text)
            l2_miss_pattern = re.search(r"system\.(?:l2cache|l2)\.overallMissRate::total\s+([0-9\.e\-]+)", stat_text)
            
            l1_miss_val = l1_miss_pattern.group(1) if l1_miss_pattern else "0"
            l2_miss_val = l2_miss_pattern.group(1) if l2_miss_pattern else "0"
            
            return [exec_time, sim_ticks, l1_miss_val, l2_miss_val, ipc_val]
    except Exception:
        return None

def process():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../results/stats"))
    output_csv = os.path.abspath(os.path.join(os.path.dirname(__file__), "../results/results.csv"))
    
    headers = ["L1_Size", "L2_Size", "L1_Assoc", "L2_Assoc", "Type", "Time", "Cycles", "L1_MissRate", "L2_MissRate", "IPC"]
    all_results = []

    print(f"Scanning: {base_dir}")
    if not os.path.exists(base_dir):
        print("Error: Statistics directory not found.")
        return

    for config_dir in sorted(os.listdir(base_dir)):
        config_path = os.path.join(base_dir, config_dir)
        if not os.path.isdir(config_path):
            continue
            
        stats_file = os.path.join(config_path, "stats.txt")
        stats = extract_stats(stats_file)
        
        if stats:
            # Parse config from dirname: Algorithm_L1_X_L2_Y_A1_Z_A2_W
            parts = config_dir.split("_")
            try:
                algo = parts[0]
                l1_size = parts[2]
                l2_size = parts[4]
                l1_assoc = parts[6]
                l2_assoc = parts[8]
                all_results.append([l1_size, l2_size, l1_assoc, l2_assoc, algo] + stats)
            except IndexError:
                print(f"Skipping malformed directory: {config_dir}")

    with open(output_csv, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(all_results)
    
    print(f"\nProcessing Complete: {len(all_results)} configurations extracted.")
    print(f"Saved to: {output_csv}")

if __name__ == "__main__":
    process()
