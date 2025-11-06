#!/usr/bin/env python3
"""
命令行接口
"""
import argparse
import sys
from pathlib import Path
from datetime import datetime

from .data.data_loader import DataLoader
from .utils.report_generator import ReportGenerator
from .indicators.onchain_metrics import OnChainMetrics
from .utils.visualizer import TerminalVisualizer


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='Crypto On-Chain Analyzer - 链上数据分析工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 生成完整报告（使用示例数据）
  python -m crypto_onchain_analyzer.cli report --demo

  # 从CSV加载数据并生成报告
  python -m crypto_onchain_analyzer.cli report --snapshots data/snapshots.csv

  # 生成示例数据
  python -m crypto_onchain_analyzer.cli generate --days 365 --output data/

  # 计算单个指标
  python -m crypto_onchain_analyzer.cli metric --type mvrv --snapshots data/snapshots.csv

  # 交互式模式
  python -m crypto_onchain_analyzer.cli interactive
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='可用命令')

    # 报告生成命令
    report_parser = subparsers.add_parser('report', help='生成链上分析报告')
    report_parser.add_argument('--demo', action='store_true', help='使用示例数据')
    report_parser.add_argument('--snapshots', type=str, help='快照数据CSV文件路径')
    report_parser.add_argument('--addresses', type=str, help='地址数据CSV文件路径')
    report_parser.add_argument('--exchanges', type=str, help='交易所流动CSV文件路径')
    report_parser.add_argument('--miners', type=str, help='矿工数据CSV文件路径')
    report_parser.add_argument('--output', type=str, help='输出文件路径')

    # 数据生成命令
    gen_parser = subparsers.add_parser('generate', help='生成示例数据')
    gen_parser.add_argument('--days', type=int, default=365, help='生成天数（默认365）')
    gen_parser.add_argument('--output', type=str, required=True, help='输出目录')

    # 指标计算命令
    metric_parser = subparsers.add_parser('metric', help='计算单个指标')
    metric_parser.add_argument('--type', type=str, required=True,
                              choices=['mvrv', 'nupl', 'sopr', 'nvt', 'puell'],
                              help='指标类型')
    metric_parser.add_argument('--snapshots', type=str, required=True, help='快照数据CSV')
    metric_parser.add_argument('--transactions', type=str, help='交易数据JSON（SOPR需要）')

    # 交互式模式
    interactive_parser = subparsers.add_parser('interactive', help='交互式分析模式')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    try:
        if args.command == 'report':
            generate_report_command(args)
        elif args.command == 'generate':
            generate_data_command(args)
        elif args.command == 'metric':
            calculate_metric_command(args)
        elif args.command == 'interactive':
            interactive_mode()
    except Exception as e:
        print(f"\n❌ 错误: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


def generate_report_command(args):
    """生成报告命令"""
    loader = DataLoader()
    generator = ReportGenerator()

    print("📊 正在加载数据...")

    if args.demo:
        # 使用示例数据
        print("使用演示数据（365天模拟数据）")
        snapshots = loader.create_sample_snapshot_data(365)
        addresses = generate_sample_addresses()
        exchange_flows = generate_sample_exchange_flows()
        miner_data = generate_sample_miner_data()
    else:
        # 从文件加载
        if not args.snapshots:
            print("❌ 错误: 请提供 --snapshots 参数或使用 --demo")
            sys.exit(1)

        snapshots = loader.load_snapshots_from_csv(args.snapshots)
        addresses = loader.load_addresses_from_csv(args.addresses) if args.addresses else None
        exchange_flows = loader.load_exchange_flows_from_csv(args.exchanges) if args.exchanges else None
        miner_data = loader.load_miner_data_from_csv(args.miners) if args.miners else None

    print(f"✓ 已加载 {len(snapshots)} 个快照")
    if addresses:
        print(f"✓ 已加载 {len(addresses)} 个地址")
    if exchange_flows:
        print(f"✓ 已加载 {len(exchange_flows)} 条交易所流动记录")
    if miner_data:
        print(f"✓ 已加载 {len(miner_data)} 条矿工数据")

    print("\n🔍 正在分析数据并生成报告...\n")

    # 生成报告
    report = generator.generate_full_report(snapshots, addresses, exchange_flows, miner_data)

    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"\n✅ 报告已保存到: {args.output}")
    else:
        print(report)


