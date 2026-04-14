import re
import csv

log_path = "/home/konghuanjun/.kimi/sessions/e895e20b014220cbc5e5bd755fec0c7d/360bdf24-6a1c-4ddd-84ca-aed14d2fb734/tasks/bash-gkeeuhwd/output.log"

with open(log_path, "r", encoding="utf-8", errors="ignore") as f:
    lines = f.readlines()

# Parse throughput
throughput = []
tp_re = re.compile(r"ThroughputTestsModule\s+-\s+(\d+)\.\s+([\d.]+)\s+MT/s")
for line in lines:
    m = tp_re.search(line)
    if m:
        sec = int(m.group(1))
        val = float(m.group(2))
        throughput.append((sec, val))

# Parse latency (only after "Warmup done" or lines with load pattern)
latency = []
lat_re = re.compile(
    r"LatencyTestsModule\s+-\s+([\d.]+)\s+MT/s\s+\{"
    r"50\.0%=(.*?),\s+"
    r"90\.0%=(.*?),\s+"
    r"95\.0%=(.*?),\s+"
    r"99\.0%=(.*?),\s+"
    r"99\.9%=(.*?),\s+"
    r"99\.99%=(.*?),\s+"
    r"W=(.*?)\}"
)

# unit converter
def to_us(val_str):
    val_str = val_str.strip()
    if val_str.endswith("ms"):
        return float(val_str[:-2]) * 1000
    elif val_str.endswith("µs"):
        return float(val_str[:-2])
    elif val_str.endswith("us"):
        return float(val_str[:-2])
    elif val_str.endswith("s"):
        return float(val_str[:-1]) * 1_000_000
    else:
        return float(val_str)

warmup_done = False
for line in lines:
    if "Warmup done" in line:
        warmup_done = True
    m = lat_re.search(line)
    if m:
        # only keep post-warmup data for the main baseline
        if warmup_done:
            load = float(m.group(1))
            latency.append((
                load,
                to_us(m.group(2)),
                to_us(m.group(3)),
                to_us(m.group(4)),
                to_us(m.group(5)),
                to_us(m.group(6)),
                to_us(m.group(7)),
                to_us(m.group(8)),
            ))

# Write CSV
with open("baseline.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["type", "second", "load_mt_s", "p50_us", "p90_us", "p95_us", "p99_us", "p99_9_us", "p99_99_us", "worst_us"])
    for sec, val in throughput:
        writer.writerow(["throughput", sec, val, "", "", "", "", "", "", ""])
    for row in latency:
        writer.writerow(["latency", "", row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7]])

print(f"Wrote {len(throughput)} throughput rows and {len(latency)} latency rows to baseline.csv")
