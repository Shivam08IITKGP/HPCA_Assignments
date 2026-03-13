#!/usr/bin/bash

LOG=simulation_loop_interchange_core_blocked.log

# Remove old log file
rm -f $LOG

# Pin all experiments to core 2 (isolated from core 0 used by OS)
CORE=2

echo "# Pinning experiments to CPU core $CORE" >> $LOG
echo "" >> $LOG

# Compile and run for each value of N
for N in 1024 2048 4096 8192; do

    echo "# Results for N = $N" >> $LOG

    # Compile the files
    gcc -O0 -o cmajor_${N}_O0 column_major_${N}.c >> $LOG 2>&1
    gcc -O0 -o rmajor_${N}_O0 row_major_${N}.c >> $LOG 2>&1

    gcc -O3 -march=native -fopt-info-vec -o cmajor_${N}_O3 column_major_${N}.c >> $LOG 2>&1
    gcc -O3 -march=native -fopt-info-vec -o rmajor_${N}_O3 row_major_${N}.c >> $LOG 2>&1

    # Execute and generate results (pinned to core $CORE via taskset)
    echo "# Column major results (-O0)" >> $LOG
    taskset -c $CORE perf stat -e cache-references,cache-misses ./cmajor_${N}_O0 >> $LOG 2>&1

    echo "# Column major results (-O3)" >> $LOG
    taskset -c $CORE perf stat -e cache-references,cache-misses ./cmajor_${N}_O3 >> $LOG 2>&1

    echo "# Row major results (-O0)" >> $LOG
    taskset -c $CORE perf stat -e cache-references,cache-misses ./rmajor_${N}_O0 >> $LOG 2>&1

    echo "# Row major results (-O3)" >> $LOG
    taskset -c $CORE perf stat -e cache-references,cache-misses ./rmajor_${N}_O3 >> $LOG 2>&1

done

echo -e "\nSimulation results present in $LOG\n"
exit