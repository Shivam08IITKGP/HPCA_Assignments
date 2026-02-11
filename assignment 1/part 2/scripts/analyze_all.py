import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# --- Configuration ---
script_dir = os.path.dirname(os.path.abspath(__file__))
data_file = os.path.join(script_dir, '../results/full_sweep/full_sweep_results.csv')
visualization_dir = os.path.join(script_dir, '../results/analysis_plots')

baseline_l1_size = '64kB'
baseline_l1_assoc = 8
baseline_l2_size = '512kB'
baseline_l2_assoc = 16

os.makedirs(visualization_dir, exist_ok=True)

# --- Data Loading & Preprocessing ---
if not os.path.exists(data_file):
    print(f"Error: Could not find CSV at {data_file}")
    print("Please run 'python3 scripts/full_sweep.py' first.")
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

# =============================================================================
# PART 1: BASELINE ANALYSIS
# =============================================================================

config_filter = dataset[
    (dataset['L1_Size'] == baseline_l1_size) &
    (dataset['L1_Assoc'] == baseline_l1_assoc) &
    (dataset['L2_Size'] == baseline_l2_size) &
    (dataset['L2_Assoc'] == baseline_l2_assoc)
]

if config_filter.empty:
    print("\nWARNING: Could not find the default baseline configuration in the results file.")
    print(f"Target: L1={baseline_l1_size}, L1_Assoc={baseline_l1_assoc}, L2={baseline_l2_size}, L2_Assoc={baseline_l2_assoc}")
else:
    print("\n" + "="*60)
    print("PART 1: BASELINE CACHE PERFORMANCE COMPARISON")
    print("="*60)
    output_table = config_filter[['Type', 'Time', 'Cycles', 'IPC', 'L1_MissRate', 'L2_MissRate']].copy()
    output_table.rename(columns={
        'Type': 'Mergesort Type',
        'Time': 'Execution Time (s)',
        'Cycles': 'Simulation Ticks',
        'IPC': 'Instructions Per Cycle',
        'L1_MissRate': 'L1 Data Miss Rate',
        'L2_MissRate': 'L2 Miss Rate'
    }, inplace=True)
    output_table.set_index('Mergesort Type', inplace=True)
    print(output_table.to_string(float_format="%.6f"))
    print("="*60 + "\n")

# =============================================================================
# PART 2: COMPREHENSIVE PLOTTING
# =============================================================================

print("Generating analysis plots...")

# ------------------ Plot 1: L2 Miss Rate (Bar Chart) ------------------
plt.figure(figsize=(12, 7), dpi=100)
filtered_l2 = dataset[
    (dataset['L1_Size'] == '64kB') &
    (dataset['L1_Assoc'] == 8) &
    (dataset['L2_Assoc'] == 16)
]
sns.barplot(data=filtered_l2, x='L2_Size', y='L2_MissRate', hue='Type', palette=['#d62728', '#2ca02c'], edgecolor='black', linewidth=1.5)
plt.title('L2 Miss Rate: Chunked vs Simple (L1=64kB, Assoc=8/16)', fontsize=16, fontweight='bold', pad=20)
plt.ylabel('L2 Miss Rate (Lower is Better)', fontsize=13, fontweight='bold')
plt.xlabel('L2 Cache Size', fontsize=13, fontweight='bold')
plt.tight_layout()
plt.savefig(f'{visualization_dir}/plot_miss_rate_comparison.png', dpi=300)
plt.close()

# ------------------ Plot 2: Execution Time vs L1 Size ------------------
plt.figure(figsize=(12, 7), dpi=100)
filtered_l1 = dataset[
    (dataset['L2_Size'] == '512kB') &
    (dataset['L1_Assoc'] == 8) &
    (dataset['L2_Assoc'] == 16)
]
sns.lineplot(data=filtered_l1, x='L1_Size', y='Time', hue='Type', marker='o', markersize=10, linewidth=3, palette=['#d62728', '#2ca02c'])
plt.title('Impact of L1 Size on Execution Time (Fixed L2=512kB)', fontsize=16, fontweight='bold', pad=20)
plt.ylabel('Execution Time (seconds)', fontsize=13, fontweight='bold')
plt.xlabel('L1 Cache Size', fontsize=13, fontweight='bold')
plt.tight_layout()
plt.savefig(f'{visualization_dir}/plot_time_impact.png', dpi=300)
plt.close()

