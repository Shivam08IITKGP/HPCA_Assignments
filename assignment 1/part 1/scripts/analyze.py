import os
import re
import csv
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# ============================================================================
# Paths & Configuration
# ============================================================================
current_dir = os.path.dirname(os.path.abspath(__file__))
project_base = os.path.abspath(os.path.join(current_dir, ".."))
results_base = os.path.join(project_base, "results")
plot_output = os.path.join(results_base, 'analysis_all')
os.makedirs(plot_output, exist_ok=True)

# Resolution target for Overleaf (1200px width)
TARGET_WIDTH_PX = 1200
def get_dpi(fig_width_inches):
    return int(TARGET_WIDTH_PX / fig_width_inches)

sweep_configs = [
    {
        'dir': os.path.join(results_base, 'full_sweep_64'),
        'output': os.path.join(results_base, 'full_sweep_64', 'enhanced_results_64.csv'),
        'matrix_size': 64
    },
    {
        'dir': os.path.join(results_base, 'full_sweep'),
        'output': os.path.join(results_base, 'full_sweep', 'enhanced_results.csv'),
        'matrix_size': 128
    },
    {
        'dir': os.path.join(results_base, 'full_sweep_256'),
        'output': os.path.join(results_base, 'full_sweep_256', 'enhanced_results_256.csv'),
        'matrix_size': 256
    }
]

# ============================================================================
# Extraction Logic
# ============================================================================
def parse_cache_size(size_str):
    return int(size_str.replace('kB', ''))

def extract_metrics_from_stats(stats_file):
    if not os.path.exists(stats_file):
        return None
    with open(stats_file, 'r') as f:
        content = f.read()
    
    metrics = {}
    m = re.search(r'simTicks\s+(\d+)', content)
    metrics['simTicks'] = int(m.group(1)) if m else None
    m = re.search(r'simSeconds\s+([0-9.e\-+]+)', content)
    metrics['simSeconds'] = float(m.group(1)) if m else None
    m = re.search(r'hostSeconds\s+([0-9.e\-+]+)', content)
    metrics['hostSeconds'] = float(m.group(1)) if m else None
    m = re.search(r'system\.cpu\.dcache\.overallMissRate::total\s+([0-9.e\-+]+)', content)
    metrics['L1_MissRate'] = float(m.group(1)) if m else None
    m = re.search(r'system\.l2cache\.overallMissRate::total\s+([0-9.e\-+]+)', content)
    metrics['L2_MissRate'] = float(m.group(1)) if m else None
    
    if metrics['L1_MissRate'] is not None:
        metrics['L1_HitRate'] = 1.0 - metrics['L1_MissRate']
    if metrics['L2_MissRate'] is not None:
        metrics['L2_HitRate'] = 1.0 - metrics['L2_MissRate']
    return metrics

def parse_config(dirname):
    parts = dirname.split('_')
    try:
        return {'L1_Size': parts[1], 'L2_Size': parts[3], 'L1_Assoc': int(parts[5]), 'L2_Assoc': int(parts[7])}
    except: return None

def run_extraction():
    print("Extracting metrics from simulation results...")
    for cfg in sweep_configs:
        if not os.path.exists(cfg['dir']): continue
        results = []
        for d in os.listdir(cfg['dir']):
            path = os.path.join(cfg['dir'], d)
            if not os.path.isdir(path): continue
            parts = parse_config(d)
            if not parts: continue
            m = extract_metrics_from_stats(os.path.join(path, 'stats.txt'))
            if not m: continue
            row = {**parts, **m, 'TotalCacheSize': parse_cache_size(parts['L1_Size']) + parse_cache_size(parts['L2_Size'])}
            results.append(row)
        if results:
            df = pd.DataFrame(results).sort_values(['L1_Size', 'L2_Size', 'L1_Assoc', 'L2_Assoc'])
            df.to_csv(cfg['output'], index=False)
            print(f"  ✓ {cfg['matrix_size']}x{cfg['matrix_size']}: {len(df)} configs saved to {os.path.basename(cfg['output'])}")