def generate_data_command(args):
    """生成示例数据命令"""
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"📦 正在生成 {args.days} 天的示例数据...")

    loader = DataLoader()

    # 生成快照数据
    snapshots = loader.create_sample_snapshot_data(args.days)
    snapshot_file = output_dir / 'snapshots.csv'

    with open(snapshot_file, 'w') as f:
        f.write('timestamp,price,market_cap,realized_cap,circulating_supply,active_addresses,new_addresses,transaction_count,transaction_volume,total_fees,avg_fee,miner_revenue,hash_rate,difficulty\n')
        for s in snapshots:
            f.write(f"{s.timestamp.isoformat()},{s.price},{s.market_cap},{s.realized_cap},{s.circulating_supply},{s.active_addresses},{s.new_addresses},{s.transaction_count},{s.transaction_volume},{s.total_fees},{s.avg_fee},{s.miner_revenue},{s.hash_rate},{s.difficulty}\n")

    print(f"✓ 快照数据: {snapshot_file}")

    # 生成地址数据
    addresses = generate_sample_addresses()
    address_file = output_dir / 'addresses.csv'

    with open(address_file, 'w') as f:
        f.write('address,balance,first_seen,last_active,transaction_count,total_received,total_sent\n')
        for a in addresses:
            f.write(f"{a.address},{a.balance},{a.first_seen.isoformat()},{a.last_active.isoformat()},{a.transaction_count},{a.total_received},{a.total_sent}\n")

    print(f"✓ 地址数据: {address_file}")

    print(f"\n✅ 示例数据已生成到: {output_dir}")


def calculate_metric_command(args):
    """计算指标命令"""
    loader = DataLoader()
    metrics = OnChainMetrics()
    viz = TerminalVisualizer()

    print(f"📊 正在计算 {args.type.upper()} 指标...")

    snapshots = loader.load_snapshots_from_csv(args.snapshots)
    print(f"✓ 已加载 {len(snapshots)} 个快照\n")

    if args.type == 'mvrv':
        latest = snapshots[-1]
        mvrv = metrics.calculate_mvrv(latest.market_cap, latest.realized_cap or latest.market_cap * 0.7)
        mvrv_z = metrics.calculate_mvrv_z_score(snapshots)

        print(f"MVRV Ratio: {mvrv:.4f}")
        print(f"MVRV Z-Score: {mvrv_z:.4f}\n")

        # 历史趋势
        mvrv_history = [metrics.calculate_mvrv(s.market_cap, s.realized_cap or s.market_cap * 0.7)
                       for s in snapshots[-90:]]
        print("MVRV 趋势 (90天):")
        print(viz.create_line_chart(mvrv_history, 70, 15, "MVRV Ratio"))

    elif args.type == 'nupl':
        latest = snapshots[-1]
        nupl = metrics.calculate_nupl(latest.market_cap, latest.realized_cap or latest.market_cap * 0.7,
                                     latest.circulating_supply)
        print(f"NUPL: {nupl:.4f}\n")
        print(viz.create_gauge(nupl, -0.5, 1.0, 60, "NUPL Gauge"))

    elif args.type == 'nvt':
        nvt = metrics.calculate_nvt_signal(snapshots)
        print(f"NVT Signal: {nvt:.4f}")

    elif args.type == 'sopr':
        if not args.transactions:
            print("❌ 错误: SOPR计算需要 --transactions 参数")
            sys.exit(1)
        # TODO: 实现SOPR计算
        print("SOPR计算需要交易数据")


def interactive_mode():
    """交互式模式"""
    print("""
╔════════════════════════════════════════════════════════════════╗
║     Crypto On-Chain Analyzer - 交互式模式                       ║
║     v1.0.0                                                     ║
╚════════════════════════════════════════════════════════════════╝

可用命令:
  1. demo         - 运行演示报告
  2. metrics      - 查看可用指标列表
  3. help         - 显示帮助
  4. exit         - 退出

    """)

    while True:
        try:
            cmd = input(">>> ").strip().lower()

            if cmd == 'exit' or cmd == 'quit':
                print("再见!")
                break
            elif cmd == 'demo':
                print("\n正在生成演示报告...\n")
                loader = DataLoader()
                generator = ReportGenerator()
                snapshots = loader.create_sample_snapshot_data(365)
                addresses = generate_sample_addresses()
                report = generator.generate_full_report(snapshots, addresses, None, None)
                print(report)
            elif cmd == 'metrics':
                print_available_metrics()
            elif cmd == 'help':
                print("输入命令名称执行相应功能")
            else:
                print(f"未知命令: {cmd}. 输入 'help' 查看帮助")

        except KeyboardInterrupt:
            print("\n\n再见!")
            break
        except EOFError:
            break


