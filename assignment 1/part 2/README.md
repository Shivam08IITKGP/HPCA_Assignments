# Assignment 1: Problem 2 - Gem5 MergeSort Cache Analysis

**Authors:** Rahate Tanishka Shivendra (22CS30044), Shivam Choudhury (22CS10072)

This directory contains the gem5 simulation scripts and results for Problem 2, which analyzes the cache performance of Simple vs. Chunked MergeSort implementations on a RISC-V architecture.

## Directory Structure
```
part 2/
├── configs/
│   └── cache_config.py           # Unified gem5 system configuration
├── mergesort/
│   ├── mergesort_simple.c        # Standard recursive mergesort
│   ├── mergesort_s               # Simple variant binary (static)
│   ├── mergesort_chunked.c       # Cache-optimized chunked mergesort
│   ├── mergesort_c               # Chunked variant binary (static)
│   ├── simple-riscv_mergesort_simple.py   # gem5 baseline for simple
│   ├── simple-riscv_mergesort_chunked.py  # gem5 baseline for chunked
│   └── (random_numbers.bin is generated at runtime)
├── scripts/
│   ├── run_sweep.py              # Run all 162 simulations
│   ├── extract_results.py        # Extract metrics from stats.txt to CSV
│   └── analyze.py                # Generate analysis plots & statistics
├── results/
│   ├── stats/                    # Raw gem5 statistics & configs (162 configs)
│   ├── plots/                    # Generated analysis plots
│   └── results.csv               # Extracted metrics
├── report.tex                    # Final LaTeX report
└── README.md                     # This file
```

## Prerequisites
- gem5 simulator with RISC-V support: `/home/tishya/shivam/hpc/gem5/build/RISCV/gem5.opt`
- RISC-V cross-compiler: `/home/tishya/shivam/hpc/gem5/riscv-toolchain/riscv/bin/`
- Python 3 with pandas, matplotlib, seaborn
- **Input data**: `random_numbers.bin` (10 MB random integers) - generated in-memory by benchmark

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
python3 scripts/analyze.py
```

**Output:**
```
============================================================
Algorithm          | Time (s) | Cycles (Ticks) | IPC    | L1 Miss % | L2 Miss %
-------------------|----------|----------------|--------|-----------|----------
Simple MergeSort   | 3.7673   | 3.77e12        | 0.3165 | 1.94%     | 68.08%
Chunked MergeSort  | 3.2451   | 3.25e12        | 0.3319 | 1.51%     | 53.67%
============================================================
```

### Part 2: Full Cache Optimization Sweep

To re-run all 162 configurations (Warning: This takes ~3-4 hours on a 48-core machine):

```bash
python3 scripts/run_sweep.py
```

To extract results from existing `results/stats/` directories without re-running:

```bash
python3 scripts/extract_results.py
```

**Parameters swept** (162 total configurations):
- L1 Sizes: [32kB, 64kB, 128kB]
- L2 Sizes: [256kB, 512kB, 1024kB]
- L1 Associativity: [4, 8, 16]
- L2 Associativity: [4, 8, 16]
- Both Simple and Chunked variants

**Output:** `results/full_sweep/full_sweep_results.csv`

### Part 3: Verification Sweep (Optional)

A focused subset of configurations to verify locality improvements:

```bash
python3 scripts/verify_locality.py
```

**Configurations tested:**
- L1=32kB/4-way, L2=512kB/4-way (both Simple & Chunked)
- L1=64kB/8-way, L2=1024kB/8-way (both Simple & Chunked)

**Output:** Results stored in `results/verification_sweep/` (4 configurations)

### Part 4: Analysis & Visualization

Generate all 8 required plots and summary statistics:

```bash
python3 scripts/analyze_all.py
```

**Generated plots** (saved to `results/analysis_plots/`):
1. `results/plots/plot_miss_rate_comparison.png` - L2 miss rate comparison
2. `results/plots/plot_time_impact.png` - L1 size impact on execution time
3. `results/plots/plot_ipc_efficiency.png` - CPU efficiency comparison
4. `results/plots/plot_hitrate_l1.png` - L1 hit rate vs L1 size
5. `results/plots/plot_l2_missrate_vs_size.png` - L2 miss rate vs L2 size
6. `results/plots/plot_ipc_vs_l1d_size.png` - IPC vs L1D cache size
7. `results/plots/plot_l1d_hitrate_vs_assoc.png` - L1D hit rate vs associativity
8. `results/plots/plot_simple_vs_chunked_comparison.png` - Comprehensive 2×2 comparison grid


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
- **Simple**: L1=128kB/4-way, L2=1024kB/4-way → IPC=0.3248
- **Chunked**: L1=128kB/1024kB/16-way → IPC=0.3403

**Key findings:**
- Chunked algorithm achieves **~4.8% higher IPC** on average at baseline.
- Chunked is **~13.9% faster** in execution time at baseline.
- Chunked reduces L2 miss rate significantly by using selection-based n-way merge.
- The use of in-memory data generation (zero I/O) provides pure performance metrics.

## Compiling Benchmarks (if needed)
```bash
export PATH=/home/tishya/shivam/hpc/gem5/riscv-toolchain/riscv/bin:$PATH

# Simple variant
riscv64-unknown-linux-gnu-gcc -O2 mergesort/mergesort_simple.c \
    -o mergesort/mergesort_s -march=rv64imafdc -mabi=lp64d

# Chunked variant
riscv64-unknown-linux-gnu-gcc -O2 mergesort/mergesort_chunked.c \
    -o mergesort/mergesort_c -march=rv64imafdc -mabi=lp64d
```
