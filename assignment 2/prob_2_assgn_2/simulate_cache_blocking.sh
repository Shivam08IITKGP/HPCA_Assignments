#!/usr/bin/bash

LOG=simulation_cache_blocking.log

# Remove old log file
rm -f $LOG

# Pin all experiments to core 2 (isolated from core 0 used by OS)
CORE=2

echo "# Pinning experiments to CPU core $CORE" >> $LOG
echo "" >> $LOG

# Array of matrix sizes
SIZES=(1024 2048 4096 8192)

for N in "${SIZES[@]}"; do
    echo "# Results for N = $N, B = 32" >> $LOG
    echo "" >> $LOG

    # Compile naive version
    gcc -O0 -o naive_${N}_O0 matmul_naive_${N}.c >> $LOG 2>&1
    gcc -O3 -march=native -fopt-info-vec -o naive_${N}_O3 matmul_naive_${N}.c >> $LOG 2>&1

    # Compile blocking version
    gcc -O0 -o blocking_${N}_O0 matmul_blocking_${N}.c >> $LOG 2>&1
    gcc -O3 -march=native -fopt-info-vec -o blocking_${N}_O3 matmul_blocking_${N}.c >> $LOG 2>&1

    # Execute and generate results (pinned to core $CORE via taskset)
    echo "# Naive results (-O0)" >> $LOG
    taskset -c $CORE perf stat -e cache-references,cache-misses ./naive_${N}_O0 >> $LOG 2>&1

    echo "# Naive results (-O3)" >> $LOG
    taskset -c $CORE perf stat -e cache-references,cache-misses ./naive_${N}_O3 >> $LOG 2>&1

    echo "# Blocking results (-O0)" >> $LOG
    taskset -c $CORE perf stat -e cache-references,cache-misses ./blocking_${N}_O0 >> $LOG 2>&1

    echo "# Blocking results (-O3)" >> $LOG
    taskset -c $CORE perf stat -e cache-references,cache-misses ./blocking_${N}_O3 >> $LOG 2>&1

    echo "" >> $LOG
done

echo -e "\nSimulation results present in $LOG\n"
exit