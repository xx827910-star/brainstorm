"""
矿工行为分析
追踪矿工的挖矿收入、抛售行为和储备变化
"""
import numpy as np
from typing import List, Dict, Tuple
from datetime import datetime, timedelta
from ..core.models import MinerData, OnChainSnapshot


class MinerAnalytics:
    """矿工分析工具"""

    @staticmethod
    def calculate_miner_position_index(miner_data: List[MinerData],
                                      window: int = 14) -> float:
        """
        Miner Position Index (MPI)
        矿工持仓指数

        MPI = Miner Outflow / Miner Outflow 1Y MA

        高值表示矿工在卖出
        低值表示矿工在囤积
        """
        if len(miner_data) < 365:
            return 1.0

        recent_outflow = sum(d.coins_moved for d in miner_data[-window:])
        yearly_avg = np.mean([d.coins_moved for d in miner_data[-365:]])

        if yearly_avg == 0:
            return 1.0

        return recent_outflow / window / yearly_avg

    @staticmethod
    def calculate_puell_multiple(miner_data: List[MinerData]) -> float:
        """
        Puell Multiple
        矿工收入倍数

        PM = Daily Miner Revenue / 365d MA Revenue

        > 4: 收入极高，可能接近顶部
        < 0.5: 收入极低，可能接近底部
        """
        if len(miner_data) < 365:
            return 1.0

        current_revenue = miner_data[-1].revenue
        yearly_avg = np.mean([d.revenue for d in miner_data[-365:]])

        if yearly_avg == 0:
            return 1.0

        return current_revenue / yearly_avg

    @staticmethod
    def analyze_miner_capitulation(snapshots: List[OnChainSnapshot],
                                   miner_data: List[MinerData]) -> Dict:
        """
        矿工投降分析

        当挖矿成本接近或高于币价时，矿工可能被迫卖出

        Returns:
            投降指标和状态
        """
        if not snapshots or not miner_data:
            return {'status': 'unknown', 'risk': 0.0}

        # 估算挖矿成本
        recent_revenue = np.mean([d.revenue for d in miner_data[-30:]])
        hash_rate = snapshots[-1].hash_rate or 1.0
        difficulty = snapshots[-1].difficulty or 1.0

        # 简化的成本模型
        mining_cost = (difficulty * 1000) / hash_rate  # 简化计算

        current_price = snapshots[-1].price
        price_to_cost_ratio = current_price / mining_cost if mining_cost > 0 else 2.0

        # 矿工储备变化
        reserve_change = 0.0
        if len(miner_data) >= 30:
            old_reserve = np.mean([d.reserve for d in miner_data[-60:-30]])
            new_reserve = np.mean([d.reserve for d in miner_data[-30:]])
            reserve_change = (new_reserve - old_reserve) / old_reserve if old_reserve > 0 else 0.0

        if price_to_cost_ratio < 1.2:
            status = 'capitulation'
            risk = 0.9
        elif price_to_cost_ratio < 1.5:
            status = 'stress'
            risk = 0.6
        else:
            status = 'healthy'
            risk = 0.2

        return {
            'status': status,
            'price_to_cost_ratio': price_to_cost_ratio,
            'risk': risk,
            'reserve_change_30d': reserve_change,
            'interpretation': self._interpret_capitulation(status, reserve_change)
        }

    @staticmethod
    def _interpret_capitulation(status: str, reserve_change: float) -> str:
        """解释投降状态"""
        if status == 'capitulation':
            if reserve_change < -0.1:
                return "强烈投降 - 矿工大量抛售，通常是底部信号"
            else:
                return "价格压力 - 矿工面临成本压力但未大量抛售"
        elif status == 'stress':
            return "中度压力 - 矿工盈利空间收窄，需关注价格走势"
        else:
            return "健康状态 - 矿工盈利充足，持续挖矿动力强"

    @staticmethod
    def calculate_miner_revenue_stress(miner_data: List[MinerData],
                                      price_data: List[float]) -> float:
        """
        矿工收入压力指数

        比较矿工收入与价格变化的关系
        """
        if len(miner_data) < 30 or len(price_data) < 30:
            return 0.0

        revenue_change = (miner_data[-1].revenue - miner_data[-30].revenue) / miner_data[-30].revenue
        price_change = (price_data[-1] - price_data[-30]) / price_data[-30]

        # 价格上涨但收入下降 = 压力
        stress = price_change - revenue_change

        return max(0.0, stress)

    @staticmethod
    def analyze_miner_flow_pattern(miner_data: List[MinerData],
                                   window: int = 7) -> Dict:
        """
        分析矿工资金流动模式

        Returns:
            流动模式分类和统计
        """
        if len(miner_data) < window:
            return {'pattern': 'unknown'}

        recent = miner_data[-window:]

        total_moved = sum(d.coins_moved for d in recent)
        avg_reserve = np.mean([d.reserve for d in recent])
        move_ratio = total_moved / (avg_reserve * window) if avg_reserve > 0 else 0.0

        # 分类模式
        if move_ratio > 0.15:
            pattern = 'heavy_selling'
            interpretation = "矿工大量抛售，可能价格承压"
        elif move_ratio > 0.08:
            pattern = 'moderate_selling'
            interpretation = "矿工正常卖出,覆盖运营成本"
        elif move_ratio < 0.03:
            pattern = 'accumulation'
            interpretation = "矿工囤积,看涨信号"
        else:
            pattern = 'normal'
            interpretation = "正常流动状态"

        return {
            'pattern': pattern,
            'move_ratio': move_ratio,
            'total_moved_7d': total_moved,
            'interpretation': interpretation
        }

    @staticmethod
    def calculate_hash_ribbons(hash_rates: List[float],
                              short_window: int = 30,
                              long_window: int = 60) -> Dict:
        """
        Hash Ribbons
        算力带指标

        当短期MA上穿长期MA时，是买入信号（投降结束）
        """
        if len(hash_rates) < long_window:
            return {'signal': 'neutral', 'ma_short': 0, 'ma_long': 0}

        ma_short = np.mean(hash_rates[-short_window:])
        ma_long = np.mean(hash_rates[-long_window:])

        # 检测交叉
        prev_ma_short = np.mean(hash_rates[-short_window-1:-1])
        prev_ma_long = np.mean(hash_rates[-long_window-1:-1])

        if ma_short > ma_long and prev_ma_short <= prev_ma_long:
            signal = 'buy'
            interpretation = "算力恢复增长，矿工投降结束，买入信号"
        elif ma_short < ma_long and prev_ma_short >= prev_ma_long:
            signal = 'sell'
            interpretation = "算力下降，矿工可能投降，谨慎信号"
        elif ma_short > ma_long:
            signal = 'bullish'
            interpretation = "算力健康增长"
        else:
            signal = 'bearish'
            interpretation = "算力下降趋势"

        return {
            'signal': signal,
            'ma_short': ma_short,
            'ma_long': ma_long,
            'ratio': ma_short / ma_long if ma_long > 0 else 1.0,
            'interpretation': interpretation
        }

    @staticmethod
    def calculate_difficulty_ribbon_compression(difficulties: List[float],
                                               windows: List[int] = [9, 14, 25, 40, 60, 90, 128, 200]) -> Dict:
        """
        Difficulty Ribbon Compression
        难度带压缩

        当多条难度MA线收敛时，表示买入机会
        """
        if len(difficulties) < max(windows):
            return {'compression': 0.0, 'signal': 'neutral'}

        mas = []
        for window in windows:
            ma = np.mean(difficulties[-window:])
            mas.append(ma)

        # 计算压缩程度（标准差）
        compression = np.std(mas) / np.mean(mas) if np.mean(mas) > 0 else 0.0

        if compression < 0.02:
            signal = 'strong_buy'
            interpretation = "极度压缩，历史买入时机"
        elif compression < 0.05:
            signal = 'buy'
            interpretation = "压缩中，关注买入机会"
        elif compression > 0.15:
            signal = 'expanded'
            interpretation = "发散中，市场活跃"
        else:
            signal = 'neutral'
            interpretation = "正常状态"

        return {
            'compression': compression,
            'signal': signal,
            'mas': {f'MA{w}': ma for w, ma in zip(windows, mas)},
            'interpretation': interpretation
        }

    @staticmethod
    def analyze_miner_sell_pressure(miner_data: List[MinerData],
                                   price_data: List[Tuple[datetime, float]]) -> List[Dict]:
        """
        分析矿工卖压时机

        识别矿工大量抛售与价格的关系
        """
        price_map = {ts: price for ts, price in price_data}
        sell_events = []

        for i in range(1, len(miner_data)):
            prev = miner_data[i-1]
            curr = miner_data[i]

            # 检测大量转移
            if curr.coins_moved > prev.coins_moved * 2 and curr.coins_moved > 100:
                price = price_map.get(curr.timestamp, 0)

                sell_events.append({
                    'timestamp': curr.timestamp,
                    'amount': curr.coins_moved,
                    'miner': curr.miner_address,
                    'price': price,
                    'reserve_before': prev.reserve,
                    'reserve_after': curr.reserve,
                    'severity': 'high' if curr.coins_moved > 500 else 'medium'
                })

        return sell_events

    @staticmethod
    def calculate_miner_balances(miner_data: List[MinerData]) -> Dict:
        """
        计算矿工余额统计

        Returns:
            矿工储备总量和分布统计
        """
        if not miner_data:
            return {}

        latest_by_miner = {}
        for data in miner_data:
            if (data.miner_address not in latest_by_miner or
                data.timestamp > latest_by_miner[data.miner_address].timestamp):
                latest_by_miner[data.miner_address] = data

        total_reserve = sum(d.reserve for d in latest_by_miner.values())
        reserves = [d.reserve for d in latest_by_miner.values()]

        return {
            'total_miners': len(latest_by_miner),
            'total_reserve': total_reserve,
            'avg_reserve': np.mean(reserves),
            'median_reserve': np.median(reserves),
            'top_10_pct': sum(sorted(reserves, reverse=True)[:max(1, len(reserves)//10)]),
            'concentration': np.std(reserves) / np.mean(reserves) if reserves else 0.0
        }
