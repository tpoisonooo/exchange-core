  本轮优化总结
   改动                                                              结果
  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   LongObjectHashMap 替换 LongAdaptiveRadixTreeMap（orderIdIndex）   ✅ 保留，Peak 基线从 ~2.36 提升到 ~2.58 MT/s
   EVENTS_POOLING 重开 + 取出清零修复                                ✅ 保留，消除第二大 alloc 热点，无性能回归，功能测试全绿
   GROUP_SPIN_LIMIT 5K→20K                                           ❌ 废弃，无收益且波动变大
   MASTER_SPIN_LIMIT 20K→100K                                        ❌ 废弃，已回退
   价格桶换 LongObjectSortedMap                                      ❌ 废弃，无提升
   l2RefreshDepth = 0                                                ❌ 废弃，掉速 ~7.5% 已回退
  最终性能基线（8 vCPU / 2ME+1RE / ProducerType.SINGLE）
  • Peak：~2.58–2.65 MT/s 平均
  • Medium：~0.93 MT/s 平均

  工作区已干净待提交，你自己 git add 即可
