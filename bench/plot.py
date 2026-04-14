import csv
import matplotlib.pyplot as plt
import numpy as np

throughput = []
latency = []

with open("baseline.csv", "r") as f:
    reader = csv.DictReader(f)
    for row in reader:
        if row["type"] == "throughput":
            throughput.append((int(row["second"]), float(row["load_mt_s"])))
        elif row["type"] == "latency":
            latency.append({
                "load": float(row["load_mt_s"]),
                "p50": float(row["p50_us"]) if row["p50_us"] else 0,
                "p90": float(row["p90_us"]) if row["p90_us"] else 0,
                "p95": float(row["p95_us"]) if row["p95_us"] else 0,
                "p99": float(row["p99_us"]) if row["p99_us"] else 0,
                "p99_9": float(row["p99_9_us"]) if row["p99_9_us"] else 0,
                "p99_99": float(row["p99_99_us"]) if row["p99_99_us"] else 0,
                "worst": float(row["worst_us"]) if row["worst_us"] else 0,
            })

# sort latency by load
latency.sort(key=lambda x: x["load"])
tp_sec, tp_val = zip(*throughput) if throughput else ([], [])

fig, axes = plt.subplots(2, 1, figsize=(10, 10))

# --- Top: Throughput over time ---
ax1 = axes[0]
ax1.plot(tp_sec, tp_val, marker='o', markersize=3, linestyle='-', color='steelblue', label='Throughput')
ax1.axhline(y=np.mean(tp_val), color='red', linestyle='--', label=f'Average = {np.mean(tp_val):.2f} MT/s')
ax1.set_xlabel("Time (seconds)")
ax1.set_ylabel("Throughput (MT/s)")
ax1.set_title("exchange-core Throughput Baseline")
ax1.legend()
ax1.grid(True, alpha=0.3)

# --- Bottom: Latency vs Load ---
ax2 = axes[1]
loads = [d["load"] for d in latency]
metrics = [
    ("p50", "P50", "#2ca02c"),
    ("p90", "P90", "#98df8a"),
    ("p95", "P95", "#ffbb78"),
    ("p99", "P99", "#ff7f0e"),
    ("p99_9", "P99.9", "#d62728"),
    ("p99_99", "P99.99", "#9467bd"),
    ("worst", "Worst", "#8c564b"),
]

for key, label, color in metrics:
    vals = [d[key] for d in latency]
    ax2.plot(loads, vals, marker='o', markersize=3, label=label, color=color)

ax2.set_xlabel("Load (MT/s)")
ax2.set_ylabel("Latency (µs)")
ax2.set_title("exchange-core Latency Baseline")
ax2.set_yscale("log")
ax2.legend(loc='upper left')
ax2.grid(True, which="both", ls="-", alpha=0.3)

plt.tight_layout()
plt.savefig("baseline.jpg", dpi=150)
print("Saved baseline.jpg")
