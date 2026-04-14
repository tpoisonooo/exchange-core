summary = """
=== 当前机器实际配置 ===
CPU 型号:     Intel(R) Xeon(R) Platinum 8369B CPU @ 2.70GHz
架构:         Ice Lake-SP (Sunny Cove), x86_64
分配核心:     1 Socket × 4 Cores × 2 Threads = 8 vCPU
全核睿频:     ~3.5 GHz (网络资料)
内存容量:     30 GiB (可用 22 GiB)
指令集:       AVX-512, VNNI, DLBoost

=== 物理 CPU (Intel Xeon Platinum 8369B) 单颗理论峰值 ===
- 物理核心:      64 Cores / 128 Threads (阿里云 DDH 资料)
- FP64 峰值:     64c × 3.5 GHz × 32 FLOPs/cycle = 7,168 GFLOPS  ≈ 7.17 TFLOPS
- FP32 峰值:     64c × 3.5 GHz × 64 FLOPs/cycle = 14,336 GFLOPS ≈ 14.34 TFLOPS
- 内存带宽:      8通道 DDR4-3200 = 8 × 3200 × 8 = 204.8 GB/s (理论峰值)
- UPI 互联:      3× 11.2 GT/s
- L3 Cache:      ~1.5 MB/core × 64 = 96 MB (Ice Lake 典型值)

=== 当前实例 (8 vCPU / 4物理核) 按比例理论峰值 ===
- FP64 峰值:     4c × 3.5 GHz × 32 = 448 GFLOPS
- FP32 峰值:     4c × 3.5 GHz × 64 = 896 GFLOPS
- 整数寄存器吞吐: 4c × 3.5 GHz × 64 bytes/cycle = 896 GB/s (AVX-512 寄存器级)
- 实际内存带宽:  云实例通常共享物理内存通道，8 vCPU 实例实测/可用带宽
                 估算约 20–60 GB/s (远低于物理机 204.8 GB/s)

注：exchange-core 属于内存密集型/延迟敏感型负载（撮合引擎），
    实际性能主要由内存延迟、缓存命中率和 CPU 单核频率决定，
    而非浮点峰值。当前 ~4.87 MT/s 的吞吐表现已非常优秀。
"""
print(summary)