def print_available_metrics():
    """打印可用指标"""
    print("""
╔════════════════════════════════════════════════════════════════╗
║                    可用链上指标                                 ║
╚════════════════════════════════════════════════════════════════╝

估值指标:
  • MVRV (Market Value to Realized Value)
  • MVRV Z-Score
  • NUPL (Net Unrealized Profit/Loss)
  • NVT (Network Value to Transactions)
  • RVT (Realized Value to Transactions)
  • Reserve Risk

活动指标:
  • Active Addresses
  • New Addresses Growth
  • Transaction Volume
  • Fee Analysis

矿工指标:
  • Puell Multiple
  • Miner Position Index
  • Hash Ribbons
  • Difficulty Ribbon

交易所指标:
  • Exchange Net Flow
  • Exchange Reserve Ratio
  • Accumulation/Distribution Phase

地址指标:
  • Supply Distribution
  • Whale Tracking
  • Gini Coefficient
  • Dormancy Analysis
  • HODL Waves
    """)


def generate_sample_addresses():
    """生成示例地址数据"""
    import random
    from datetime import timedelta
    from crypto_onchain_analyzer.core.models import AddressBalance

    addresses = []
    base_date = datetime(2020, 1, 1)

    # 生成各种类型的地址
    for i in range(100):
        if i < 5:  # 巨鲸
            balance = random.uniform(1000, 10000)
        elif i < 20:  # 大户
            balance = random.uniform(100, 1000)
        elif i < 50:  # 中户
            balance = random.uniform(10, 100)
        else:  # 小户
            balance = random.uniform(0.1, 10)

        first_seen = base_date + timedelta(days=random.randint(0, 1000))
        last_active = first_seen + timedelta(days=random.randint(1, 1000))

        addr = AddressBalance(
            address=f"bc1q{''.join(random.choices('0123456789abcdef', k=40))}",
            balance=balance,
            first_seen=first_seen,
            last_active=last_active,
            transaction_count=random.randint(1, 500),
            total_received=balance * random.uniform(1.5, 3.0),
            total_sent=balance * random.uniform(0.5, 1.5)
        )
        addresses.append(addr)

    return addresses


def generate_sample_exchange_flows():
    """生成示例交易所流动数据"""
    import random
    from datetime import timedelta
    from crypto_onchain_analyzer.core.models import ExchangeFlow

    flows = []
    base_date = datetime(2024, 1, 1)
    exchanges = ['Binance', 'Coinbase', 'Kraken', 'Bitfinex', 'Gemini']

    for day in range(90):
        for exchange in exchanges:
            inflow = random.uniform(500, 2000)
            outflow = random.uniform(500, 2000)
            reserve = random.uniform(50000, 150000)

            flow = ExchangeFlow(
                timestamp=base_date + timedelta(days=day),
                exchange_name=exchange,
                inflow=inflow,
                outflow=outflow,
                net_flow=inflow - outflow,
                reserve=reserve
            )
            flows.append(flow)

    return flows


def generate_sample_miner_data():
    """生成示例矿工数据"""
    import random
    from datetime import timedelta
    from crypto_onchain_analyzer.core.models import MinerData

    miner_data = []
    base_date = datetime(2024, 1, 1)
    miners = [f"miner_{i}" for i in range(5)]

    for day in range(365):
        for miner in miners:
            data = MinerData(
                timestamp=base_date + timedelta(days=day),
                miner_address=miner,
                revenue=random.uniform(15, 35),
                fees_collected=random.uniform(1, 5),
                coins_moved=random.uniform(0, 50),
                reserve=random.uniform(1000, 5000)
            )
            miner_data.append(data)

    return miner_data


if __name__ == '__main__':
    main()