# ============================================================================
# Plotting Logic
# ============================================================================
def run_plotting():
    print("\nGenerating comprehensive plots...")
    combined_data = []
    for cfg in sweep_configs:
        if os.path.exists(cfg['output']):
            df = pd.read_csv(cfg['output'])
            df['MatrixSize'] = cfg['matrix_size']
            combined_data.append(df)
    
    if not combined_data: return
    full_dataset = pd.concat(combined_data, ignore_index=True)
    full_dataset['L1_Int'] = full_dataset['L1_Size'].str.replace('kB','').astype(int)
    full_dataset['L2_Int'] = full_dataset['L2_Size'].str.replace('kB','').astype(int)
    full_dataset = full_dataset[full_dataset['L1_Int'] != 128] # Filter experimental 128kB L1

    sns.set_theme(style="whitegrid", font_scale=1.0)
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c']

    # 1. L1 Size vs Time
    fig1 = plt.figure(figsize=(10, 6))
    sns.lineplot(data=full_dataset[full_dataset['L2_Size'] == '256kB'], x='L1_Int', y='simSeconds', hue='MatrixSize', linewidth=3, marker='o', palette='Dark2')
    plt.yscale('log')
    plt.title("Impact of L1 Cache Size on Execution Time (L2=256kB)", weight='bold')
    plt.tight_layout()
    fig1.savefig(os.path.join(plot_output, 'l1_size_vs_time.png'), dpi=get_dpi(10))
    plt.close()

    # 2. L2 Size vs Time
    fig2 = plt.figure(figsize=(10, 6))
    sns.lineplot(data=full_dataset[full_dataset['L1_Size'] == '16kB'], x='L2_Int', y='simSeconds', hue='MatrixSize', linewidth=3, marker='s', palette='tab10')
    plt.yscale('log')
    plt.title("Impact of L2 Cache Size on Execution Time (L1=16kB)", weight='bold')
    plt.tight_layout()
    plt.savefig(os.path.join(plot_output, 'l2_size_vs_time.png'), dpi=get_dpi(10))
    plt.close()

    # 3. Hit Rate Analysis
    metrics_to_plot = [
        ('L1_Int', 'L1_HitRate', 'L1D Hit Rate vs L1 Cache Size', 'l1_hitrate_vs_l1_size.png'),
        ('L1_Assoc', 'L1_HitRate', 'L1D Hit Rate vs L1 Associativity', 'l1_hitrate_vs_l1_assoc.png'),
        ('L2_Int', 'L2_HitRate', 'L2D Hit Rate vs L2 Cache Size', 'l2_hitrate_vs_l2_size.png'),
        ('L2_Assoc', 'L2_HitRate', 'L2D Hit Rate vs L2 Associativity', 'l2_hitrate_vs_l2_assoc.png')
    ]
    for param, metric, title, fname in metrics_to_plot:
        plt.figure(figsize=(10, 6))
        for i, m_size in enumerate([64, 128, 256]):
            subset = full_dataset[full_dataset['MatrixSize'] == m_size]
            grouped = subset.groupby(param)[metric].mean()
            plt.plot(grouped.index, grouped.values, marker='o', linewidth=2.5, label=f'{m_size}x{m_size}', color=colors[i])
        plt.title(title, weight='bold')
        plt.legend(title='Matrix Size')
        plt.tight_layout()
        plt.savefig(os.path.join(plot_output, fname), dpi=get_dpi(10))
        plt.close()

    # 4. Heatmaps (128x128 example)
    plt.figure(figsize=(10, 8))
    h_data = full_dataset[full_dataset['MatrixSize'] == 128].pivot_table(index='L1_Size', columns='L2_Size', values='simSeconds', aggfunc='mean')
    sns.heatmap(h_data, annot=True, fmt=".4f", cmap="viridis")
    plt.title('Execution Time Heatmap (Matrix 128x128)', weight='bold')
    plt.tight_layout()
    plt.savefig(os.path.join(plot_output, 'heatmap_time_128x128.png'), dpi=get_dpi(10))
    plt.close()

    print(f"  ✓ All plots saved to {plot_output}")

    # Summary Statistics
    stats = []
    for m in [64, 128, 256]:
        sub = full_dataset[full_dataset['MatrixSize'] == m]
        for met in ['simSeconds', 'L1_HitRate', 'L2_HitRate']:
            stats.append({'Matrix': m, 'Metric': met, 'Mean': sub[met].mean(), 'Min': sub[met].min(), 'Max': sub[met].max()})
    pd.DataFrame(stats).to_csv(os.path.join(plot_output, 'summary_statistics.csv'), index=False)
    
    print("\n--- Top Configurations (Fastest) ---")
    for m in [64, 128, 256]:
        best = full_dataset[full_dataset['MatrixSize'] == m].sort_values('simSeconds').head(1)
        print(f"Matrix {m}x{m}: L1={best['L1_Size'].values[0]}, L2={best['L2_Size'].values[0]}, L1_Assoc={best['L1_Assoc'].values[0]}, L2_Assoc={best['L2_Assoc'].values[0]} -> {best['simSeconds'].values[0]:.4f}s")

if __name__ == "__main__":
    run_extraction()
    run_plotting()
