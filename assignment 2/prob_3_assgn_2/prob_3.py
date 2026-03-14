#!/usr/bin/env python3
# prob_3.py — Run from inside /home/shivam/Projects/cacti-master/
# Usage: python3 prob_3.py > prob_3.log

import subprocess, os, re, sys
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

CACTI      = "./cacti"
BASE_CFG   = "./cache.cfg"
CFG_DIR    = "./prob3_configs"
PLOT_FILE  = "./prob_3_fig28.png"

SIZES      = [16*1024, 32*1024, 64*1024, 128*1024, 256*1024]
LABELS     = ["16 KB", "32 KB", "64 KB", "128 KB", "256 KB"]
ASSOCS     = [1, 2, 4, 8]

os.makedirs(CFG_DIR, exist_ok=True)

def make_config(size, assoc, path):
    with open(BASE_CFG) as f:
        cfg = f.read()
    # Disable all existing size/associativity lines
    cfg = re.sub(r'^(-size)',       r'//\1', cfg, flags=re.MULTILINE)
    cfg = re.sub(r'^(-associativity)', r'//\1', cfg, flags=re.MULTILINE)
    # Inject our values at the top
    cfg = f"-size (bytes) {size}\n-associativity {assoc}\n" + cfg
    with open(path, 'w') as f:
        f.write(cfg)

def run_cacti(path):
    r = subprocess.run([CACTI, "-infile", path],
                       capture_output=True, text=True, timeout=120)
    return r.stdout + r.stderr

def parse_time(output):
    m = re.search(r'Access time \(ns\):\s*([\d.]+)', output)
    return float(m.group(1)) if m else None

# ── Run all 20 configurations ──────────────────────────────────────────────
print("=" * 65)
print("Problem 3: CACTI — Cache Access Time vs Size (Fig 2.8)")
print("=" * 65)
print()

results = {a: [None]*len(SIZES) for a in ASSOCS}

for assoc in ASSOCS:
    for i, size in enumerate(SIZES):
        size_kb  = size // 1024
        cfg_path = f"{CFG_DIR}/cache_{size_kb}KB_{assoc}way.cfg"

        print(f"--- {size_kb} KB, {assoc}-way ---")
        print(f"    Config : {cfg_path}")

        make_config(size, assoc, cfg_path)
        output = run_cacti(cfg_path)
        t = parse_time(output)

        if t:
            results[assoc][i] = t
            print(f"    Access time : {t:.5f} ns")
        else:
            print(f"    WARNING: Could not parse. Raw:\n{output[:400]}")
            results[assoc][i] = 0.0
        print()

# ── Summary table ──────────────────────────────────────────────────────────
print("=" * 65)
print("SUMMARY TABLE — Access Time (ns)")
print("=" * 65)
hdr = f"{'Assoc':<8}" + "".join(f"{l:>10}" for l in LABELS)
print(hdr)
print("-" * len(hdr))
for a in ASSOCS:
    row = f"{str(a)+'-way':<8}"
    for i in range(len(SIZES)):
        v = results[a][i]
        row += f"{v:>10.4f}" if v else f"{'N/A':>10}"
    print(row)
print("=" * 65)
print()

# ── Plot ───────────────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(10, 6))

x       = np.arange(len(SIZES))
width   = 0.18
offsets = np.array([-1.5, -0.5, 0.5, 1.5]) * width
colors  = ['#e41a1c', '#377eb8', '#4daf4a', '#ff7f00']  # red, blue, green, orange
labels  = ['1-way', '2-way', '4-way', '8-way']

for idx, assoc in enumerate(ASSOCS):
    vals = [results[assoc][i] or 0 for i in range(len(SIZES))]
    ax.bar(x + offsets[idx], vals, width,
           label=labels[idx], color=colors[idx],
           edgecolor='black', linewidth=0.6)

ax.set_xlabel("Cache size", fontsize=12)
ax.set_ylabel("Access time (ns)", fontsize=12)
ax.set_title("Cache Access Time vs Cache Size\n(Fig 2.8 — CACTI 7.0, 90nm, 64B blocks)", fontsize=12)
ax.set_xticks(x)
ax.set_xticklabels(LABELS, fontsize=11)
ax.legend(title="Associativity", fontsize=10)
ax.grid(axis='y', linestyle='--', alpha=0.4)
ax.set_ylim(bottom=0)

plt.tight_layout()
plt.savefig(PLOT_FILE, dpi=150, bbox_inches='tight')
print(f"Plot saved : {PLOT_FILE}")
print("Done.")