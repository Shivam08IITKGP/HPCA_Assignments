import subprocess
import re
import csv
import multiprocessing
import os
import itertools

# --- CONFIGURATION ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ASSIGNMENT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))
GEM5_ROOT = "/home/tishya/shivam/hpc/gem5"

GEM5_EXEC = os.path.join(GEM5_ROOT, "build/RISCV/gem5.opt")
CONFIG_SCRIPT = os.path.join(ASSIGNMENT_ROOT, "configs/cache_config.py")
BINARY_SIMPLE = os.path.join(ASSIGNMENT_ROOT, "mergesort/mergesort_s")
BINARY_CHUNKED = os.path.join(ASSIGNMENT_ROOT, "mergesort/mergesort_c")
OUTPUT_DIR = os.path.join(ASSIGNMENT_ROOT, "results/full_sweep")
CSV_FILE = os.path.join(OUTPUT_DIR, "full_sweep_results.csv")

# --- PARAMETERS TO SWEEP ---
l1_sizes = ["32kB", "64kB", "128kB"]
l2_sizes = ["256kB", "512kB", "1024kB"]
l1_assocs = ["4", "8", "16"]
l2_assocs = ["4", "8", "16"]
types = ["Simple", "Chunked"]

# Generate all combinations (Cartesian product)
configs = list(itertools.product(l1_sizes, l2_sizes, l1_assocs, l2_assocs, types))

def run_simulation(config):
    l1_size, l2_size, l1_assoc, l2_assoc, run_type = config
    binary_path = BINARY_SIMPLE if run_type == "Simple" else BINARY_CHUNKED
    
    # Create unique ID for this config
    run_id = f"{run_type}_L1_{l1_size}_L2_{l2_size}_A1_{l1_assoc}_A2_{l2_assoc}"
    run_dir = os.path.join(OUTPUT_DIR, run_id)
    os.makedirs(run_dir, exist_ok=True)
    
    cmd = [
        GEM5_EXEC,
        "-d", run_dir,
        CONFIG_SCRIPT,
        f"--l1d_size={l1_size}",
        f"--l2_size={l2_size}", 
        f"--l1_assoc={l1_assoc}",
        f"--l2_assoc={l2_assoc}",
        f"--binary={binary_path}"
    ]
    
    try:
        simulation_cwd = os.path.join(ASSIGNMENT_ROOT, "mergesort")
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, cwd=simulation_cwd)
        
        # Parse stats
        stats_path = os.path.join(run_dir, "stats.txt")
        if not os.path.exists(stats_path):
            return [*config, "Failed", 0, 0, 0]

        with open(stats_path, "r") as f:
            content = f.read()
            time_match = re.search(r"simSeconds\s+([0-9\.e\-]+)", content)
            sim_seconds = time_match.group(1) if time_match else "N/A"
            
            # Get Hit Rates (L1 and L2)
            l1_miss = re.search(r"system\.cpu\.dcache\.overallMissRate::total\s+([0-9\.e\-]+)", content)
            l2_miss = re.search(r"system\.l2cache\.overallMissRate::total\s+([0-9\.e\-]+)", content)
            
            l1_miss_rate = l1_miss.group(1) if l1_miss else "0"
            l2_miss_rate = l2_miss.group(1) if l2_miss else "0"
            
            # Get IPC
            ipc_match = re.search(r"system\.cpu\.ipc\s+([0-9\.e\-]+)", content)
            ipc = ipc_match.group(1) if ipc_match else "0"
            
            return [*config, sim_seconds, l1_miss_rate, l2_miss_rate, ipc]

    except Exception as e:
        return [*config, "Error", 0, 0, 0]

if __name__ == "__main__":
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Run in parallel
    num_workers = min(multiprocessing.cpu_count(), len(configs))
    print(f"Starting Full Sweep on {num_workers} cores ({len(configs)} total configs)...")
    
    with multiprocessing.Pool(num_workers) as pool:
        results = pool.map(run_simulation, configs)
    
    # Save Results
    with open(CSV_FILE, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["L1_Size", "L2_Size", "L1_Assoc", "L2_Assoc", "Type", "Time", "L1_MissRate", "L2_MissRate", "IPC"])
        writer.writerows(results)
        
    print(f"Full Sweep Complete! Data saved to {CSV_FILE}")