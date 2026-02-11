import subprocess
import re
import csv
import multiprocessing
import os

# get the folder where this script is
script_dir = os.path.dirname(os.path.abspath(__file__))

# path to gem5 stuff
gem5_path = "/home/tishya/shivam/hpc/gem5"

gem5_bin = os.path.join(gem5_path, "build/RISCV/gem5.opt")
config = os.path.join(script_dir, "../configs/cache_config.py")
bench = os.path.join(script_dir, "../benchmarks/matrix_multiply")
res_dir = os.path.join(script_dir, "../results")
out_csv = os.path.join(res_dir, "l1_sweep_results.csv")

# different L1 cache sizes to try
sizes = ["16kB", "32kB", "64kB", "128kB", "256kB"]

def run_one_sim(sz):
    # make output folder for this size
    out_dir = os.path.join(res_dir, "l1_" + sz)
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    # build the command to run gem5
    cmd = []
    cmd.append(gem5_bin)
    cmd.append("-d")
    cmd.append(out_dir)
    cmd.append(config)
    cmd.append("--l1d_size=" + sz)
    cmd.append("--binary=" + bench)

    print("-> Launching " + sz + " simulation...")

    try:
        result = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        # check for the stats file
        stats_path = os.path.join(out_dir, "stats.txt")

        found = os.path.exists(stats_path)
        if found == False:
            return [sz, "Error: No Stats", 0, 0]

        # read stats file
        f = open(stats_path, "r")
        data=f.read()
        f.close()

        # find sim time
        m = re.search(r"simSeconds\s+([0-9\.e\-]+)", data)
        if m:
            sim_time=m.group(1)
        else:
            sim_time="N/A"

        # find hits
        m2 = re.search(r"system\.cpu\.dcache\.overallHits::total\s+(\d+)", data)
        if m2:
            hits= m2.group(1)
        else:
            hits="0"

        # find misses
        m3 = re.search(r"system\.cpu\.dcache\.overallMisses::total\s+(\d+)", data)
        if m3:
            misses=m3.group(1)
        else:
            misses = "0"

        row = [sz, sim_time, hits, misses]
        return row

    except Exception as e:
        err_msg =str(e)
        return [sz, "Error: " + err_msg, 0, 0]

if __name__ == "__main__":
    if not os.path.exists(res_dir):
        os.makedirs(res_dir)

    num_cores=multiprocessing.cpu_count()
    num_workers=min(num_cores, len(sizes))
    print("Starting parallel sweep on " + str(num_workers) + " cores...")

    pool =multiprocessing.Pool(num_workers)
    results= pool.map(run_one_sim, sizes)
    pool.close()
    pool.join()

    # write results to csv
    f =open(out_csv, "w", newline="")
    writer =csv.writer(f)
    header =["L1_Size", "Execution_Time", "Hits", "Misses"]
    writer.writerow(header)
    for r in results:
        writer.writerow(r)
    f.close()

    print("")
    print("Sweep Complete! Data saved to:")
    print(out_csv)