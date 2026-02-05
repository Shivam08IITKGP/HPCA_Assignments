import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# --- CONFIGURATION ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
csv_path = os.path.join(SCRIPT_DIR, '../results/full_sweep/full_sweep_results.csv')
output_dir = os.path.join(SCRIPT_DIR, '../results/analysis_plots')

# Ensure output directory exists
os.makedirs(output_dir, exist_ok=True)

# --- LOAD AND PREP DATA ---
try:
    df = pd.read_csv(csv_path)
except FileNotFoundError:
    print(f"Error: Could not find CSV at {csv_path}")
    print(f"Make sure you have run full_sweep.py first.")
    exit(1)

# Convert L1/L2 Size strings (e.g., '256kB') to integers for proper sorting
def parse_size(s):
    if not isinstance(s, str): return 0
    if 'MB' in s:
        return int(float(s.replace('MB', '')) * 1024)
    return int(s.replace('kB', ''))

df['L1_Int'] = df['L1_Size'].apply(parse_size)
df['L2_Int'] = df['L2_Size'].apply(parse_size)
df = df.sort_values(['Type', 'L1_Int', 'L2_Int'])

# Set visual style
sns.set_style("whitegrid")

# --- PLOT 1: L2 MISS RATE COMPARISON (from original plot.py) ---
plt.figure(figsize=(10, 6))
# Filter to see pure L2 size impact for a fixed L1
subset = df[(df['L1_Size'] == '64kB') & (df['L1_Assoc'] == 8)]

sns.barplot(data=subset, x='L2_Size', y='L2_MissRate', hue='Type', palette='viridis')
plt.title('L2 Miss Rate: Chunked vs Simple (L1=64kB, Assoc=8)')
plt.ylabel('L2 Miss Rate (Lower is Better)')
plt.savefig(f'{output_dir}/plot_miss_rate_comparison.png')
print(f"Saved {output_dir}/plot_miss_rate_comparison.png")

# --- PLOT 2: EXECUTION TIME COMPARISON (from original plot.py) ---
plt.figure(figsize=(10, 6))
sns.lineplot(data=subset, x='L1_Size', y='Time', hue='Type', marker='o')
plt.title('L1 Size impact on Execution Time (Fixed L2=512kB)')
plt.ylabel('Execution Time (seconds)')
plt.savefig(f'{output_dir}/plot_time_impact.png')
print(f"Saved {output_dir}/plot_time_impact.png")

# --- PLOT 3: CPU Efficiency (IPC) ---
plt.figure(figsize=(10, 6))
sns.barplot(data=subset, x='L2_Size', y='IPC', hue='Type', palette='muted')
plt.title('CPU Efficiency (IPC): Chunked vs Simple (L1=64kB)')
plt.ylabel('IPC (Higher is Better)')
plt.savefig(f'{output_dir}/plot_ipc_efficiency.png')
print(f"Saved {output_dir}/plot_ipc_efficiency.png")

# --- PLOT 4: Hit Rate (from plot_part2.py logic) ---
# L1 Hit Rate = 1 - L1 Miss Rate
df['L1_HitRate'] = 1 - df['L1_MissRate']
plt.figure(figsize=(10, 6))
sns.lineplot(data=subset, x='L1_Size', y='L1_HitRate', hue='Type', marker='s')
plt.title('L1 Hit Rate vs L1 Size (Fixed L2=512kB)')
plt.ylabel('L1 Hit Rate')
plt.ylim(0, 1.05)
plt.savefig(f'{output_dir}/plot_hitrate_l1.png')
print(f"Saved {output_dir}/plot_hitrate_l1.png")

# --- TOP 3 CONFIGS BY IPC ---
print("\n--- TOP 3 CONFIGS BY IPC (Simple) ---")
top3_simple = df[df['Type'] == 'Simple'].sort_values('IPC', ascending=False).head(3)
print(top3_simple[['L1_Size', 'L1_Assoc', 'L2_Size', 'L2_Assoc', 'IPC']].to_string(index=False))

print("\n--- TOP 3 CONFIGS BY IPC (Chunked) ---")
top3_chunked = df[df['Type'] == 'Chunked'].sort_values('IPC', ascending=False).head(3)
print(top3_chunked[['L1_Size', 'L1_Assoc', 'L2_Size', 'L2_Assoc', 'IPC']].to_string(index=False))