# ------------------ Plot 3: IPC (Bar Chart) ------------------
plt.figure(figsize=(12, 7), dpi=100)
sns.barplot(data=filtered_l2, x='L2_Size', y='IPC', hue='Type', palette=['#1f77b4', '#ff7f0e'], edgecolor='black', linewidth=1.5)
plt.title('CPU Efficiency (IPC): Chunked vs Simple (L1=64kB)', fontsize=16, fontweight='bold', pad=20)
plt.ylabel('IPC (Higher is Better)', fontsize=13, fontweight='bold')
plt.xlabel('L2 Cache Size', fontsize=13, fontweight='bold')
plt.tight_layout()
plt.savefig(f'{visualization_dir}/plot_ipc_efficiency.png', dpi=300)
plt.close()

# ------------------ Plot 4: L1 Hit Rate vs L1 Size ------------------
plt.figure(figsize=(12, 7), dpi=100)
sns.lineplot(data=filtered_l1, x='L1_Size', y='L1_HitRate', hue='Type', marker='o', markersize=10, linewidth=3, palette=['#d62728', '#2ca02c'])
plt.title('L1 Hit Rate vs L1 Size (Fixed L2=512kB)', fontsize=16, fontweight='bold', pad=20)
plt.ylabel('L1 Hit Rate', fontsize=13, fontweight='bold')
plt.xlabel('L1 Cache Size', fontsize=13, fontweight='bold')
plt.tight_layout()
plt.savefig(f'{visualization_dir}/plot_hitrate_l1.png', dpi=300)
plt.close()

# ------------------ Plot 5: L2 Miss Rate vs L2 Size (Line Plot) ------------------
plt.figure(figsize=(12, 7), dpi=100)
sns.lineplot(data=filtered_l2, x='L2_Size', y='L2_MissRate', hue='Type', marker='o', markersize=10, linewidth=3, palette=['#d62728', '#2ca02c'])
plt.title('L2 Miss Rate vs L2 Cache Size (L1=64kB)', fontsize=16, fontweight='bold', pad=20)
plt.ylabel('L2 Miss Rate (Lower is Better)', fontsize=13, fontweight='bold')
plt.xlabel('L2 Cache Size', fontsize=13, fontweight='bold')
plt.tight_layout()
plt.savefig(f'{visualization_dir}/plot_l2_missrate_vs_size.png', dpi=300)
plt.close()

# ------------------ Plot 6: IPC vs L1D Size (Line Plot) ------------------
plt.figure(figsize=(12, 7), dpi=100)
sns.lineplot(data=filtered_l1, x='L1_Size', y='IPC', hue='Type', marker='o', markersize=10, linewidth=3, palette=['#1f77b4', '#ff7f0e'])
plt.title('IPC vs L1D Cache Size (Fixed L2=512kB)', fontsize=16, fontweight='bold', pad=20)
plt.ylabel('IPC (Higher is Better)', fontsize=13, fontweight='bold')
plt.xlabel('L1D Cache Size', fontsize=13, fontweight='bold')
plt.tight_layout()
plt.savefig(f'{visualization_dir}/plot_ipc_vs_l1d_size.png', dpi=300)
plt.close()

# ------------------ Plot 7: L1D Hit Rate vs Associativity ------------------
plt.figure(figsize=(12, 7), dpi=100)
filtered_assoc = dataset[(dataset['L1_Size'] == '64kB') & (dataset['L2_Size'] == '512kB') & (dataset['L2_Assoc'] == 16)]
sns.lineplot(data=filtered_assoc, x='L1_Assoc', y='L1_HitRate', hue='Type', marker='o', markersize=10, linewidth=3, palette=['#d62728', '#2ca02c'])
plt.title('L1D Hit Rate vs Associativity (L1=64kB, L2=512kB)', fontsize=16, fontweight='bold', pad=20)
plt.ylabel('L1D Hit Rate (Higher is Better)', fontsize=13, fontweight='bold')
plt.xlabel('L1 Associativity', fontsize=13, fontweight='bold')
plt.xticks([4, 8, 16])
plt.tight_layout()
plt.savefig(f'{visualization_dir}/plot_l1d_hitrate_vs_assoc.png', dpi=300)
plt.close()

