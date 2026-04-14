#!/bin/bash
set -e

echo "======================================"
echo "exchange-core 并发性能测试脚本"
echo "======================================"

# 1. 编译项目
echo "[1/3] 编译项目..."
mvn clean compile -q

# 2. 运行各项性能测试
echo "[2/3] 吞吐量测试 (Throughput)..."
mvn -Dtest=PerfThroughput#testThroughputMargin test

echo "[3/3] 延迟测试 (Latency)..."
mvn -Dtest=PerfLatency#testLatencyMargin test

echo "======================================"
echo "全部测试完成"
echo "======================================"
