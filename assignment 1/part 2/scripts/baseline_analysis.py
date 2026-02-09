import pandas as pd
import os

# --- CONFIGURATION ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(SCRIPT_DIR, '../results/full_sweep/full_sweep_results.csv')

# Default configuration from the PDF
DEFAULT_L1_SIZE = '64kB'
DEFAULT_L1_ASSOC = 8
DEFAULT_L2_SIZE = '512kB'
DEFAULT_L2_ASSOC = 16

# --- LOAD DATA ---
try:
    df = pd.read_csv(CSV_PATH)
except FileNotFoundError:
    print(f"Error: Could not find CSV at {CSV_PATH}")
    print("Please ensure that 'part 2/scripts/full_sweep.py' has been run successfully.")
    exit(1)

# --- FILTER FOR DEFAULT CONFIGURATION ---
baseline_df = df[
    (df['L1_Size'] == DEFAULT_L1_SIZE) &
    (df['L1_Assoc'] == DEFAULT_L1_ASSOC) &
    (df['L2_Size'] == DEFAULT_L2_SIZE) &
    (df['L2_Assoc'] == DEFAULT_L2_ASSOC)
]

# --- DISPLAY RESULTS ---
if baseline_df.empty:
    print("Could not find the default configuration in the results file.")
    print(f"Default config: L1D={DEFAULT_L1_SIZE}, L1_Assoc={DEFAULT_L1_ASSOC}, L2={DEFAULT_L2_SIZE}, L2_Assoc={DEFAULT_L2_ASSOC}")
else:
    print("--- Part 2: Baseline Cache Performance Comparison ---")
    # Select and rename columns for clarity
    display_df = baseline_df[['Type', 'Time', 'IPC', 'L1_MissRate', 'L2_MissRate']].copy()
    display_df.rename(columns={
        'Type': 'Mergesort Type',
        'Time': 'Execution Time (s)',
        'IPC': 'Instructions Per Cycle',
        'L1_MissRate': 'L1 Data Miss Rate',
        'L2_MissRate': 'L2 Miss Rate'
    }, inplace=True)
    
    # Set 'Mergesort Type' as the index for a cleaner table
    display_df.set_index('Mergesort Type', inplace=True)
    
    print(display_df.to_string(float_format="%.6f"))

