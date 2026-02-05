# Run this from gem5 folder
import subprocess
import re
import csv
import multiprocessing
import os
import itertools

# --- CONFIGURATION ---
GEM5_ROOT = "/home/tishya/shivam/hpc/gem5"

GEM5_EXEC = os.path.join(GEM5_ROOT, "build/RISCV/gem5.opt")
CONFIG_SCRIPT = "configs/cache_config.py"

BINARY_SIMPLE = "mergesort/mergesort_simple"
BINARY_CHUNKED = "mergesort/mergesort_chunked"

OUTPUT_DIR = "results/sweep"
CSV_FILE = "results/sweep/p2_sweep_results.csv"

# --- PARAMETERS TO SWEEP ---
l1_sizes = ["32kB", "64kB"] 
l1_assocs = ["4", "8"]
l2_sizes = ["256kB", "512kB", "1MB", "2MB"] 
l2_assocs = ["8"]

# Generate combinations
configs = list(itertools.product(l1_sizes, l1_assocs, l2_sizes, l2_assocs))

def run_simulation(args):
    config, binary_type = args
    l1_s, l1_a, l2_s, l2_a = config
    
    binary_path = BINARY_SIMPLE if binary_type == "Simple" else BINARY_CHUNKED
    
    # Unique ID
    run_id = f"{binary_type}_L1{l1_s}_L1A{l1_a}_L2{l2_s}_L2A{l2_a}"
    run_dir = os.path.join(OUTPUT_DIR, run_id)
    os.makedirs(run_dir, exist_ok=True)
    
    cmd = [
        GEM5_EXEC, "-d", run_dir, CONFIG_SCRIPT,
        f"--l1d_size={l1_s}",
        f"--l1_assoc={l1_a}",
        f"--l2_size={l2_s}",
        f"--l2_assoc={l2_a}",
        f"--binary={binary_path}"
    ]
    
    try:
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        # Parse stats
        stats_path = os.path.join(run_dir, "stats.txt")
        if not os.path.exists(stats_path):
            return [binary_type, *config, "Failed", 0, 0]

        with open(stats_path, "r") as f:
            content = f.read()
            # Extract simSeconds
            time_match = re.search(r"simSeconds\s+([0-9\.e\-]+)", content)
            time = time_match.group(1) if time_match else "N/A"
            
            # Extract IPC (Instructions Per Cycle)
            ipc_match = re.search(r"system\.cpu\.ipc\s+([0-9\.e\-]+)", content)
            ipc = ipc_match.group(1) if ipc_match else "0"
            
            # Extract L2 Miss Rate
            l2_miss = re.search(r"system\.l2cache\.overallMissRate::total\s+([0-9\.e\-]+)", content)
            l2_mr = l2_miss.group(1) if l2_miss else "0"
            
            return [binary_type, *config, time, ipc, l2_mr]

    except Exception as e:
        return [binary_type, *config, "Error", 0, 0]

if __name__ == "__main__":
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Create work items: (Config, "Simple") and (Config, "Chunked")
    work_items = []
    for c in configs:
        work_items.append((c, "Simple"))
        work_items.append((c, "Chunked"))

    num_workers = min(multiprocessing.cpu_count(), len(work_items))
    print(f"Starting Sweep with {num_workers} cores ({len(work_items)} total runs)...")
    
    with multiprocessing.Pool(num_workers) as pool:
        results = pool.map(run_simulation, work_items)
    
    # Save CSV
    with open(CSV_FILE, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Type", "L1_Size", "L1_Assoc", "L2_Size", "L2_Assoc", "Time", "IPC", "L2_MissRate"])
        writer.writerows(results)
        
    print(f"Sweep Complete! Data saved to {CSV_FILE}")