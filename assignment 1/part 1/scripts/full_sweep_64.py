import subprocess
import re
import csv
import multiprocessing
import os
import itertools

gem5_installation ="/home/tishya/shivam/hpc/gem5"
project_base =os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

gem5_bin =os.path.join(gem5_installation, "build/RISCV/gem5.opt")
cache_conf= os.path.join(project_base, "configs/cache_config.py")
test_binary=os.path.join(project_base, "benchmarks/matrix_multiply_64x64")
sweep_output=os.path.join(project_base, "results/full_sweep_64")
results_file=os.path.join(sweep_output, "full_sweep_results_64.csv")

def build_benchmark():
    src_file=os.path.join(project_base, "benchmarks/matrix_multiply.c")
    build_cmd=[
        "/home/tishya/shivam/hpc/gem5/riscv-toolchain/riscv/bin/riscv64-unknown-linux-gnu-gcc",
        "-O2", "-static", "-DMATRIX_SIZE=64",
        src_file, "-o", test_binary
    ]
    
    try:
        subprocess.run(build_cmd, check=True)
        print(f"Compiled benchmark for 64x64 matrix: {test_binary}")
    except subprocess.CalledProcessError:
        print(f"Failed to compile benchmark for 64x64 matrix")
        exit(1)

l1_cache_sizes=["16kB", "32kB", "64kB"]
l2_cache_sizes=["128kB", "256kB", "512kB"]
l1_associativities=["2", "4", "8"]
l2_associativities =["4", "8", "16"]

all_configurations =list(itertools.product(l1_cache_sizes, l2_cache_sizes, l1_associativities, l2_associativities))

def execute_config(params):
    l1_sz, l2_sz, l1_assoc, l2_assoc = params
    
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
            return [*params, "Failed", 0, 0]

        with open(stat_file, "r") as f:
            stat_content = f.read()
            time_result = re.search(r"simSeconds\s+([0-9\.e\-]+)", stat_content)
            exec_time = time_result.group(1) if time_result else "N/A"
            
            l1_miss_pattern = re.search(r"system\.cpu\.dcache\.overallMissRate::total\s+([0-9\.e\-]+)", stat_content)
            l2_miss_pattern = re.search(r"system\.l2cache\.overallMissRate::total\s+([0-9\.e\-]+)", stat_content)
            
            l1_rate = l1_miss_pattern.group(1) if l1_miss_pattern else "0"
            l2_rate = l2_miss_pattern.group(1) if l2_miss_pattern else "0"
            
            return [*params, exec_time, l1_rate, l2_rate]

    except Exception as e:
        return [*params, "Error", 0, 0]

if __name__ == "__main__":
    build_benchmark()
    
    os.makedirs(sweep_output, exist_ok=True)
    
    parallel_workers = min(multiprocessing.cpu_count(), len(all_configurations))
    print(f"Starting Full Sweep for 64x64 on {parallel_workers} cores ({len(all_configurations)} total configs)...")
    
    with multiprocessing.Pool(parallel_workers) as pool:
        config_results = pool.map(execute_config, all_configurations)
    
    with open(results_file, "w", newline="") as f:
        file_writer = csv.writer(f)
        file_writer.writerow(["L1_Size", "L2_Size", "L1_Assoc", "L2_Assoc", "Time", "L1_MissRate", "L2_MissRate"])
        file_writer.writerows(config_results)
        
    print(f"Full Sweep Complete! Data saved to {results_file}")
