import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# --- Configuration ---
script_dir = os.path.dirname(os.path.abspath(__file__))
data_file = os.path.join(script_dir, '../results/results.csv')
visualization_dir = os.path.join(script_dir, '../results/plots')

baseline_l1_size = '64kB'
baseline_l1_assoc = 8
baseline_l2_size = '512kB'
baseline_l2_assoc = 16

os.makedirs(visualization_dir, exist_ok=True)

# --- Data Loading & Preprocessing ---
if not os.path.exists(data_file):
    print(f"Error: Could not find CSV at {data_file}")
    print("Please run 'python3 scripts/extract_results.py' first.")
    exit(1)

dataset = pd.read_csv(data_file)

def extract_size(size_str):
    if not isinstance(size_str, str):
        return 0
    return int(size_str.replace('kB', ''))

dataset['L1_Int'] = dataset['L1_Size'].apply(extract_size)
dataset['L2_Int'] = dataset['L2_Size'].apply(extract_size)
dataset['L1_HitRate'] = 1 - dataset['L1_MissRate']
dataset = dataset.sort_values(['Type', 'L1_Int', 'L2_Int'])

# --- Styling ---
sns.set_style("darkgrid")
sns.set_context("paper", font_scale=1.3)
plt.rcParams['figure.facecolor'] = 'white'
plt.rcParams['axes.facecolor'] = '#f0f0f0'
plt.rcParams['axes.edgecolor'] = 'black'
plt.rcParams['axes.linewidth'] = 1.5
plt.rcParams['grid.alpha'] = 0.6

# ------------------ Baseline Data for Comparison ------------------
baseline_data = dataset[
    (dataset['L1_Size'] == baseline_l1_size) &
    (dataset['L1_Assoc'] == baseline_l1_assoc) &
    (dataset['L2_Size'] == baseline_l2_size) &
    (dataset['L2_Assoc'] == baseline_l2_assoc)
]

print("Generating 8 analysis plots...")

# 1. plot_miss_rate_comparison.png (Bar Chart)
plt.figure(figsize=(12, 7))
sns.barplot(data=baseline_data, x='Type', y='L2_MissRate', palette=['#d62728', '#2ca02c'], edgecolor='black', linewidth=1.5)
plt.title('L2 Miss Rate Comparison at Baseline', fontsize=16, fontweight='bold', pad=20)
plt.ylabel('L2 Miss Rate (Lower is Better)', fontweight='bold')
plt.savefig(os.path.join(visualization_dir, 'plot_miss_rate_comparison.png'), dpi=300)
plt.close()

# 2. plot_time_impact.png (Execution Time vs L1 Size)
plt.figure(figsize=(12, 7))
sns.lineplot(data=dataset[dataset['L2_Size'] == baseline_l2_size], x='L1_Size', y='Time', hue='Type', marker='o', linewidth=3)
plt.title('Impact of L1 Size on Execution Time', fontweight='bold')
plt.savefig(os.path.join(visualization_dir, 'plot_time_impact.png'), dpi=300)
plt.close()

# 3. plot_ipc_efficiency.png (IPC Bar Chart)
plt.figure(figsize=(12, 7))
sns.barplot(data=baseline_data, x='Type', y='IPC', palette=['#1f77b4', '#ff7f0e'], edgecolor='black', linewidth=1.5)
plt.title('CPU Efficiency (IPC) Comparison', fontweight='bold')
plt.savefig(os.path.join(visualization_dir, 'plot_ipc_efficiency.png'), dpi=300)
plt.close()

# 4. plot_hitrate_l1.png (L1 Hit Rate vs L1 Size)
plt.figure(figsize=(12, 7))
sns.lineplot(data=dataset[dataset['L2_Size'] == baseline_l2_size], x='L1_Size', y='L1_HitRate', hue='Type', marker='o', linewidth=3)
plt.title('L1 Hit Rate vs L1 Size', fontweight='bold')
plt.savefig(os.path.join(visualization_dir, 'plot_hitrate_l1.png'), dpi=300)
plt.close()

# 5. plot_l2_missrate_vs_size.png (Line Plot)
plt.figure(figsize=(12, 7))
sns.lineplot(data=dataset[dataset['L1_Size'] == baseline_l1_size], x='L2_Size', y='L2_MissRate', hue='Type', marker='o', linewidth=3)
plt.title('L2 Miss Rate vs L2 Cache Size', fontweight='bold')
plt.savefig(os.path.join(visualization_dir, 'plot_l2_missrate_vs_size.png'), dpi=300)
plt.close()

# 6. plot_ipc_vs_l1d_size.png (Line Plot)
plt.figure(figsize=(12, 7))
sns.lineplot(data=dataset[dataset['L2_Size'] == baseline_l2_size], x='L1_Size', y='IPC', hue='Type', marker='o', linewidth=3)
plt.title('IPC vs L1D Cache Size', fontweight='bold')
plt.savefig(os.path.join(visualization_dir, 'plot_ipc_vs_l1d_size.png'), dpi=300)
plt.close()

# 7. plot_l1d_hitrate_vs_assoc.png (Line Plot)
plt.figure(figsize=(12, 7))
sns.lineplot(data=dataset[(dataset['L1_Size'] == baseline_l1_size) & (dataset['L2_Size'] == baseline_l2_size)], x='L1_Assoc', y='L1_HitRate', hue='Type', marker='o', linewidth=3)
plt.title('L1D Hit Rate vs Associativity', fontweight='bold')
plt.xticks([4, 8, 16])
plt.savefig(os.path.join(visualization_dir, 'plot_l1d_hitrate_vs_assoc.png'), dpi=300)
plt.close()

# 8. plot_simple_vs_chunked_comparison.png (Grid)
fig, axes = plt.subplots(1, 5, figsize=(25, 5))
fig.suptitle('Simple vs Chunked: Baseline Comparison', fontsize=18, fontweight='bold', y=1.05)
for i, col in enumerate(['Time', 'Cycles', 'IPC', 'L1_MissRate', 'L2_MissRate']):
    sns.barplot(data=baseline_data, x='Type', y=col, hue='Type', ax=axes[i], legend=False)
    axes[i].set_title(col, fontweight='bold')
plt.tight_layout()
plt.savefig(os.path.join(visualization_dir, 'plot_simple_vs_chunked_comparison.png'), dpi=300, bbox_inches='tight')
plt.close()

# --- Summary ---
print("\n" + "="*60)
print("BASELINE PERFORMANCE SUMMARY")
print("="*60)
print(baseline_data[['Type', 'Time', 'Cycles', 'IPC', 'L1_MissRate', 'L2_MissRate']].to_string(index=False))

print("\n" + "="*60)
print("TOP 3 CONFIGURATIONS (BY IPC)")
print("="*60)
for algo in ['Simple', 'Chunked']:
    print(f"\n--- {algo.upper()} ---")
    top = dataset[dataset['Type'] == algo].sort_values('IPC', ascending=False).head(3)
    print(top[['L1_Size', 'L2_Size', 'L1_Assoc', 'L2_Assoc', 'IPC']].to_string(index=False))

print(f"\n✅ Success! 8 plots generated in {visualization_dir}")
