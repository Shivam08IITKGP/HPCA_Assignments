import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
data_path = os.path.join(current_dir, '../results')
plot_output = os.path.join(data_path, 'analysis_all')
os.makedirs(plot_output, exist_ok=True)

data_files = {
    64: os.path.join(data_path, 'full_sweep_64/full_sweep_results_64.csv'),
    128: os.path.join(data_path, 'full_sweep/full_sweep_results.csv'),
    256: os.path.join(data_path, 'full_sweep_256/full_sweep_results_256.csv')
}

combined_data = []
for matrix_dim, file_path in data_files.items():
    if os.path.exists(file_path):
        try:
            dataframe = pd.read_csv(file_path)
            dataframe['MatrixSize'] = matrix_dim
            combined_data.append(dataframe)
            print(f"Loaded data for Matrix {matrix_dim}")
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
    else:
        print(f"Warning: File not found: {file_path}")

if not combined_data:
    print("Error: No data files found. Exiting.")
    exit(1)

full_dataset = pd.concat(combined_data, ignore_index=True)

full_dataset['L1_Int'] = full_dataset['L1_Size'].str.replace('kB','').astype(int)
full_dataset['L2_Int'] = full_dataset['L2_Size'].str.replace('kB','').astype(int)
full_dataset['L1_Assoc'] = full_dataset['L1_Assoc'].astype(int)
full_dataset['L2_Assoc'] = full_dataset['L2_Assoc'].astype(int)

full_dataset['Time'] = pd.to_numeric(full_dataset['Time'], errors='coerce')
full_dataset.dropna(subset=['Time'], inplace=True)

l1_sorted = sorted(full_dataset['L1_Int'].unique())
l2_sorted = sorted(full_dataset['L2_Int'].unique())
l1_categories = [f"{x}kB" for x in l1_sorted]
l2_categories = [f"{x}kB" for x in l2_sorted]

full_dataset['L1_Size'] = pd.Categorical(full_dataset['L1_Size'], categories=l1_categories, ordered=True)
full_dataset['L2_Size'] = pd.Categorical(full_dataset['L2_Size'], categories=l2_categories, ordered=True)

sns.set_theme(style="whitegrid", font_scale=1.1)

plt.figure(figsize=(12, 7))

plot1_data = full_dataset[full_dataset['L2_Size'] == '256kB']

sns.lineplot(
    data=plot1_data,
    x='L1_Int',
    y='Time',
    hue='MatrixSize',
    units='L1_Assoc',
    estimator=None,
    linewidth=1.5,
    alpha=0.35,
    legend=False
)
sns.lineplot(
    data=plot1_data,
    x='L1_Int',
    y='Time',
    hue='MatrixSize',
    linewidth=3,
    marker='o',
    palette='Dark2'
)

plt.xlabel("L1 Cache Size (kB)")
plt.ylabel("Execution Time (log scale)")
plt.yscale('log')
plt.xticks(l1_sorted)
plt.title(
    "Impact of L1 Cache Size on Execution Time",
    fontsize=16,
    weight='bold'
)

plt.legend(
    title="Matrix Size",
    loc="center left",
    bbox_to_anchor=(1.02, 0.5),
    frameon=True
)
plt.tight_layout()
plt.savefig(
    os.path.join(plot_output, 'plot_compare_l1_size_vs_time.png'),
    bbox_inches='tight'
)

print("Saved Plot 1 (L1 cache plot)")

plt.figure(figsize=(12, 7))

plot2_data = full_dataset[full_dataset['L1_Size'] == '16kB']

sns.lineplot(
    data=plot2_data,
    x='L2_Int',
    y='Time',
    hue='MatrixSize',
    units='L2_Assoc',
    estimator=None,
    linewidth=1.5,
    alpha=0.35,
    legend=False
)

sns.lineplot(
    data=plot2_data,
    x='L2_Int',
    y='Time',
    hue='MatrixSize',
    linewidth=3,
    marker='s',
    palette='tab10'
)

plt.xlabel("L2 Cache Size (kB)")
plt.ylabel("Execution Time (log scale)")
plt.yscale('log')
plt.xticks(l2_sorted)
plt.title(
    "Impact of L2 Cache Size on Execution Time (L1 Size = 16kB)",
    fontsize=16,
    weight='bold'
)

plt.legend(
    title="Matrix Size",
    loc="center left",
    bbox_to_anchor=(1.02, 0.5),
    frameon=True
)
plt.tight_layout()
plt.savefig(
    os.path.join(plot_output, 'plot_compare_l2_size_vs_time.png'),
    bbox_inches='tight'
)

print("Saved Plot 2 (L2 cache plot)")


fig = sns.catplot(
    data=full_dataset,
    x='L1_Assoc',
    y='L1_MissRate',
    hue='L1_Size',
    col='MatrixSize',
    kind='bar',
    palette='viridis',
    edgecolor='black',
    sharey=False,
    height=5, 
    aspect=0.8,
    legend_out=True
)

fig.fig.subplots_adjust(top=0.85) 
fig.fig.suptitle('L1 Miss Rate by Associativity and Matrix Size', fontsize=16, weight='bold')
fig.set_axis_labels("L1 Associativity", "L1 Miss Rate")
fig.set_titles("Matrix {col_name}x{col_name}")

plt.savefig(os.path.join(plot_output, 'plot_compare_l1_miss_rate.png'), bbox_inches='tight')
print("Saved Plot 3")

for matrix_dim in sorted(full_dataset['MatrixSize'].unique()):
    plt.figure(figsize=(10, 8))
    data_subset = full_dataset[full_dataset['MatrixSize'] == matrix_dim]
    
    heatmap_data = data_subset.pivot_table(index='L1_Size', columns='L2_Size', values='Time', aggfunc='mean')
    
    sns.heatmap(
        heatmap_data, 
        annot=True, 
        fmt=".4f", 
        cmap="viridis",
        linewidths=.5,
        linecolor='white'
    )
    plt.title(f'Mean Execution Time Heatmap (Matrix {matrix_dim}x{matrix_dim})', fontsize=16, weight='bold', pad=15)
    plt.xlabel('L2 Cache Size')
    plt.ylabel('L1 Cache Size')
    
    plt.tight_layout()
    plt.savefig(os.path.join(plot_output, f'plot_heatmap_time_{matrix_dim}x{matrix_dim}.png'))
    print(f"Saved Heatmap {matrix_dim}x{matrix_dim}")

print("\n--- Top 3 Fastest Configurations per Matrix Size ---")
for matrix_dim in sorted(full_dataset['MatrixSize'].unique()):
    print(f"\n--- Matrix Size: {matrix_dim}x{matrix_dim} ---")
    best_configs = full_dataset[full_dataset['MatrixSize'] == matrix_dim].sort_values('Time').head(3)
    print(best_configs[['L1_Size', 'L2_Size', 'L1_Assoc', 'L2_Assoc', 'Time']].to_string(index=False))

print("\nAnalysis complete. Plots generated with high-contrast colors.")