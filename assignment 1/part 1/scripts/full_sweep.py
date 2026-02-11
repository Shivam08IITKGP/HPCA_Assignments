import subprocess
import re
import csv
import multiprocessing
import os
import itertools
import argparse

gem5_installation = "/home/tishya/shivam/hpc/gem5"
project_base = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

gem5_bin = os.path.join(gem5_installation, "build/RISCV/gem5.opt")
cache_conf = os.path.join(project_base, "configs/cache_config.py")

def build_benchmark(matrix_size, test_binary):
    src_file = os.path.join(project_base, "benchmarks/matrix_multiply.c")
    
    build_cmd = [
        "/home/tishya/shivam/hpc/gem5/riscv-toolchain/riscv/bin/riscv64-unknown-linux-gnu-gcc",
        "-O2", "-static", f"-DMATRIX_SIZE={matrix_size}",
        src_file, "-o", test_binary
    ]
    
    try:
        subprocess.run(build_cmd, check=True)
        print(f"Compiled benchmark for {matrix_size}x{matrix_size} matrix: {test_binary}")
    except subprocess.CalledProcessError:
        print(f"Failed to compile benchmark for {matrix_size}x{matrix_size} matrix")
        exit(1)

def execute_config(params):
    l1_sz, l2_sz, l1_assoc, l2_assoc, test_binary, sweep_output = params
    
    config_id = f"L1_{l1_sz}_L2_{l2_sz}_A1_{l1_assoc}_A2_{l2_assoc}"
    sim_output = os.path.join(sweep_output, config_id)
    os.makedirs(sim_output, exist_ok=True)
    
    sim_command = [
        gem5_bin,
        "-d", sim_output,
        cache_conf,
        f"--l1d_size={l1_sz}",
        f"--l2_size={l2_sz}", 
        f"--l1_assoc={l1_assoc}",
        f"--l2_assoc={l2_assoc}",
        f"--binary={test_binary}"
    ]
    
    try:
        subprocess.run(sim_command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        stat_file = os.path.join(sim_output, "stats.txt")
        if not os.path.exists(stat_file):
            return [l1_sz, l2_sz, l1_assoc, l2_assoc, "Failed", 0, 0]

        with open(stat_file, "r") as f:
            stat_content = f.read()
            time_result = re.search(r"simSeconds\s+([0-9\.e\-]+)", stat_content)
            exec_time = time_result.group(1) if time_result else "N/A"
            
            l1_miss_pattern = re.search(r"system\.cpu\.dcache\.overallMissRate::total\s+([0-9\.e\-]+)", stat_content)
            l2_miss_pattern = re.search(r"system\.l2cache\.overallMissRate::total\s+([0-9\.e\-]+)", stat_content)
            
            l1_rate = l1_miss_pattern.group(1) if l1_miss_pattern else "0"
            l2_rate = l2_miss_pattern.group(1) if l2_miss_pattern else "0"
            
            return [l1_sz, l2_sz, l1_assoc, l2_assoc, exec_time, l1_rate, l2_rate]

    except Exception as e:
        return [l1_sz, l2_sz, l1_assoc, l2_assoc, "Error", 0, 0]

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run full sweep for matrix multiplication benchmark.")
    parser.add_argument("--size", type=int, choices=[64, 128, 256], default=128, help="Matrix size (N for NxN matrix). Default: 128.")
    args = parser.parse_args()

    # Dynamic paths based on size
    size_suffix = f"_{args.size}x{args.size}" if args.size != 128 else ""
    binary_name = f"matrix_multiply{size_suffix}"
    test_binary = os.path.join(project_base, f"benchmarks/{binary_name}")
    
    output_dir_name = f"full_sweep_{args.size}" if args.size != 128 else "full_sweep"
    sweep_output = os.path.join(project_base, f"results/{output_dir_name}")
    
    results_file_name = f"full_sweep_results_{args.size}.csv" if args.size != 128 else "full_sweep_results.csv"
    results_file = os.path.join(sweep_output, results_file_name)

    # Build the benchmark first
    build_benchmark(args.size, test_binary)
    
    os.makedirs(sweep_output, exist_ok=True)
    
    l1_cache_sizes = ["16kB", "32kB", "64kB"]
    l2_cache_sizes = ["128kB", "256kB", "512kB"]
    l1_associativities = ["2", "4", "8"]
    l2_associativities = ["4", "8", "16"]
    
    base_configs = list(itertools.product(l1_cache_sizes, l2_cache_sizes, l1_associativities, l2_associativities))
    all_configurations = [(*cfg, test_binary, sweep_output) for cfg in base_configs]
    
    parallel_workers = min(multiprocessing.cpu_count(), len(all_configurations))
    print(f"Starting Full Sweep for {args.size}x{args.size} on {parallel_workers} cores ({len(all_configurations)} total configs)...")
    
    with multiprocessing.Pool(parallel_workers) as pool:
        config_results = pool.map(execute_config, all_configurations)
    
    with open(results_file, "w", newline="") as f:
        file_writer = csv.writer(f)
        file_writer.writerow(["L1_Size", "L2_Size", "L1_Assoc", "L2_Assoc", "Time", "L1_MissRate", "L2_MissRate"])
        file_writer.writerows(config_results)
        
    print(f"Full Sweep Complete! Data saved to {results_file}")