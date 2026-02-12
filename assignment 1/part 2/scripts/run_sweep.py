import subprocess
import os
import itertools
import multiprocessing
import argparse

# --- Configuration ---
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(script_dir, ".."))
# Note: gem5_bin path is specific to the cluster environment
gem5_bin = "/home/tishya/shivam/hpc/gem5/build/RISCV/gem5.opt"
cache_conf = os.path.join(project_root, "configs/cache_config.py")

# Binaries
simple_binary = os.path.join(project_root, "mergesort/mergesort_s")
chunked_binary = os.path.join(project_root, "mergesort/mergesort_c")

# Output
output_base_dir = os.path.join(project_root, "results/stats")

# Sweep Parameters
l1_cache_sizes = ["32kB", "64kB", "128kB"]
l2_cache_sizes = ["256kB", "512kB", "1024kB"]
l1_associativities = ["4", "8", "16"]
l2_associativities = ["4", "8", "16"]
algorithm_types = ["Simple", "Chunked"]

all_configs = list(itertools.product(l1_cache_sizes, l2_cache_sizes, l1_associativities, l2_associativities, algorithm_types))

def run_simulation(params, force=False):
    l1_sz, l2_sz, l1_assoc, l2_assoc, algo_type = params
    binary = simple_binary if algo_type == "Simple" else chunked_binary
    
    config_name = f"{algo_type}_L1_{l1_sz}_L2_{l2_sz}_A1_{l1_assoc}_A2_{l2_assoc}"
    sim_dir = os.path.join(output_base_dir, config_name)
    os.makedirs(sim_dir, exist_ok=True)
    
    stats_file = os.path.join(sim_dir, "stats.txt")
    if not force and os.path.exists(stats_file) and os.path.getsize(stats_file) > 1024:
        return
        
    cmd = [
        gem5_bin,
        "-d", sim_dir,
        cache_conf,
        f"--l1d_size={l1_sz}",
        f"--l2_size={l2_sz}",
        f"--l1_assoc={l1_assoc}",
        f"--l2_assoc={l2_assoc}",
        f"--binary={binary}"
    ]
    
    try:
        # Set working directory to mergesort for relative path consistency if needed
        work_dir = os.path.join(project_root, "mergesort")
        with open(os.path.join(sim_dir, "sim_out.txt"), "w") as out, \
             open(os.path.join(sim_dir, "sim_err.txt"), "w") as err:
            subprocess.run(cmd, stdout=out, stderr=err, cwd=work_dir)
    except Exception as e:
        print(f"Error running {config_name}: {e}")

def wrapper(args):
    return run_simulation(*args)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run full cache sweep for MergeSort")
    parser.add_argument("--force", action="store_true", help="Force re-running simulations")
    parser.add_argument("--threads", type=int, default=48, help="Number of parallel threads")
    args = parser.parse_args()
    
    os.makedirs(output_base_dir, exist_ok=True)
    
    print(f"Starting sweep of {len(all_configs)} configurations using {args.threads} threads...")
    
    pool_args = [(config, args.force) for config in all_configs]
    with multiprocessing.Pool(args.threads) as pool:
        pool.map(wrapper, pool_args)
        
    print("Sweep complete. Results stored in results/stats/")
