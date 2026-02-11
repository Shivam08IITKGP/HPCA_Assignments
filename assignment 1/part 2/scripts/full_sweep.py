import subprocess
import re
import csv
import multiprocessing
import os
import itertools
import argparse

base_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(base_dir, ".."))
gem5_installation = "/home/tishya/shivam/hpc/gem5"

gem5_bin = os.path.join(gem5_installation, "build/RISCV/gem5.opt")
cache_conf = os.path.join(project_root, "configs/cache_config.py")
simple_binary = os.path.join(project_root, "mergesort/mergesort_s")
chunked_binary = os.path.join(project_root, "mergesort/mergesort_c")
output_path = os.path.join(project_root, "results/full_sweep")
results_csv = os.path.join(output_path, "full_sweep_results.csv")

l1_cache_sizes = ["32kB", "64kB", "128kB"]
l2_cache_sizes = ["256kB", "512kB", "1024kB"]
l1_associativities = ["4", "8", "16"]
l2_associativities = ["4", "8", "16"]
algorithm_types = ["Simple", "Chunked"]

all_configs = list(itertools.product(l1_cache_sizes, l2_cache_sizes, l1_associativities, l2_associativities, algorithm_types))

def execute_benchmark(params, force=False, extract_only=False):
    l1_sz, l2_sz, l1_assoc, l2_assoc, algo_type = params
    binary_to_run = simple_binary if algo_type == "Simple" else chunked_binary
    
    config_name = f"{algo_type}_L1_{l1_sz}_L2_{l2_sz}_A1_{l1_assoc}_A2_{l2_assoc}"
    sim_dir = os.path.join(output_path, config_name)
    os.makedirs(sim_dir, exist_ok=True)
    
    stats_location = os.path.join(sim_dir, "stats.txt")
    
    if not extract_only:
        if force or not os.path.exists(stats_location):
            sim_cmd = [
                gem5_bin,
                "-d", sim_dir,
                cache_conf,
                f"--l1d_size={l1_sz}",
                f"--l2_size={l2_sz}", 
                f"--l1_assoc={l1_assoc}",
                f"--l2_assoc={l2_assoc}",
                f"--binary={binary_to_run}"
            ]
            try:
                work_dir = os.path.join(project_root, "mergesort")
                with open(os.path.join(sim_dir, "sim_out.txt"), "w") as out, \
                     open(os.path.join(sim_dir, "sim_err.txt"), "w") as err:
                    subprocess.run(sim_cmd, stdout=out, stderr=err, cwd=work_dir)
            except Exception as e:
                print(f"Error running {config_name}: {e}")

    try:
        if not os.path.exists(stats_location):
            return [*params, "Failed", 0, 0, 0, 0]

        with open(stats_location, "r") as f:
            stat_text = f.read()
            time_pattern = re.search(r"simSeconds\s+([0-9\.e\-]+)", stat_text)
            exec_time = time_pattern.group(1) if time_pattern else "N/A"
            
            ticks_pattern = re.search(r"simTicks\s+([0-9]+)", stat_text)
            sim_ticks = ticks_pattern.group(1) if ticks_pattern else "0"
            
            l1_miss_pattern = re.search(r"system\.cpu\.dcache\.overallMissRate::total\s+([0-9\.e\-]+)", stat_text)
            l2_miss_pattern = re.search(r"system\.l2cache\.overallMissRate::total\s+([0-9\.e\-]+)", stat_text)
            
            l1_miss_val = l1_miss_pattern.group(1) if l1_miss_pattern else "0"
            l2_miss_val = l2_miss_pattern.group(1) if l2_miss_pattern else "0"
            
            ipc_pattern = re.search(r"system\.cpu\.ipc\s+([0-9\.e\-]+)", stat_text)
            ipc_val = ipc_pattern.group(1) if ipc_pattern else "0"
            
            return [*params, exec_time, sim_ticks, l1_miss_val, l2_miss_val, ipc_val]

    except Exception as e:
        return [*params, "Error", 0, 0, 0, 0]

def execute_wrapper(args):
    return execute_benchmark(*args)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run full cache sweep for MergeSort")
    parser.add_argument("--force", action="store_true", help="Force re-running simulations even if stats exist")
    parser.add_argument("--extract-only", action="store_true", help="Only extract stats from existing directories")
    args = parser.parse_args()

    os.makedirs(output_path, exist_ok=True)
    
    parallel_workers = 48
    mode_str = "Extraction only" if args.extract_only else ("Forcing re-simulation" if args.force else "Normal sweep (skipping existing)")
    print(f"Starting Full Sweep ({mode_str}) on {parallel_workers} cores ({len(all_configs)} total configs)...")
    
    # Prepare arguments for multiprocessing
    work_args = [(config, args.force, args.extract_only) for config in all_configs]
    
    with multiprocessing.Pool(parallel_workers) as pool:
        benchmark_results = pool.map(execute_wrapper, work_args)
    
    with open(results_csv, "w", newline="") as f:
        csv_writer = csv.writer(f)
        csv_writer.writerow(["L1_Size", "L2_Size", "L1_Assoc", "L2_Assoc", "Type", "Time", "Cycles", "L1_MissRate", "L2_MissRate", "IPC"])
        csv_writer.writerows(benchmark_results)
        
    print(f"Full Sweep Complete! Data saved to {results_csv}")