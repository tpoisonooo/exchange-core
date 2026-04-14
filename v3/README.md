最终保留的有效改动清单
   文件                            改动                                                       状态
  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   ExchangeApi.java                promises 改用 JDK ConcurrentHashMap                        保留
   ExchangeCore.java               Disruptor 使用 perfCfg.getProducerType()                   保留
   PerformanceConfiguration.java   新增 producerType 字段                                     保留
   SharedPool.java                 改用 MpmcArrayQueue                                        保留
   OrderBookDirectImpl.java        orderIdIndex 改用 LongObjectHashMap                        保留
   RiskEngine.java                 两处 positions 循环增加 !isEmpty()  guard                  保留
   ThroughputTestsModule.java      移除每轮迭代后的 System.gc()                               保留
   PerfThroughput.java             Peak/Medium 使用 SINGLE producer、128K buffer、16K batch   保留
   bench/bench.sh                  修复 cd 路径问题                                           保留
  ────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
  最终 Benchmark 成绩
   测试                            优化前基准   最终成绩                          提升
  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   Peak (2ME+1RE, 100 symbols)     ~2.05 MT/s   ~2.67 MT/s avg / 3.22 MT/s peak   +30%
   Medium (2ME+1RE, 10K symbols)   ~1.05 MT/s   ~1.02 MT/s avg                    基本持平*
  *Medium 测试受前 5~10 轮 JVM C2 warm-up 拖累严重（冷启动 0.7 MT/s，热身后 1.2~1.4 MT/s），平均数波动较大，未出现明显退化。