# ------------------ Plot 8: Comprehensive Comparison Grid ------------------
fig, axes = plt.subplots(1, 5, figsize=(25, 5), dpi=100)

fig.suptitle(
    'Simple vs Chunked MergeSort: Baseline Cache Performance Comparison',
    fontsize=18, fontweight='bold', y=1.05
)

BAR_WIDTH = 0.35  # thinner bars

def add_labels(ax, fmt="%.4f"):
    for p in ax.patches:
        ax.annotate(fmt % p.get_height(), (p.get_x() + p.get_width() / 2., p.get_height()),
                    ha='center', va='center', xytext=(0, 10), textcoords='offset points', fontweight='bold')

# Execution Time
sns.barplot(
    data=config_filter,
    x='Type', y='Time',
    hue='Type',
    palette=['#d62728', '#2ca02c'],
    width=BAR_WIDTH,
    ax=axes[0],
    legend=False
)
axes[0].set_title('Execution Time', fontweight='bold')
axes[0].set_ylabel('Seconds', fontweight='bold')
axes[0].set_ylim(
    config_filter['Time'].min() * 0.998,
    config_filter['Time'].max() * 1.002
)

# Simulation Ticks (Cycles)
sns.barplot(
    data=config_filter,
    x='Type', y='Cycles',
    hue='Type',
    palette=['#ff9f43', '#5f27cd'],
    width=BAR_WIDTH,
    ax=axes[1],
    legend=False
)
axes[1].set_title('Simulation Ticks', fontweight='bold')
axes[1].set_ylabel('Ticks', fontweight='bold')
axes[1].set_ylim(
    config_filter['Cycles'].min() * 0.998,
    config_filter['Cycles'].max() * 1.002
)

# IPC
sns.barplot(
    data=config_filter,
    x='Type', y='IPC',
    hue='Type',
    palette=['#1f77b4', '#ff7f0e'],
    width=BAR_WIDTH,
    ax=axes[2],
    legend=False
)
axes[2].set_title('IPC', fontweight='bold')
axes[2].set_ylabel('IPC', fontweight='bold')
axes[2].set_ylim(
    config_filter['IPC'].min() * 0.995,
    config_filter['IPC'].max() * 1.005
)

# L1 Miss Rate
sns.barplot(
    data=config_filter,
    x='Type', y='L1_MissRate',
    hue='Type',
    palette=['#9467bd', '#8c564b'],
    width=BAR_WIDTH,
    ax=axes[3],
    legend=False
)
axes[3].set_title('L1 Miss Rate', fontweight='bold')
axes[3].set_ylabel('Rate', fontweight='bold')
axes[3].set_ylim(
    config_filter['L1_MissRate'].min() * 0.95,
    config_filter['L1_MissRate'].max() * 1.05
)

# L2 Miss Rate
sns.barplot(
    data=config_filter,
    x='Type', y='L2_MissRate',
    hue='Type',
    palette=['#e377c2', '#7f7f7f'],
    width=BAR_WIDTH,
    ax=axes[4],
    legend=False
)
axes[4].set_title('L2 Miss Rate', fontweight='bold')
axes[4].set_ylabel('Rate', fontweight='bold')
axes[4].set_ylim(
    config_filter['L2_MissRate'].min() * 0.98,
    config_filter['L2_MissRate'].max() * 1.02
)

# Cosmetics
for ax in axes:
    ax.set_xlabel('')
    ax.tick_params(axis='x', labelrotation=0)

plt.tight_layout()
plt.savefig(
    f'{visualization_dir}/plot_simple_vs_chunked_comparison.png',
    dpi=300,
    bbox_inches='tight'
)
plt.close()

# =============================================================================
# TOP CONFIGURATIONS
# =============================================================================
print("Calculating top configurations...")
for algo in ['Simple', 'Chunked']:
    print(f"\n--- TOP 3 CONFIGS BY IPC ({algo}) ---")
    top = dataset[dataset['Type'] == algo].sort_values('IPC', ascending=False).head(3)
    print(top[['L1_Size', 'L1_Assoc', 'L2_Size', 'L2_Assoc', 'IPC']].to_string(index=False))

print(f"\n✅ Analysis complete! 8 plots generated in: {visualization_dir}")
