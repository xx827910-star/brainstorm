"""
交易所流入流出分析
追踪资金在交易所和链上的流动
"""
import numpy as np
from typing import List, Dict, Tuple
from datetime import datetime, timedelta
from ..core.models import ExchangeFlow


class ExchangeAnalytics:
    """交易所分析工具"""

    @staticmethod
    def calculate_net_flow(flows: List[ExchangeFlow],
                          window_days: int = 7) -> Dict[str, float]:
        """
        计算各交易所的净流入

        Args:
            flows: 交易所流动数据
            window_days: 统计窗口（天）

        Returns:
            {exchange_name: net_flow}
        """
        cutoff = datetime.now() - timedelta(days=window_days)
        recent_flows = [f for f in flows if f.timestamp >= cutoff]

        exchange_net = {}
        for flow in recent_flows:
            if flow.exchange_name not in exchange_net:
                exchange_net[flow.exchange_name] = 0.0
            exchange_net[flow.exchange_name] += flow.net_flow

        return exchange_net

    @staticmethod
    def detect_whale_movements(flows: List[ExchangeFlow],
                              threshold: float = 100.0) -> List[Dict]:
        """
        检测巨鲸转账

        Args:
            flows: 流动数据
            threshold: 触发阈值（BTC数量）

        Returns:
            巨鲸转账事件列表
        """
        whale_events = []

        for flow in flows:
            if abs(flow.net_flow) >= threshold:
                whale_events.append({
                    'timestamp': flow.timestamp,
                    'exchange': flow.exchange_name,
                    'amount': flow.net_flow,
                    'direction': 'inflow' if flow.net_flow > 0 else 'outflow',
                    'reserve_after': flow.reserve
                })

        return whale_events

    @staticmethod
    def calculate_exchange_reserve_ratio(flows: List[ExchangeFlow],
                                        circulating_supply: float) -> Dict[str, float]:
        """
        交易所储备比率

        Reserve Ratio = Exchange Reserve / Circulating Supply

        低比率可能表示供应紧张
        """
        latest_by_exchange = {}

        for flow in flows:
            if (flow.exchange_name not in latest_by_exchange or
                flow.timestamp > latest_by_exchange[flow.exchange_name].timestamp):
                latest_by_exchange[flow.exchange_name] = flow

        reserve_ratios = {}
        for exchange, flow in latest_by_exchange.items():
            ratio = flow.reserve / circulating_supply if circulating_supply > 0 else 0.0
            reserve_ratios[exchange] = ratio

        return reserve_ratios

    @staticmethod
    def identify_accumulation_distribution(flows: List[ExchangeFlow],
                                          ma_period: int = 30) -> str:
        """
        识别积累/分配阶段

        Returns:
            "accumulation": 资金持续流出交易所（积累）
            "distribution": 资金持续流入交易所（分配）
            "neutral": 中性
        """
        if len(flows) < ma_period:
            return "neutral"

        recent = flows[-ma_period:]
        total_net = sum(f.net_flow for f in recent)
        avg_net = total_net / len(recent)

        # 检查趋势一致性
        positive_days = sum(1 for f in recent if f.net_flow < 0)  # 流出为负
        consistency = positive_days / len(recent)

        if avg_net < -10 and consistency > 0.6:
            return "accumulation"
        elif avg_net > 10 and consistency > 0.6:
            return "distribution"
        else:
            return "neutral"

    @staticmethod
    def calculate_flow_momentum(flows: List[ExchangeFlow],
                               short_window: int = 7,
                               long_window: int = 30) -> float:
        """
        流动动量

        比较短期和长期净流入的差异
        """
        if len(flows) < long_window:
            return 0.0

        short_flows = flows[-short_window:]
        long_flows = flows[-long_window:]

        short_avg = np.mean([f.net_flow for f in short_flows])
        long_avg = np.mean([f.net_flow for f in long_flows])

        return short_avg - long_avg

    @staticmethod
    def analyze_weekend_effect(flows: List[ExchangeFlow]) -> Dict:
        """
        分析周末效应

        Returns:
            周末与工作日的流入差异统计
        """
        weekday_flows = []
        weekend_flows = []

        for flow in flows:
            if flow.timestamp.weekday() >= 5:  # Saturday, Sunday
                weekend_flows.append(flow.net_flow)
            else:
                weekday_flows.append(flow.net_flow)

        return {
            'weekday_avg': np.mean(weekday_flows) if weekday_flows else 0.0,
            'weekend_avg': np.mean(weekend_flows) if weekend_flows else 0.0,
            'difference': (np.mean(weekend_flows) - np.mean(weekday_flows))
                         if weekend_flows and weekday_flows else 0.0
        }

    @staticmethod
    def calculate_exchange_dominance(flows: List[ExchangeFlow]) -> Dict[str, float]:
        """
        计算各交易所的储备占比

        Returns:
            {exchange: percentage}
        """
        latest_by_exchange = {}

        for flow in flows:
            if (flow.exchange_name not in latest_by_exchange or
                flow.timestamp > latest_by_exchange[flow.exchange_name].timestamp):
                latest_by_exchange[flow.exchange_name] = flow

        total_reserve = sum(f.reserve for f in latest_by_exchange.values())

        dominance = {}
        for exchange, flow in latest_by_exchange.items():
            dominance[exchange] = (flow.reserve / total_reserve * 100
                                  if total_reserve > 0 else 0.0)

        return dominance

    @staticmethod
    def detect_selling_pressure(flows: List[ExchangeFlow],
                               price_data: List[Tuple[datetime, float]],
                               threshold: float = 50.0) -> List[Dict]:
        """
        检测卖压信号

        大量流入交易所 + 价格下跌 = 卖压

        Args:
            flows: 交易所流动
            price_data: [(timestamp, price)]
            threshold: 流入阈值

        Returns:
            卖压事件列表
        """
        price_map = {ts: price for ts, price in price_data}
        selling_signals = []

        for i, flow in enumerate(flows):
            if flow.net_flow > threshold:  # 大量流入
                # 检查价格变化
                price_now = price_map.get(flow.timestamp, 0)
                future_ts = flow.timestamp + timedelta(hours=24)
                price_future = None

                # 找到未来价格
                for ts, price in price_data:
                    if ts >= future_ts:
                        price_future = price
                        break

                if price_now > 0 and price_future and price_future < price_now:
                    price_change = (price_future - price_now) / price_now * 100
                    selling_signals.append({
                        'timestamp': flow.timestamp,
                        'exchange': flow.exchange_name,
                        'inflow': flow.net_flow,
                        'price_change_24h': price_change,
                        'severity': 'high' if abs(price_change) > 5 else 'medium'
                    })

        return selling_signals

    @staticmethod
    def calculate_exchange_supply_ratio(total_exchange_reserve: float,
                                       circulating_supply: float) -> Dict:
        """
        交易所总供应比率

        ESR = Total Exchange Reserve / Circulating Supply

        解读：
        - ESR下降: 供应从交易所转移到钱包（看涨）
        - ESR上升: 供应转移到交易所（可能卖出）
        """
        esr = total_exchange_reserve / circulating_supply if circulating_supply > 0 else 0.0

        return {
            'esr': esr,
            'interpretation': (
                'Bullish - Supply leaving exchanges' if esr < 0.10 else
                'Bearish - Supply entering exchanges' if esr > 0.15 else
                'Neutral'
            )
        }
