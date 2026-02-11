import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import numpy as np

# Paths
current_dir = os.path.dirname(os.path.abspath(__file__))
project_base = os.path.abspath(os.path.join(current_dir, ".."))
results_base = os.path.join(project_base, "results")
plot_output = os.path.join(results_base, 'analysis_all')
os.makedirs(plot_output, exist_ok=True)

# Load enhanced data
data_files = {
    64: os.path.join(results_base, 'full_sweep_64/enhanced_results_64.csv'),
    128: os.path.join(results_base, 'full_sweep/enhanced_results.csv'),
    256: os.path.join(results_base, 'full_sweep_256/enhanced_results_256.csv')
}

def is_pareto_efficient(costs):
    """
    Find the pareto-efficient points
    :param costs: An (n_points, n_costs) array
    :return: A (n_points, ) boolean array indicating whether each point is Pareto efficient
    """
    is_efficient = np.ones(costs.shape[0], dtype=bool)
    for i, c in enumerate(costs):
        if is_efficient[i]:
            # Keep any point with a lower cost
            is_efficient[is_efficient] = np.any(costs[is_efficient] < c, axis=1)
            # And keep self
            is_efficient[i] = True
    return is_efficient

combined_data = []
for matrix_dim, file_path in data_files.items():
    if os.path.exists(file_path):
        df = pd.read_csv(file_path)
        df['MatrixSize'] = matrix_dim
        combined_data.append(df)
    else:
        print(f"Warning: File not found: {file_path}")

full_dataset = pd.concat(combined_data, ignore_index=True)

# Filter out 128kB L1 cache configurations as requested in previous steps
full_dataset = full_dataset[full_dataset['L1_Size'] != '128kB']

# Pareto Analysis
print("\nIdentifying Pareto-Optimal Configurations...")
pareto_results = []

plt.figure(figsize=(15, 10))
colors = {64: '#1f77b4', 128: '#ff7f0e', 256: '#2ca02c'}

for size in [64, 128, 256]:
    subset = full_dataset[full_dataset['MatrixSize'] == size].copy()
    
    # We want to minimize both simTicks and TotalCacheSize
    # Extract numeric columns for Pareto calculation
    costs = subset[['TotalCacheSize', 'simTicks']].values
    
    efficient_mask = is_pareto_efficient(costs)
    pareto_points = subset[efficient_mask].sort_values('TotalCacheSize')
    
    # Store for summary
    pareto_points['MatrixSize'] = size
    pareto_results.append(pareto_points)
    
    # Scatter plot of all points
    plt.scatter(subset['TotalCacheSize'], subset['simTicks'], 
               color=colors[size], alpha=0.2, label=f'{size}x{size} (All)', s=20)
    
    # Pareto front line
    plt.plot(pareto_points['TotalCacheSize'], pareto_points['simTicks'], 
            'o-', color=colors[size], linewidth=3, markersize=8, label=f'{size}x{size} Pareto Front')

plt.yscale('log')
plt.xlabel('Total Cache Size (L1D + L2) [kB]', fontsize=14, fontweight='bold')
plt.ylabel('Execution Time (simTicks) [log scale]', fontsize=14, fontweight='bold')
plt.title('Design Space Exploration: Pareto-Optimal Cache Configurations', fontsize=18, fontweight='bold', pad=20)
plt.legend(loc='upper right', frameon=True, fontsize=12)
plt.grid(True, which="both", ls="-", alpha=0.3)
plt.tight_layout()

pareto_plot_path = os.path.join(plot_output, 'pareto_frontier.png')
plt.savefig(pareto_plot_path, dpi=300)
print(f"Pareto plot saved to: {pareto_plot_path}")

# Export Pareto summary
all_pareto = pd.concat(pareto_results)
pareto_csv_path = os.path.join(plot_output, 'pareto_optimal_configs.csv')
all_pareto.to_csv(pareto_csv_path, index=False)
print(f"Pareto summary saved to: {pareto_csv_path}")

# Print summary table for report
print("\n--- Pareto Optimal Configurations ---")
cols_to_print = ['MatrixSize', 'L1_Size', 'L2_Size', 'L1_Assoc', 'L2_Assoc', 'TotalCacheSize', 'simTicks']
print(all_pareto[cols_to_print].to_string(index=False))
