# Assignment 1: Problem 1 - Cache Hierarchy Optimization

**Authors:** Rahate Tanishka Shivendra (22CS30043), Shivam Choudhury (22CS10072)

This directory contains the gem5 simulation scripts and results for Problem 1, which investigates the impact of cache parameters on a matrix multiplication workload across multiple matrix sizes (64x64, 128x128, 256x256).

## Directory Structure
```
part 1/
├── benchmarks/
│   ├── matrix_multiply.c         # Single source file with #ifndef MATRIX_SIZE
│   └── matrix_multiply           # Compiled RISC-V binary (128x128 default)
├── configs/
│   └── cache_config.py           # gem5 cache hierarchy configuration
├── scripts/
│   ├── cache_sweep.py            # Single-parameter L1 sweep (Part 2)
│   ├── full_sweep.py             # Unified sweep script for all matrix sizes
│   └── analyze.py                # Combined extraction and analysis
├── results/
│   ├── full_sweep/               # 128x128 results
│   ├── full_sweep_64/            # 64x64 results
│   ├── full_sweep_256/           # 256x256 results
│   └── analysis_all/             # Comparative plots
└── report.tex                     # LaTeX report
```

## Prerequisites
- gem5 simulator with RISC-V support: `/home/tishya/shivam/hpc/gem5/build/RISCV/gem5.opt`
- RISC-V cross-compiler: `/home/tishya/shivam/hpc/gem5/riscv-toolchain/riscv/bin/`
- Python 3 with pandas, matplotlib, seaborn

## How to Reproduce Results

### 1. Environment Setup & Basic Test (Part 1)
Run a single simulation with default parameters to verify setup:
```bash
/home/tishya/shivam/hpc/gem5/build/RISCV/gem5.opt configs/cache_config.py \
    --l1d_size=16kB --l2_size=256kB \
    --l1_assoc=4 --l2_assoc=8 \
    --binary=benchmarks/matrix_multiply
```
Check `m5out/stats.txt` for cache statistics.

### 2. Single Parameter Sweep (Part 2)
Vary L1 Data Cache Size while keeping other parameters fixed:
```bash
python3 scripts/cache_sweep.py
```
**Parameters swept:** L1D sizes [16kB, 32kB, 64kB, 128kB, 256kB]  
**Output:** `results/l1_sweep_results.csv`

### 3. Full Multi-Parameter Sweep (Part 3)
Run comprehensive sweeps for all three matrix sizes using the unified script:

**For 128x128 matrix (default):**
```bash
python3 scripts/full_sweep.py --size 128
```
*Note: `--size 128` is the default if no argument is provided.*

**For 64x64 matrix:**
```bash
python3 scripts/full_sweep.py --size 64
```
*Note: This script automatically compiles the benchmark for the specified size.*

**For 256x256 matrix:**
```bash
python3 scripts/full_sweep.py --size 256
```

**Parameters swept:**
- L1 Sizes: [16kB, 32kB, 64kB]
- L2 Sizes: [128kB, 256kB, 512kB]
- L1 Associativity: [2, 4, 8]
- L2 Associativity: [4, 8, 16]

**Note:** Each sweep runs in parallel using all available CPU cores (48 cores detected).

### 4. Analysis & Visualization (Part 4)
Generate comprehensive plots and summary statistics:
```bash
python3 scripts/analyze.py
```

**Generated plots** (saved to `results/analysis_all/`):
1. `l1_size_vs_time.png` - L1 cache size impact
2. `l2_size_vs_time.png` - L2 cache size impact
3. `l1_hitrate_vs_l1_size.png` - L1 hit rate vs L1 size
4. `l1_hitrate_vs_l1_assoc.png` - L1 hit rate vs L1 associativity
5. `l2_hitrate_vs_l2_size.png` - L2 hit rate vs L2 size
6. `l2_hitrate_vs_l2_assoc.png` - L2 hit rate vs L2 associativity
7. `heatmap_time_128x128.png` - Performance heatmap
8. `simticks_vs_l2_size.png` - Simulation ticks vs L2 size
9. `hostseconds_vs_l2_size.png` - Wall-clock time vs L2 size
10. `summary_statistics.csv` - Statistical summary of all metrics

**Console output:**
- Top 3 fastest configurations for each matrix size
- Summary statistics (mean, median, std dev, min, max) for all metrics

## Key Configuration Parameters
- **Clock Frequency**: 1 GHz
- **Memory Mode**: Timing simulation
- **Memory Range**: 512 MB
- **CPU Model**: RiscvTimingSimpleCPU
- **Cache Line Size**: 64 bytes (default)
- **L1I Cache**: 16 kB (fixed)
- **L1D Cache**: Configurable (16 kB - 64 kB)
- **L2 Cache**: Unified, configurable (128 kB - 512 kB)

## Results Summary
Best configurations by matrix size:
- **64x64**: L1=64kB, L2=256kB, Assoc=2,8 → 0.0106s
- **128x128**: L1=64kB, L2=512kB, Assoc=4,8 → 0.0803s
- **256x256**: L1=32kB, L2=512kB, Assoc=8,16 → 1.0176s

## Compiling Benchmarks (if needed)

**Default (128x128 matrix):**
```bash
export PATH=/home/tishya/shivam/hpc/gem5/riscv-toolchain/riscv/bin:$PATH
riscv64-unknown-linux-gnu-gcc -O2 -static benchmarks/matrix_multiply.c \
    -o benchmarks/matrix_multiply
```

**For different matrix sizes:**
```bash
# 64x64 matrix
riscv64-unknown-linux-gnu-gcc -O2 -static -DMATRIX_SIZE=64 \
    benchmarks/matrix_multiply.c -o benchmarks/matrix_multiply_64x64

# 256x256 matrix
riscv64-unknown-linux-gnu-gcc -O2 -static -DMATRIX_SIZE=256 \
    benchmarks/matrix_multiply.c -o benchmarks/matrix_multiply_256x256
```

**Source code structure:**
```c
#ifndef MATRIX_SIZE
#define MATRIX_SIZE 128  /* Default: 128. Override with -DMATRIX_SIZE=64 */
#endif
```
