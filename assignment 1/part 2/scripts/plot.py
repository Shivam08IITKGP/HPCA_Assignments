import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

script_dir = os.path.dirname(os.path.abspath(__file__))
data_file = os.path.join(script_dir, '../results/full_sweep/full_sweep_results.csv')
visualization_dir = os.path.join(script_dir, '../results/analysis_plots')

os.makedirs(visualization_dir, exist_ok=True)

dataset = pd.read_csv(data_file)

def extract_size(size_str):
    if not isinstance(size_str, str): return 0
    # if 'MB' in size_str:
    #     return int(float(size_str.replace('MB', '')) * 1024)
    return int(size_str.replace('kB', ''))

dataset['L1_Int'] = dataset['L1_Size'].apply(extract_size)
dataset['L2_Int'] = dataset['L2_Size'].apply(extract_size)
dataset['L1_HitRate'] = 1 - dataset['L1_MissRate']
dataset = dataset.sort_values(['Type', 'L1_Int', 'L2_Int'])

sns.set_style("darkgrid")
sns.set_context("paper", font_scale=1.3)
plt.rcParams['figure.facecolor'] = 'white'
plt.rcParams['axes.facecolor'] = '#f0f0f0'
plt.rcParams['axes.edgecolor'] = 'black'
plt.rcParams['axes.linewidth'] = 1.5
plt.rcParams['grid.alpha'] = 0.6

plt.figure(figsize=(12, 7), dpi=100)
filtered_l2 = dataset[(dataset['L1_Size'] == '64kB') & (dataset['L1_Assoc'] == 8) & (dataset['L2_Assoc'] == 16)]

sns.barplot(data=filtered_l2, x='L2_Size', y='L2_MissRate', hue='Type', palette=['#d62728', '#2ca02c'], edgecolor='black', linewidth=1.5)
plt.title('L2 Miss Rate: Chunked vs Simple (L1=64kB, L1_Assoc=8, L2_Assoc=16)', fontsize=16, fontweight='bold', pad=20)
plt.ylabel('L2 Miss Rate (Lower is Better)', fontsize=13, fontweight='bold')
plt.xlabel('L2 Cache Size', fontsize=13, fontweight='bold')
plt.legend(title='Algorithm Type', fontsize=11, title_fontsize=12, framealpha=0.9)
plt.tight_layout()
plt.savefig(f'{visualization_dir}/plot_miss_rate_comparison.png', dpi=300, bbox_inches='tight')
plt.close()
print(f"Saved {visualization_dir}/plot_miss_rate_comparison.png")

plt.figure(figsize=(12, 7), dpi=100)
filtered_l1 = dataset[(dataset['L2_Size'] == '512kB') & (dataset['L1_Assoc'] == 8) & (dataset['L2_Assoc'] == 16)]
sns.lineplot(data=filtered_l1, x='L1_Size', y='Time', hue='Type', marker='o', markersize=10, linewidth=3, palette=['#d62728', '#2ca02c'])
plt.title('Impact of L1 Size on Execution Time (Fixed L2=512kB)', fontsize=16, fontweight='bold', pad=20)
plt.ylabel('Execution Time (seconds)', fontsize=13, fontweight='bold')
plt.xlabel('L1 Cache Size', fontsize=13, fontweight='bold')
plt.legend(title='Algorithm Type', fontsize=11, title_fontsize=12, framealpha=0.9)
plt.grid(True, alpha=0.3, linestyle='--')
plt.tight_layout()
plt.savefig(f'{visualization_dir}/plot_time_impact.png', dpi=300, bbox_inches='tight')
plt.close()
print(f"Saved {visualization_dir}/plot_time_impact.png")

plt.figure(figsize=(12, 7), dpi=100)
sns.barplot(data=filtered_l2, x='L2_Size', y='IPC', hue='Type', palette=['#1f77b4', '#ff7f0e'], edgecolor='black', linewidth=1.5)
plt.title('CPU Efficiency (IPC): Chunked vs Simple (L1=64kB)', fontsize=16, fontweight='bold', pad=20)
plt.ylabel('IPC (Higher is Better)', fontsize=13, fontweight='bold')
plt.xlabel('L2 Cache Size', fontsize=13, fontweight='bold')
plt.legend(title='Algorithm Type', fontsize=11, title_fontsize=12, framealpha=0.9)
plt.tight_layout()
plt.savefig(f'{visualization_dir}/plot_ipc_efficiency.png', dpi=300, bbox_inches='tight')
plt.close()
print(f"Saved {visualization_dir}/plot_ipc_efficiency.png")

plt.figure(figsize=(12, 7), dpi=100)
simple_subset = filtered_l1[filtered_l1['Type'] == 'Simple']
chunked_subset = filtered_l1[filtered_l1['Type'] == 'Chunked']

plt.plot(simple_subset['L1_Size'], simple_subset['L1_HitRate'], marker='o', markersize=12, 
         linewidth=3.5, color='#d62728', linestyle='-', label='Simple', alpha=0.9)
plt.plot(chunked_subset['L1_Size'], chunked_subset['L1_HitRate'], marker='s', markersize=12, 
         linewidth=3.5, color='#2ca02c', linestyle='--', label='Chunked', alpha=0.9)

plt.title('L1 Hit Rate vs L1 Size (Fixed L2=512kB)', fontsize=16, fontweight='bold', pad=20)
plt.ylabel('L1 Hit Rate', fontsize=13, fontweight='bold')
plt.xlabel('L1 Cache Size', fontsize=13, fontweight='bold')
plt.ylim(0.97, 1.002)
plt.legend(title='Algorithm Type', fontsize=11, title_fontsize=12, framealpha=0.9, loc='lower right')
plt.grid(True, alpha=0.3, linestyle=':')
plt.tight_layout()
plt.savefig(f'{visualization_dir}/plot_hitrate_l1.png', dpi=300, bbox_inches='tight')
plt.close()
print(f"Saved {visualization_dir}/plot_hitrate_l1.png")

print("\n--- TOP 3 CONFIGS BY IPC (Simple) ---")
best_simple = dataset[dataset['Type'] == 'Simple'].sort_values('IPC', ascending=False).head(3)
print(best_simple[['L1_Size', 'L1_Assoc', 'L2_Size', 'L2_Assoc', 'IPC']].to_string(index=False))

print("\n--- TOP 3 CONFIGS BY IPC (Chunked) ---")
best_chunked = dataset[dataset['Type'] == 'Chunked'].sort_values('IPC', ascending=False).head(3)
print(best_chunked[['L1_Size', 'L1_Assoc', 'L2_Size', 'L2_Assoc', 'IPC']].to_string(index=False))