import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# --- CONFIGURATION ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# Adjust this path if your results are in a different relative location
RESULTS_DIR = os.path.join(SCRIPT_DIR, '../results')
OUTPUT_DIR = os.path.join(RESULTS_DIR, 'analysis_all')
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Data sources for the different matrix sizes
data_sources = {
    64: os.path.join(RESULTS_DIR, 'full_sweep_64/full_sweep_results_64.csv'),
    128: os.path.join(RESULTS_DIR, 'full_sweep/full_sweep_results.csv'),
    256: os.path.join(RESULTS_DIR, 'full_sweep_256/full_sweep_results_256.csv')
}

# --- LOAD AND COMBINE DATA ---
all_data = []
for size, path in data_sources.items():
    if os.path.exists(path):
        try:
            df = pd.read_csv(path)
            df['MatrixSize'] = size
            all_data.append(df)
            print(f"Loaded data for Matrix {size}")
        except Exception as e:
            print(f"Error reading {path}: {e}")
    else:
        print(f"Warning: File not found: {path}")

if not all_data:
    print("Error: No data files found. Exiting.")
    exit(1)

df_combined = pd.concat(all_data, ignore_index=True)

# --- DATA PREPARATION ---
# Clean strings and convert to integers
df_combined['L1_Int'] = df_combined['L1_Size'].str.replace('kB','').astype(int)
df_combined['L2_Int'] = df_combined['L2_Size'].str.replace('kB','').astype(int)
df_combined['L1_Assoc'] = df_combined['L1_Assoc'].astype(int)
df_combined['L2_Assoc'] = df_combined['L2_Assoc'].astype(int)

# Convert Time to numeric
df_combined['Time'] = pd.to_numeric(df_combined['Time'], errors='coerce')
df_combined.dropna(subset=['Time'], inplace=True)

# --- SORTING SETUP (CRITICAL FOR HEATMAPS) ---
# Create ordered categories so heatmaps sort 16->32->64, not 128->16->256
l1_order = sorted(df_combined['L1_Int'].unique())
l2_order = sorted(df_combined['L2_Int'].unique())
l1_labels = [f"{x}kB" for x in l1_order]
l2_labels = [f"{x}kB" for x in l2_order]

df_combined['L1_Size'] = pd.Categorical(df_combined['L1_Size'], categories=l1_labels, ordered=True)
df_combined['L2_Size'] = pd.Categorical(df_combined['L2_Size'], categories=l2_labels, ordered=True)

# Set global style
sns.set_theme(style="whitegrid", font_scale=1.1)

# --- PLOT 1: L1 Size vs. Execution Time (Comparative) ---
plt.figure(figsize=(12, 7))
sns.lineplot(
    data=df_combined[df_combined['L2_Size'] == '256kB'],
    x='L1_Int',
    y='Time',
    hue='MatrixSize',
    style='L1_Assoc',
    marker='o',
    markersize=8,  # Make markers bigger
    palette='Dark2', # High contrast palette (Dark Green, Orange, Purple)
    linewidth=3
)

plt.xlabel('L1 Cache Size (kB)', fontsize=12)
plt.ylabel('Execution Time (log scale)', fontsize=12)
plt.yscale('log')
plt.xticks(l1_order)
# Move legend
plt.legend(title='Matrix Size / L1 Assoc', bbox_to_anchor=(1.02, 1), loc='upper left', borderaxespad=0)
plt.title('Impact of L1 Cache Size on Execution Time', fontsize=16, weight='bold')
plt.tight_layout() # This works better now that legend is anchored
plt.savefig(os.path.join(OUTPUT_DIR, 'plot_compare_l1_size_vs_time.png'), bbox_inches='tight')
print("Saved Plot 1")

# --- PLOT 2: L2 Size vs. Execution Time (Comparative) ---
plt.figure(figsize=(12, 7))
sns.lineplot(
    data=df_combined[df_combined['L1_Size'] == '16kB'],
    x='L2_Int',
    y='Time',
    hue='MatrixSize',
    style='L2_Assoc',
    marker='s', # Square marker
    markersize=8,
    palette='tab10', # Another high contrast palette
    linewidth=3
)
plt.title('Impact of L2 Cache Size on Execution Time (L1 Size = 16kB)', fontsize=16, weight='bold')
plt.xlabel('L2 Cache Size (kB)', fontsize=12)
plt.ylabel('Execution Time (log scale)', fontsize=12)
plt.yscale('log')
plt.xticks(l2_order)
plt.legend(title='Matrix Size / L2 Assoc', bbox_to_anchor=(1.02, 1), loc='upper left')
plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, 'plot_compare_l2_size_vs_time.png'), bbox_inches='tight')
print("Saved Plot 2")

# --- PLOT 3: L1 Miss Rate vs. Matrix Size (Faceted) ---
g = sns.catplot(
    data=df_combined,
    x='L1_Assoc',
    y='L1_MissRate',
    hue='L1_Size',
    col='MatrixSize',
    kind='bar',
    palette='viridis', # Darker blues/greens, readable on white
    edgecolor='black', # Add black border to bars for visibility
    sharey=False,
    height=5, 
    aspect=0.8,
    legend_out=True
)

g.fig.subplots_adjust(top=0.85) 
g.fig.suptitle('L1 Miss Rate by Associativity and Matrix Size', fontsize=16, weight='bold')
g.set_axis_labels("L1 Associativity", "L1 Miss Rate")
g.set_titles("Matrix {col_name}x{col_name}")

plt.savefig(os.path.join(OUTPUT_DIR, 'plot_compare_l1_miss_rate.png'), bbox_inches='tight')
print("Saved Plot 3")

# --- PLOT 4: Performance Heatmap ---
# Ensure we iterate over sorted unique values
for size in sorted(df_combined['MatrixSize'].unique()):
    plt.figure(figsize=(10, 8))
    subset = df_combined[df_combined['MatrixSize'] == size]
    
    # Pivot table will now respect the Categorical ordering we set earlier
    pivot = subset.pivot_table(index='L1_Size', columns='L2_Size', values='Time', aggfunc='mean')
    
    sns.heatmap(
        pivot, 
        annot=True, 
        fmt=".4f", 
        cmap="viridis", # High contrast gradient
        linewidths=.5,
        linecolor='white'
    )
    plt.title(f'Mean Execution Time Heatmap (Matrix {size}x{size})', fontsize=16, weight='bold', pad=15)
    plt.xlabel('L2 Cache Size')
    plt.ylabel('L1 Cache Size')
    
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, f'plot_heatmap_time_{size}x{size}.png'))
    print(f"Saved Heatmap {size}x{size}")

# --- Summary Tables ---
print("\n--- Top 3 Fastest Configurations per Matrix Size ---")
for size in sorted(df_combined['MatrixSize'].unique()):
    print(f"\n--- Matrix Size: {size}x{size} ---")
    # Sort by time to find fastest
    top3 = df_combined[df_combined['MatrixSize'] == size].sort_values('Time').head(3)
    print(top3[['L1_Size', 'L2_Size', 'L1_Assoc', 'L2_Assoc', 'Time']].to_string(index=False))

print("\nAnalysis complete. Plots generated with high-contrast colors.")