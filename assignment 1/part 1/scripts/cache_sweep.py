import subprocess
import re
import csv
import multiprocessing
import os

script_location = os.path.dirname(os.path.abspath(__file__))
gem5_base = "/home/tishya/shivam/hpc/gem5"

gem5_binary = os.path.join(gem5_base, "build/RISCV/gem5.opt")
config_file = os.path.join(script_location, "../configs/cache_config.py")
benchmark_binary = os.path.join(script_location, "../benchmarks/matrix_multiply")
results_base = os.path.join(script_location, "../results")
output_csv = os.path.join(results_base, "l1_sweep_results.csv")

cache_sizes = ["16kB", "32kB", "64kB", "128kB", "256kB"]

def execute_sim(cache_size):
    output_path = os.path.join(results_base, f"l1_{cache_size}")
    os.makedirs(output_path, exist_ok=True)
    
    command = [
        gem5_binary,
        "-d", output_path,
        config_file,
        f"--l1d_size={cache_size}",
        f"--binary={benchmark_binary}"
    ]
    
    print(f"-> Launching {cache_size} simulation...")
    
    try:
        subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        stats_file = os.path.join(output_path, "stats.txt")
        
        if not os.path.exists(stats_file):
            return [cache_size, "Error: No Stats", 0, 0]

        with open(stats_file, "r") as f:
            file_content = f.read()
            
            time_val = re.search(r"simSeconds\s+([0-9\.e\-]+)", file_content)
            execution_time = time_val.group(1) if time_val else "N/A"
            
            hit_pattern = re.search(r"system\.cpu\.dcache\.overallHits::total\s+(\d+)", file_content)
            total_hits = hit_pattern.group(1) if hit_pattern else "0"
            
            miss_pattern = re.search(r"system\.cpu\.dcache\.overallMisses::total\s+(\d+)", file_content)
            total_misses = miss_pattern.group(1) if miss_pattern else "0"
            
            return [cache_size, execution_time, total_hits, total_misses]

    except Exception as e:
        return [cache_size, f"Error: {str(e)}", 0, 0]

if __name__ == "__main__":
    os.makedirs(results_base, exist_ok=True)
    
    worker_count = min(multiprocessing.cpu_count(), len(cache_sizes))
    print(f"Starting parallel sweep on {worker_count} cores...")
    
    with multiprocessing.Pool(worker_count) as pool:
        sweep_results = pool.map(execute_sim, cache_sizes)
    
    with open(output_csv, "w", newline="") as f:
        csv_writer = csv.writer(f)
        csv_writer.writerow(["L1_Size", "Execution_Time", "Hits", "Misses"])
        csv_writer.writerows(sweep_results)
        
    print(f"\nSweep Complete! Data saved to:\n{output_csv}")