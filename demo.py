#!/usr/bin/env python3
"""
快速演示脚本
展示链上分析工具的核心功能
"""

import sys
sys.path.insert(0, '/home/user/brainstorm')

from crypto_onchain_analyzer.data.data_loader import DataLoader
from crypto_onchain_analyzer.indicators.onchain_metrics import OnChainMetrics
from crypto_onchain_analyzer.utils.visualizer import TerminalVisualizer
from crypto_onchain_analyzer.utils.report_generator import ReportGenerator


def main():
    print("""
╔══════════════════════════════════════════════════════════════════════╗
║           🔗 Crypto On-Chain Analyzer - 快速演示                      ║
║           链上数据分析工具演示程序                                      ║
╚══════════════════════════════════════════════════════════════════════╝
    """)

    # 1. 加载示例数据
    print("📊 步骤 1: 生成示例数据 (365天)")
    print("=" * 70)

    loader = DataLoader()
    snapshots = loader.create_sample_snapshot_data(365)

    print(f"✓ 已生成 {len(snapshots)} 天的链上快照数据")
    print(f"  价格范围: ${snapshots[0].price:.2f} - ${max(s.price for s in snapshots):.2f}")
    print(f"  时间范围: {snapshots[0].timestamp.date()} 到 {snapshots[-1].timestamp.date()}")

    # 2. 计算核心指标
    print("\n\n📈 步骤 2: 计算核心链上指标")
    print("=" * 70)

    metrics = OnChainMetrics()
    viz = TerminalVisualizer()

    latest = snapshots[-1]

    # MVRV
    mvrv = metrics.calculate_mvrv(latest.market_cap, latest.realized_cap)
    print(f"\n✓ MVRV (Market Value to Realized Value): {mvrv:.4f}")
    if mvrv > 3.7:
        print("  ⚠️  警告: 极度高估区域")
    elif mvrv > 2.4:
        print("  ⚠️  注意: 可能过热")
    elif mvrv < 1.0:
        print("  ✅ 机会: 历史低估区域")
    else:
        print("  ✓  正常: 合理估值范围")

    # NUPL
    nupl = metrics.calculate_nupl(latest.market_cap, latest.realized_cap, latest.circulating_supply)
    print(f"\n✓ NUPL (Net Unrealized Profit/Loss): {nupl:.4f}")
    if nupl > 0.75:
        print("  😰 市场情绪: 贪婪/狂热")
    elif nupl > 0.5:
        print("  🤔 市场情绪: 乐观/焦虑")
    elif nupl > 0.25:
        print("  😐 市场情绪: 希望/恐惧")
    elif nupl > 0:
        print("  😟 市场情绪: 投降/愤怒")
    else:
        print("  😱 市场情绪: 极度恐慌")

    # NVT
    nvt = metrics.calculate_nvt_signal(snapshots)
    print(f"\n✓ NVT Signal (Network Value to Transactions): {nvt:.2f}")
    if nvt > 100:
        print("  ⚠️  相对使用量高估")
    elif nvt < 50:
        print("  ✅ 相对使用量低估")
    else:
        print("  ✓  合理估值")

    # 3. 可视化展示
    print("\n\n📊 步骤 3: 数据可视化")
    print("=" * 70)

    # 价格趋势
    prices = [s.price for s in snapshots[-90:]]
    print("\n价格趋势 (最近90天):")
    print(viz.create_line_chart(prices, 70, 15, "Bitcoin Price (USD)"))

    # MVRV趋势
    mvrv_history = [metrics.calculate_mvrv(s.market_cap, s.realized_cap)
                   for s in snapshots[-90:]]
    print("\n\nMVRV趋势 (最近90天):")
    print(viz.create_line_chart(mvrv_history, 70, 15, "MVRV Ratio"))

    # 迷你图
    print("\n\n快速趋势指示 (Sparklines):")
    print(f"价格 (90d):     {viz.create_sparkline(prices, 50)}")
    print(f"MVRV (90d):     {viz.create_sparkline(mvrv_history, 50)}")
    active = [s.active_addresses for s in snapshots[-90:]]
    print(f"活跃地址 (90d): {viz.create_sparkline(active, 50)}")

    # 4. 仪表盘
    print("\n\n🎯 步骤 4: 指标仪表盘")
    print("=" * 70)

    print(viz.create_gauge(mvrv, 0, 5, 60, "MVRV Gauge",
                          [(1.0, "Undervalued", '░'),
                           (2.4, "Fair Value", '▒'),
                           (5.0, "Overvalued", '▓')]))

    print("\n")
    print(viz.create_gauge(nupl, -0.5, 1.0, 60, "NUPL Gauge",
                          [(0, "Capitulation", '░'),
                           (0.5, "Hope/Fear", '▒'),
                           (1.0, "Greed", '▓')]))

    # 5. 统计表格
    print("\n\n📋 步骤 5: 关键指标汇总")
    print("=" * 70)

    headers = ["指标", "当前值", "状态", "说明"]
    rows = [
        ["MVRV", f"{mvrv:.4f}", "正常" if 1 < mvrv < 2.4 else "异常", "市场估值"],
        ["NUPL", f"{nupl:.4f}", "中性" if 0.25 < nupl < 0.75 else "极端", "盈亏状态"],
        ["NVT", f"{nvt:.2f}", "正常" if nvt < 100 else "高估", "网络价值"],
        ["价格", f"${latest.price:,.0f}", "跟踪中", "当前BTC价格"],
        ["市值", f"${latest.market_cap/1e9:.1f}B", "跟踪中", "总市值"],
    ]

    print(viz.create_table(headers, rows, "核心指标概览"))

    # 6. 生成完整报告
    print("\n\n📑 步骤 6: 生成完整分析报告")
    print("=" * 70)
    print("\n正在生成完整报告...\n")

    # 生成示例地址数据
    from crypto_onchain_analyzer.cli import generate_sample_addresses
    addresses = generate_sample_addresses()

    generator = ReportGenerator()
    report = generator.generate_full_report(snapshots, addresses, None, None)

    print(report)

    # 总结
    print("\n\n" + "=" * 70)
    print("✅ 演示完成!")
    print("=" * 70)
    print("""
你刚刚看到了:
  1. ✓ 链上数据生成和加载
  2. ✓ 核心指标计算 (MVRV, NUPL, NVT等)
  3. ✓ 多种可视化方式 (线图, 仪表盘, 迷你图)
  4. ✓ 完整的分析报告生成

下一步:
  • 导入真实的链上数据进行分析
  • 开发自定义的量化策略
  • 添加更多指标和分析维度
  • 集成到交易系统中

运行完整功能:
  python -m crypto_onchain_analyzer.cli report --demo
  python -m crypto_onchain_analyzer.cli interactive

查看文档:
  cat README.md
    """)


if __name__ == '__main__':
    main()
