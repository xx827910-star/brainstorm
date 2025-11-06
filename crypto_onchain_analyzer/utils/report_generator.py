"""
报告生成器
生成全面的链上分析报告
"""
from typing import List, Dict
from datetime import datetime
from ..core.models import OnChainSnapshot, AddressBalance, ExchangeFlow, MinerData
from ..indicators.onchain_metrics import OnChainMetrics
from ..indicators.exchange_analytics import ExchangeAnalytics
from ..indicators.miner_analytics import MinerAnalytics
from ..indicators.address_analytics import AddressAnalytics
from .visualizer import TerminalVisualizer


class ReportGenerator:
    """报告生成器"""

    def __init__(self):
        self.viz = TerminalVisualizer()
        self.metrics = OnChainMetrics()
        self.exchange_analytics = ExchangeAnalytics()
        self.miner_analytics = MinerAnalytics()
        self.address_analytics = AddressAnalytics()

    def generate_full_report(self,
                           snapshots: List[OnChainSnapshot],
                           addresses: List[AddressBalance] = None,
                           exchange_flows: List[ExchangeFlow] = None,
                           miner_data: List[MinerData] = None) -> str:
        """
        生成完整的链上分析报告

        Args:
            snapshots: 链上快照数据
            addresses: 地址数据（可选）
            exchange_flows: 交易所流动（可选）
            miner_data: 矿工数据（可选）

        Returns:
            完整报告文本
        """
        sections = []

        # 标题
        sections.append(self._generate_header())

        # 1. 概览
        sections.append(self._generate_overview(snapshots))

        # 2. 价值指标
        sections.append(self._generate_valuation_metrics(snapshots))

        # 3. 网络活动
        sections.append(self._generate_network_activity(snapshots))

        # 4. 地址分析
        if addresses:
            sections.append(self._generate_address_analysis(addresses, snapshots))

        # 5. 交易所分析
        if exchange_flows:
            sections.append(self._generate_exchange_analysis(exchange_flows, snapshots))

        # 6. 矿工分析
        if miner_data:
            sections.append(self._generate_miner_analysis(miner_data, snapshots))

        # 7. 市场信号总结
        sections.append(self._generate_market_signals(snapshots, addresses, exchange_flows, miner_data))

        # 页脚
        sections.append(self._generate_footer())

        return '\n\n'.join(sections)

    def _generate_header(self) -> str:
        """生成报告头"""
        header = f"""
{'=' * 100}
{'CRYPTO ON-CHAIN ANALYSIS REPORT':^100}
{'=' * 100}
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
{'=' * 100}
"""
        return header

    def _generate_overview(self, snapshots: List[OnChainSnapshot]) -> str:
        """生成概览部分"""
        if not snapshots:
            return "## OVERVIEW\nNo data available"

        latest = snapshots[-1]
        prev_30d = snapshots[-30] if len(snapshots) >= 30 else snapshots[0]

        price_change = (latest.price - prev_30d.price) / prev_30d.price * 100

        overview = f"""
## 1. MARKET OVERVIEW

Current Price:        ${self.viz.format_large_number(latest.price)}
Market Cap:           ${self.viz.format_large_number(latest.market_cap)}
30d Price Change:     {price_change:+.2f}%
Circulating Supply:   {self.viz.format_large_number(latest.circulating_supply)} BTC

Price Trend (90d):    {self.viz.create_sparkline([s.price for s in snapshots[-90:]], 60)}

Active Addresses:     {self.viz.format_large_number(latest.active_addresses)}
Daily Transactions:   {self.viz.format_large_number(latest.transaction_count)}
Hash Rate:            {self.viz.format_large_number(latest.hash_rate or 0)} H/s
"""
        return overview

    def _generate_valuation_metrics(self, snapshots: List[OnChainSnapshot]) -> str:
        """生成估值指标"""
        if not snapshots:
            return ""

        latest = snapshots[-1]

        # 计算MVRV
        mvrv = self.metrics.calculate_mvrv(latest.market_cap, latest.realized_cap or latest.market_cap * 0.7)
        mvrv_z = self.metrics.calculate_mvrv_z_score(snapshots[-365:] if len(snapshots) >= 365 else snapshots)

        # 计算NUPL
        nupl = self.metrics.calculate_nupl(latest.market_cap, latest.realized_cap or latest.market_cap * 0.7,
                                          latest.circulating_supply)

        # 计算NVT
        nvt = self.metrics.calculate_nvt_signal(snapshots[-90:] if len(snapshots) >= 90 else snapshots)

        # MVRV历史
        mvrv_history = [self.metrics.calculate_mvrv(s.market_cap, s.realized_cap or s.market_cap * 0.7)
                       for s in snapshots[-90:]]

        valuation = f"""
## 2. VALUATION METRICS

### MVRV (Market Value to Realized Value)
Current MVRV:         {mvrv:.2f}
MVRV Z-Score:         {mvrv_z:.2f}

Interpretation:       {self._interpret_mvrv(mvrv)}

MVRV Trend (90d):     {self.viz.create_sparkline(mvrv_history, 60)}

{self.viz.create_gauge(mvrv, 0, 5, 60, "MVRV Gauge",
                       [(1.0, "Undervalued", '░'),
                        (2.4, "Fair Value", '▒'),
                        (5.0, "Overvalued", '▓')])}

### NUPL (Net Unrealized Profit/Loss)
Current NUPL:         {nupl:.2f}
Sentiment:            {self._interpret_nupl(nupl)}

{self.viz.create_gauge(nupl, -0.5, 1.0, 60, "NUPL Gauge",
                       [(0, "Capitulation", '░'),
                        (0.5, "Hope/Fear", '▒'),
                        (1.0, "Greed/Euphoria", '▓')])}

### NVT (Network Value to Transactions)
Current NVT Signal:   {nvt:.2f}
Status:               {self._interpret_nvt(nvt)}
"""
        return valuation

    def _generate_network_activity(self, snapshots: List[OnChainSnapshot]) -> str:
        """生成网络活动分析"""
        if not snapshots:
            return ""

        # 活跃地址趋势
        active_addrs = [s.active_addresses for s in snapshots[-90:]]
        tx_volumes = [s.transaction_volume for s in snapshots[-90:]]
        fees = [s.total_fees for s in snapshots[-90:]]

        network = f"""
## 3. NETWORK ACTIVITY

### Active Addresses (90 days)
{self.viz.create_line_chart(active_addrs, 70, 15, "Active Addresses Trend")}

Current:              {self.viz.format_large_number(active_addrs[-1])}
90d Average:          {self.viz.format_large_number(sum(active_addrs)/len(active_addrs))}
Trend:                {'↑ Increasing' if active_addrs[-1] > sum(active_addrs)/len(active_addrs) else '↓ Decreasing'}

### Transaction Volume (90 days)
{self.viz.create_line_chart(tx_volumes, 70, 15, "Transaction Volume (USD)")}

### Fee Analysis
Average Daily Fee:    {sum(fees)/len(fees):.2f} BTC
Fee Trend:            {self.viz.create_sparkline(fees, 60)}
"""
        return network

    def _generate_address_analysis(self, addresses: List[AddressBalance],
                                  snapshots: List[OnChainSnapshot]) -> str:
        """生成地址分析"""
        # 供应分布
        bins = [(0, 1), (1, 10), (10, 100), (100, 1000), (1000, 10000), (10000, float('inf'))]
        distribution = self.address_analytics.calculate_supply_distribution(addresses, bins)

        # 巨鲸识别
        whales = self.address_analytics.identify_whale_addresses(addresses, 1000)[:10]

        # 基尼系数
        gini = self.address_analytics.calculate_gini_coefficient(addresses)

        # 休眠币分析
        dormant = self.address_analytics.analyze_dormant_coins(addresses)

        address_report = f"""
## 4. ADDRESS ANALYSIS

### Supply Distribution
{self._format_distribution_table(distribution)}

### Wealth Concentration
Gini Coefficient:     {gini:.3f}
Interpretation:       {self._interpret_gini(gini)}

### Top 10 Whale Addresses
{self._format_whale_table(whales)}

### Dormant Coins (>1 year)
Total Dormant:        {self.viz.format_large_number(dormant['dormant_supply'])} BTC
Percentage:           {dormant['dormant_supply_pct']:.2f}%
Interpretation:       {dormant['interpretation']}
"""
        return address_report

    def _generate_exchange_analysis(self, flows: List[ExchangeFlow],
                                   snapshots: List[OnChainSnapshot]) -> str:
        """生成交易所分析"""
        # 净流入
        net_flows = self.exchange_analytics.calculate_net_flow(flows, 7)

        # 积累/分配状态
        phase = self.exchange_analytics.identify_accumulation_distribution(flows, 30)

        # 巨鲸转账
        whale_movements = self.exchange_analytics.detect_whale_movements(flows, 100)[:5]

        # 储备比率
        if snapshots:
            total_reserve = sum(f.reserve for f in flows[-10:]) / min(10, len(flows))
            esr = self.exchange_analytics.calculate_exchange_supply_ratio(
                total_reserve, snapshots[-1].circulating_supply
            )
        else:
            esr = {'esr': 0, 'interpretation': 'Unknown'}

        exchange_report = f"""
## 5. EXCHANGE FLOW ANALYSIS

### Net Flow (7 days)
{self.viz.create_bar_chart(net_flows, 50, "Net Flow by Exchange (BTC)")}

### Market Phase
Current Phase:        {phase.upper()}
Interpretation:       {self._interpret_phase(phase)}

### Exchange Supply Ratio
ESR:                  {esr['esr']:.4f} ({esr['esr']*100:.2f}%)
Signal:               {esr['interpretation']}

### Recent Whale Movements
{self._format_whale_movements_table(whale_movements)}
"""
        return exchange_report

    def _generate_miner_analysis(self, miner_data: List[MinerData],
                                snapshots: List[OnChainSnapshot]) -> str:
        """生成矿工分析"""
        # Puell Multiple
        puell = self.miner_analytics.calculate_puell_multiple(miner_data)

        # 矿工流动模式
        flow_pattern = self.miner_analytics.analyze_miner_flow_pattern(miner_data, 7)

        # Hash Ribbons
        if snapshots:
            hash_rates = [s.hash_rate for s in snapshots[-60:] if s.hash_rate]
            if hash_rates:
                hash_ribbons = self.miner_analytics.calculate_hash_ribbons(hash_rates)
            else:
                hash_ribbons = {'signal': 'unknown', 'interpretation': 'No data'}
        else:
            hash_ribbons = {'signal': 'unknown', 'interpretation': 'No data'}

        # 投降分析
        capitulation = self.miner_analytics.analyze_miner_capitulation(snapshots, miner_data)

        miner_report = f"""
## 6. MINER ANALYSIS

### Puell Multiple
Current Value:        {puell:.2f}
Signal:               {self._interpret_puell(puell)}

{self.viz.create_gauge(puell, 0, 5, 60, "Puell Multiple",
                       [(0.5, "Extreme Low", '░'),
                        (2.0, "Normal", '▒'),
                        (5.0, "Extreme High", '▓')])}

### Miner Flow Pattern
Pattern:              {flow_pattern['pattern'].replace('_', ' ').title()}
7d Coins Moved:       {self.viz.format_large_number(flow_pattern['total_moved_7d'])} BTC
Interpretation:       {flow_pattern['interpretation']}

### Hash Ribbons Signal
Signal:               {hash_ribbons['signal'].upper()}
Interpretation:       {hash_ribbons['interpretation']}

### Capitulation Status
Status:               {capitulation['status'].upper()}
Risk Level:           {capitulation['risk']:.1%}
Interpretation:       {capitulation.get('interpretation', 'N/A')}
"""
        return miner_report

    def _generate_market_signals(self, snapshots, addresses, flows, miner_data) -> str:
        """生成市场信号总结"""
        signals = []

        if snapshots:
            latest = snapshots[-1]
            mvrv = self.metrics.calculate_mvrv(latest.market_cap, latest.realized_cap or latest.market_cap * 0.7)

            if mvrv > 3.5:
                signals.append(("⚠️", "MVRV Overvaluation Warning", "MVRV > 3.5, historically near tops"))
            elif mvrv < 1.0:
                signals.append(("✅", "MVRV Undervaluation Opportunity", "MVRV < 1.0, historically near bottoms"))

        if flows:
            phase = self.exchange_analytics.identify_accumulation_distribution(flows, 30)
            if phase == "accumulation":
                signals.append(("✅", "Accumulation Phase Detected", "Coins leaving exchanges, bullish"))
            elif phase == "distribution":
                signals.append(("⚠️", "Distribution Phase Detected", "Coins entering exchanges, caution"))

        if miner_data and snapshots:
            puell = self.miner_analytics.calculate_puell_multiple(miner_data)
            if puell > 4:
                signals.append(("⚠️", "Extreme Miner Revenue", "Puell > 4, possible top"))
            elif puell < 0.5:
                signals.append(("✅", "Low Miner Revenue", "Puell < 0.5, possible bottom"))

        signals_text = f"""
## 7. MARKET SIGNALS SUMMARY

{'Signal':<5} {'Type':<35} {'Description':<50}
{'-' * 95}
"""
        for emoji, signal_type, desc in signals:
            signals_text += f"{emoji:<5} {signal_type:<35} {desc:<50}\n"

        if not signals:
            signals_text += "\nNo strong signals detected at this time. Market appears neutral.\n"

        return signals_text

    def _generate_footer(self) -> str:
        """生成页脚"""
        footer = f"""
{'=' * 100}
End of Report | Generated by Crypto On-Chain Analyzer
{'=' * 100}
"""
        return footer

    # Helper methods for interpretation
    def _interpret_mvrv(self, mvrv: float) -> str:
        if mvrv > 3.7:
            return "⚠️  EXTREME - Historical top territory"
        elif mvrv > 2.4:
            return "⚠️  HIGH - Possible overvaluation"
        elif mvrv > 1.0:
            return "✓  FAIR - Reasonable valuation"
        else:
            return "✅ LOW - Potential buying opportunity"

    def _interpret_nupl(self, nupl: float) -> str:
        if nupl > 0.75:
            return "😰 Greed/Euphoria"
        elif nupl > 0.5:
            return "🤔 Optimism/Anxiety"
        elif nupl > 0.25:
            return "😐 Hope/Fear"
        elif nupl > 0:
            return "😟 Capitulation/Anger"
        else:
            return "😱 Capitulation/Depression"

    def _interpret_nvt(self, nvt: float) -> str:
        if nvt > 100:
            return "⚠️  Overvalued relative to usage"
        elif nvt > 50:
            return "→  Fair valuation"
        else:
            return "✅ Undervalued relative to usage"

    def _interpret_gini(self, gini: float) -> str:
        if gini > 0.9:
            return "Very high inequality"
        elif gini > 0.7:
            return "High inequality"
        elif gini > 0.5:
            return "Moderate inequality"
        else:
            return "Relatively equal distribution"

    def _interpret_phase(self, phase: str) -> str:
        if phase == "accumulation":
            return "✅ Bullish - Smart money accumulating"
        elif phase == "distribution":
            return "⚠️  Bearish - Whales distributing"
        else:
            return "→  Neutral - No clear trend"

    def _interpret_puell(self, puell: float) -> str:
        if puell > 4:
            return "⚠️  Extreme high - Possible top"
        elif puell > 2:
            return "↑  Above average"
        elif puell > 0.5:
            return "→  Normal range"
        else:
            return "✅ Extreme low - Possible bottom"

    def _format_distribution_table(self, distribution: Dict) -> str:
        """格式化分布表格"""
        headers = ["Range (BTC)", "Addresses", "Supply", "% of Total"]
        rows = []
        for range_label, data in distribution.items():
            rows.append([
                range_label,
                f"{data['address_count']:,}",
                TerminalVisualizer.format_large_number(data['supply']),
                f"{data['supply_pct']:.2f}%"
            ])
        return self.viz.create_table(headers, rows)

    def _format_whale_table(self, whales: List[Dict]) -> str:
        """格式化巨鲸表格"""
        headers = ["Address", "Balance", "Age", "Status", "Type"]
        rows = []
        for whale in whales[:10]:
            rows.append([
                whale['address'][:12] + "...",
                TerminalVisualizer.format_large_number(whale['balance']),
                f"{whale['age_days']}d",
                whale['activity'],
                whale['type'].replace('_', ' ').title()
            ])
        return self.viz.create_table(headers, rows)

    def _format_whale_movements_table(self, movements: List[Dict]) -> str:
        """格式化巨鲸转账表格"""
        if not movements:
            return "No significant whale movements detected"

        headers = ["Timestamp", "Exchange", "Amount", "Direction"]
        rows = []
        for mov in movements:
            rows.append([
                mov['timestamp'].strftime('%Y-%m-%d %H:%M'),
                mov['exchange'],
                f"{mov['amount']:+.2f} BTC",
                mov['direction'].upper()
            ])
        return self.viz.create_table(headers, rows)
