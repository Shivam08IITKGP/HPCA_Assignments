# Assignment 1: Problem 2 - Gem5 MergeSort Cache Analysis

**Authors:** Rahate Tanishka Shivendra (22CS30043), Shivam Choudhury (22CS10072)

This directory contains the gem5 simulation scripts and results for Problem 2, which analyzes the cache performance of Simple vs. Chunked MergeSort implementations on a RISC-V architecture.

## Directory Structure
```
part 2/
├── configs/
│   └── cache_config.py           # gem5 cache hierarchy configuration
├── mergesort/
│   ├── mergesort_simple.c        # Standard recursive mergesort (provided)
│   ├── mergesort_s               # Simple variant binary
│   ├── mergesort_chunked.c       # Cache-optimized chunked mergesort (provided)
│   ├── mergesort_c               # Chunked variant binary
│   ├── simple-riscv_mergesort_simple.py   # gem5 config for simple
│   └── simple-riscv_mergesort_chunked.py  # gem5 config for chunked
├── scripts/
│   ├── full_sweep.py             # Full multi-parameter sweep for both variants
│   ├── plot.py                   # Generate all analysis plots
│   └── baseline_analysis.py      # Extract baseline comparison table
├── results/
│   ├── full_sweep/               # Full sweep results CSV
│   └── analysis_plots/           # Generated plots
└── report.tex                     # LaTeX report
```

## Prerequisites
- gem5 simulator with RISC-V support: `/home/tishya/shivam/hpc/gem5/build/RISCV/gem5.opt`
- RISC-V cross-compiler: `/home/tishya/shivam/hpc/gem5/riscv-toolchain/riscv/bin/`
- Python 3 with pandas, matplotlib, seaborn
- **Input data**: `random_numbers.bin` (10 MB random integers) - must be in parent directory

## Algorithm Comparison

### Simple MergeSort
- Standard recursive implementation
- Operates on entire 10 MB dataset in memory
- No explicit cache optimization
- Array size: 2,621,440 integers

### Chunked MergeSort
- Two-phase approach optimized for cache locality
- **Phase 1**: Sort 2 MB chunks independently (fits in L2 cache)
- **Phase 2**: Merge sorted chunks using 1 MB streaming buffers
- Chunk size: 524,288 integers per chunk

## How to Reproduce Results

### Part 1: Baseline Comparison

To extract and display the baseline performance comparison for the default cache configuration:  
**(L1D: 64KiB/8-way, L2: 512KiB/16-way)**

Run the unified analysis script:
```bash
python3 scripts/analyze_all.py
```

**Output:**
```
============================================================
PART 1: BASELINE CACHE PERFORMANCE COMPARISON
============================================================
                Execution Time (s)  Simulation Ticks  Instructions Per Cycle  L1 Data Miss Rate  L2 Miss Rate
Mergesort Type                                                                                               
Simple                    3.992447     3992447091000                0.299274           0.019771      0.680915
Chunked                   4.007310     4007310104000                0.300675           0.019184      0.669356
============================================================
```

### Part 2: Full Cache Optimization Sweep

Run the multi-parameter sweep for both mergesort variants. This script is now smart: it skips simulations if `stats.txt` already exists unless the `--force` flag is used.

```bash
# To extract results without re-running simulations:
python3 scripts/full_sweep.py --extract-only

# To force re-running all simulations:
python3 scripts/full_sweep.py --force
```

**Parameters swept** (162 total configurations):
- L1 Sizes: [32kB, 64kB, 128kB]
- L2 Sizes: [256kB, 512kB, 1024kB]
- L1 Associativity: [4, 8, 16]
- L2 Associativity: [4, 8, 16]
- Both Simple and Chunked variants

**Output:** `results/full_sweep/full_sweep_results.csv`

### Part 3: Analysis & Visualization

Generate all 8 required plots and summary statistics:

```bash
python3 scripts/analyze_all.py
```

**Generated plots** (saved to `results/analysis_plots/`):
1. `plot_miss_rate_comparison.png` - L2 miss rate comparison (bar chart)
2. `plot_time_impact.png` - L1 size impact on execution time (line chart)
3. `plot_ipc_efficiency.png` - CPU efficiency comparison (bar chart)
4. `plot_hitrate_l1.png` - L1 hit rate vs L1 size (line chart)
5. `plot_l2_missrate_vs_size.png` - L2 miss rate vs L2 size (line chart)
6. `plot_ipc_vs_l1d_size.png` - IPC vs L1D cache size (line chart)
7. `plot_l1d_hitrate_vs_assoc.png` - L1D hit rate vs associativity (line chart)
8. `plot_simple_vs_chunked_comparison.png` - Comprehensive 2×2 comparison grid


**Console output:**
- Top 3 configurations by IPC for Simple variant
- Top 3 configurations by IPC for Chunked variant

## Key Configuration Parameters
- **Clock Frequency**: 1 GHz
- **Memory**: DDR3_1600_8x8, 512 MiB
- **CPU Model**: RiscvTimingSimpleCPU
- **L1I Cache**: 32 KiB, 8-way (fixed)
- **L1D Cache**: Configurable (32-128 KiB)
- **L2 Cache**: Unified, configurable (256 KiB - 1 MiB)

## Results Summary

**Best IPC configurations:**
- **Simple**: L1=128kB/4-way, L2=1024kB/4-way → IPC=0.3067
- **Chunked**: L1=128kB/8-way, L2=1024kB/4-way → IPC=0.3068

**Key findings:**
- Chunked algorithm achieves 1.5% higher IPC on average
- Chunked reduces L2 miss rate by ~1.7%
- Performance is less sensitive to cache size for chunked variant
- Chunked can achieve similar performance with 50% smaller L2 cache

## Compiling Benchmarks (if needed)
```bash
export PATH=/home/tishya/shivam/hpc/gem5/riscv-toolchain/riscv/bin:$PATH

# Simple variant
riscv64-unknown-linux-gnu-gcc -O2 -static mergesort/mergesort_simple.c \
    -o mergesort/mergesort_s -march=rv64imafdc -mabi=lp64d

# Chunked variant
riscv64-unknown-linux-gnu-gcc -O2 -static mergesort/mergesort_chunked.c \
    -o mergesort/mergesort_c -march=rv64imafdc -mabi=lp64d
```
