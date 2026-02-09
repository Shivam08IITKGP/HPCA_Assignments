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
# L1 Hit Rate = 1 - L1 Miss Rate
df['L1_HitRate'] = 1 - df['L1_MissRate']
df = df.sort_values(['Type', 'L1_Int', 'L2_Int'])

# Set visual style with better contrast
sns.set_style("darkgrid")
sns.set_context("paper", font_scale=1.3)
plt.rcParams['figure.facecolor'] = 'white'
plt.rcParams['axes.facecolor'] = '#f0f0f0'
plt.rcParams['axes.edgecolor'] = 'black'
plt.rcParams['axes.linewidth'] = 1.5
plt.rcParams['grid.alpha'] = 0.6

# --- PLOT 1: L2 MISS RATE COMPARISON ---
plt.figure(figsize=(12, 7), dpi=100)
# Filter to see pure L2 size impact for a fixed L1 configuration
subset_l2 = df[(df['L1_Size'] == '64kB') & (df['L1_Assoc'] == 8) & (df['L2_Assoc'] == 16)]

sns.barplot(data=subset_l2, x='L2_Size', y='L2_MissRate', hue='Type', palette=['#d62728', '#2ca02c'], edgecolor='black', linewidth=1.5)
plt.title('L2 Miss Rate: Chunked vs Simple (L1=64kB, L1_Assoc=8, L2_Assoc=16)', fontsize=16, fontweight='bold', pad=20)
plt.ylabel('L2 Miss Rate (Lower is Better)', fontsize=13, fontweight='bold')
plt.xlabel('L2 Cache Size', fontsize=13, fontweight='bold')
plt.legend(title='Algorithm Type', fontsize=11, title_fontsize=12, framealpha=0.9)
plt.tight_layout()
plt.savefig(f'{output_dir}/plot_miss_rate_comparison.png', dpi=300, bbox_inches='tight')
plt.close()
print(f"Saved {output_dir}/plot_miss_rate_comparison.png")

# --- PLOT 2: L1 SIZE IMPACT ON EXECUTION TIME ---
plt.figure(figsize=(12, 7), dpi=100)
# Filter for fixed L2 to see L1 size impact
subset_l1 = df[(df['L2_Size'] == '512kB') & (df['L1_Assoc'] == 8) & (df['L2_Assoc'] == 16)]
sns.lineplot(data=subset_l1, x='L1_Size', y='Time', hue='Type', marker='o', markersize=10, linewidth=3, palette=['#d62728', '#2ca02c'])
plt.title('Impact of L1 Size on Execution Time (Fixed L2=512kB)', fontsize=16, fontweight='bold', pad=20)
plt.ylabel('Execution Time (seconds)', fontsize=13, fontweight='bold')
plt.xlabel('L1 Cache Size', fontsize=13, fontweight='bold')
plt.legend(title='Algorithm Type', fontsize=11, title_fontsize=12, framealpha=0.9)
plt.grid(True, alpha=0.3, linestyle='--')
plt.tight_layout()
plt.savefig(f'{output_dir}/plot_time_impact.png', dpi=300, bbox_inches='tight')
plt.close()
print(f"Saved {output_dir}/plot_time_impact.png")

# --- PLOT 3: CPU Efficiency (IPC) ---
plt.figure(figsize=(12, 7), dpi=100)
sns.barplot(data=subset_l2, x='L2_Size', y='IPC', hue='Type', palette=['#1f77b4', '#ff7f0e'], edgecolor='black', linewidth=1.5)
plt.title('CPU Efficiency (IPC): Chunked vs Simple (L1=64kB)', fontsize=16, fontweight='bold', pad=20)
plt.ylabel('IPC (Higher is Better)', fontsize=13, fontweight='bold')
plt.xlabel('L2 Cache Size', fontsize=13, fontweight='bold')
plt.legend(title='Algorithm Type', fontsize=11, title_fontsize=12, framealpha=0.9)
plt.tight_layout()
plt.savefig(f'{output_dir}/plot_ipc_efficiency.png', dpi=300, bbox_inches='tight')
plt.close()
print(f"Saved {output_dir}/plot_ipc_efficiency.png")

# --- PLOT 4: Hit Rate vs L1 Size ---
plt.figure(figsize=(12, 7), dpi=100)
# Plot each type separately with different styles for better visibility
simple_data = subset_l1[subset_l1['Type'] == 'Simple']
chunked_data = subset_l1[subset_l1['Type'] == 'Chunked']

plt.plot(simple_data['L1_Size'], simple_data['L1_HitRate'], marker='o', markersize=12, 
         linewidth=3.5, color='#d62728', linestyle='-', label='Simple', alpha=0.9)
plt.plot(chunked_data['L1_Size'], chunked_data['L1_HitRate'], marker='s', markersize=12, 
         linewidth=3.5, color='#2ca02c', linestyle='--', label='Chunked', alpha=0.9)

plt.title('L1 Hit Rate vs L1 Size (Fixed L2=512kB)', fontsize=16, fontweight='bold', pad=20)
plt.ylabel('L1 Hit Rate', fontsize=13, fontweight='bold')
plt.xlabel('L1 Cache Size', fontsize=13, fontweight='bold')
plt.ylim(0.97, 1.002)
plt.legend(title='Algorithm Type', fontsize=11, title_fontsize=12, framealpha=0.9, loc='lower right')
plt.grid(True, alpha=0.3, linestyle=':')
plt.tight_layout()
plt.savefig(f'{output_dir}/plot_hitrate_l1.png', dpi=300, bbox_inches='tight')
plt.close()
print(f"Saved {output_dir}/plot_hitrate_l1.png")

# --- TOP 3 CONFIGS BY IPC ---
print("\n--- TOP 3 CONFIGS BY IPC (Simple) ---")
top3_simple = df[df['Type'] == 'Simple'].sort_values('IPC', ascending=False).head(3)
print(top3_simple[['L1_Size', 'L1_Assoc', 'L2_Size', 'L2_Assoc', 'IPC']].to_string(index=False))

print("\n--- TOP 3 CONFIGS BY IPC (Chunked) ---")
top3_chunked = df[df['Type'] == 'Chunked'].sort_values('IPC', ascending=False).head(3)
print(top3_chunked[['L1_Size', 'L1_Assoc', 'L2_Size', 'L2_Assoc', 'IPC']].to_string(index=False))