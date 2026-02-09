import pandas as pd
import os

script_dir = os.path.dirname(os.path.abspath(__file__))
results_csv = os.path.join(script_dir, '../results/full_sweep/full_sweep_results.csv')

baseline_l1_size = '64kB'
baseline_l1_assoc = 8
baseline_l2_size = '512kB'
baseline_l2_assoc = 16

try:
    dataset = pd.read_csv(results_csv)
except FileNotFoundError:
    print(f"Error: Could not find CSV at {results_csv}")
    print("Please ensure that 'part 2/scripts/full_sweep.py' has been run successfully.")
    exit(1)

config_filter = dataset[
    (dataset['L1_Size'] == baseline_l1_size) &
    (dataset['L1_Assoc'] == baseline_l1_assoc) &
    (dataset['L2_Size'] == baseline_l2_size) &
    (dataset['L2_Assoc'] == baseline_l2_assoc)
]

if config_filter.empty:
    print("Could not find the default configuration in the results file.")
    print(f"Default config: L1D={baseline_l1_size}, L1_Assoc={baseline_l1_assoc}, L2={baseline_l2_size}, L2_Assoc={baseline_l2_assoc}")
else:
    print("--- Part 2: Baseline Cache Performance Comparison ---")
    output_table = config_filter[['Type', 'Time', 'IPC', 'L1_MissRate', 'L2_MissRate']].copy()
    output_table.rename(columns={
        'Type': 'Mergesort Type',
        'Time': 'Execution Time (s)',
        'IPC': 'Instructions Per Cycle',
        'L1_MissRate': 'L1 Data Miss Rate',
        'L2_MissRate': 'L2 Miss Rate'
    }, inplace=True)
    
    output_table.set_index('Mergesort Type', inplace=True)
    
    print(output_table.to_string(float_format="%.6f"))

