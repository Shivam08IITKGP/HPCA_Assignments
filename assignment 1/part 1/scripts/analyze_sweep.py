import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Load Data
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(SCRIPT_DIR, '../results/full_sweep/full_sweep_results.csv')
df = pd.read_csv(DATA_PATH)

# Convert 'kB' strings to integers for proper sorting
df['L1_Int'] = df['L1_Size'].str.replace('kB','').astype(int)
df['L2_Int'] = df['L2_Size'].str.replace('kB','').astype(int)
df['L1_Assoc'] = df['L1_Assoc'].astype(int)
df['L2_Assoc'] = df['L2_Assoc'].astype(int)

# --- 1. Top 3 Configurations Table [cite: 411-414] ---
top3_time = df.sort_values('Time').head(3)[['L1_Size', 'L2_Size', 'L1_Assoc', 'L2_Assoc', 'Time']]
print("\n--- Top 3 Configs (Fastest Execution) ---")
print(top3_time.to_string(index=False))

top3_l1hit = df.sort_values('L1_MissRate').head(3)[['L1_Size', 'L2_Size', 'L1_Assoc', 'L2_Assoc', 'L1_MissRate']]
print("\n--- Top 3 Configs (Best L1 Hit Rate) ---")
print(top3_l1hit.to_string(index=False))

# --- 2. Generate Plots [cite: 406-409] ---
sns.set_style("whitegrid")

# Plot A: Impact of L1 Size (The "Cliff")
plt.figure(figsize=(10, 6))
# We filter for a fixed L2/Assoc to see the pure L1 size effect clearly
subset = df[(df['L2_Size'] == '256kB') & (df['L1_Assoc'] == 4)]
plt.plot(subset['L1_Int'], subset['Time'], marker='o', linewidth=2, color='blue')
plt.title('Impact of L1 Cache Size on Execution Time (Fixed L2=256k, Assoc=4)')
plt.xlabel('L1 Cache Size (kB)')
plt.ylabel('Execution Time (s)')
plt.xticks([16, 32, 64])
plt.savefig(os.path.join(SCRIPT_DIR, '../results/full_sweep/plot_l1_impact.png'))

# Plot B: Impact of Associativity (The "Anomaly")
plt.figure(figsize=(10, 6))
# Look at 64kB specifically, as that's where the interesting behavior is
subset_assoc = df[df['L1_Size'] == '64kB']
sns.barplot(data=subset_assoc, x='L1_Assoc', y='L1_MissRate', hue='L2_Size')
plt.title('Impact of L1 Associativity on Miss Rate (L1=64kB)')
plt.ylabel('L1 Miss Rate (Lower is Better)')
plt.savefig(os.path.join(SCRIPT_DIR, '../results/full_sweep/plot_assoc_impact.png'))

# Plot C: Impact of L2 Size (Diminishing Returns)
plt.figure(figsize=(10, 6))
# L2 matters most when L1 is small (16kB)
subset_l2 = df[df['L1_Size'] == '16kB']
sns.lineplot(data=subset_l2, x='L2_Size', y='Time', hue='L1_Assoc', marker='o')
plt.title('Impact of L2 Cache Size when L1 is Small (16kB)')
plt.ylabel('Execution Time (s)')
plt.savefig(os.path.join(SCRIPT_DIR, '../results/full_sweep/plot_l2_impact.png'))

print(f"\nPlots saved to {os.path.join(SCRIPT_DIR, '../results/full_sweep/')}")