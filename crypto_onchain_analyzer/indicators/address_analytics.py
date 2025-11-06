"""
地址和交易分析
活跃地址、新增地址、巨鲸追踪等
"""
import numpy as np
from typing import List, Dict, Tuple
from datetime import datetime, timedelta
from ..core.models import AddressBalance, OnChainSnapshot


class AddressAnalytics:
    """地址分析工具"""

    @staticmethod
    def analyze_active_addresses(snapshots: List[OnChainSnapshot],
                                 window: int = 30) -> Dict:
        """
        活跃地址分析

        Returns:
            活跃地址趋势和统计
        """
        if len(snapshots) < window:
            return {'trend': 'unknown'}

        recent = snapshots[-window:]
        addresses = [s.active_addresses for s in recent]

        current = addresses[-1]
        avg = np.mean(addresses)
        trend_slope = np.polyfit(range(len(addresses)), addresses, 1)[0]

        if trend_slope > avg * 0.02:
            trend = 'increasing'
            interpretation = "活跃度上升，网络使用增加"
        elif trend_slope < -avg * 0.02:
            trend = 'decreasing'
            interpretation = "活跃度下降，需关注"
        else:
            trend = 'stable'
            interpretation = "活跃度稳定"

        return {
            'current': current,
            'avg_30d': avg,
            'trend': trend,
            'change_pct': (current - avg) / avg * 100 if avg > 0 else 0.0,
            'interpretation': interpretation
        }

    @staticmethod
    def calculate_address_growth_rate(snapshots: List[OnChainSnapshot],
                                     window: int = 30) -> float:
        """
        地址增长率

        新增地址数量趋势
        """
        if len(snapshots) < window:
            return 0.0

        recent = snapshots[-window:]
        new_addresses = [s.new_addresses for s in recent]

        total_new = sum(new_addresses)
        avg_daily = total_new / window

        return avg_daily

    @staticmethod
    def identify_whale_addresses(addresses: List[AddressBalance],
                                 threshold_btc: float = 1000) -> List[Dict]:
        """
        识别巨鲸地址

        Args:
            addresses: 地址余额列表
            threshold_btc: 巨鲸阈值

        Returns:
            巨鲸地址列表
        """
        whales = []

        for addr in addresses:
            if addr.balance >= threshold_btc:
                whales.append({
                    'address': addr.address,
                    'balance': addr.balance,
                    'age_days': addr.age_days,
                    'last_active': addr.last_active,
                    'activity': 'dormant' if (datetime.now() - addr.last_active).days > 180 else 'active',
                    'type': AddressAnalytics._classify_whale(addr)
                })

        return sorted(whales, key=lambda x: x['balance'], reverse=True)

    @staticmethod
    def _classify_whale(addr: AddressBalance) -> str:
        """分类巨鲸类型"""
        age_days = addr.age_days
        tx_count = addr.transaction_count

        if age_days > 1000 and tx_count < 10:
            return 'long_term_holder'
        elif tx_count > 1000:
            return 'exchange_or_service'
        elif age_days < 90:
            return 'new_whale'
        else:
            return 'active_whale'

    @staticmethod
    def track_whale_movements(addresses: List[AddressBalance],
                             historical: Dict[str, AddressBalance]) -> List[Dict]:
        """
        追踪巨鲸资金移动

        Args:
            addresses: 当前地址状态
            historical: 历史地址状态

        Returns:
            变动记录
        """
        movements = []

        for addr in addresses:
            if addr.address in historical and addr.balance >= 100:
                old = historical[addr.address]
                change = addr.balance - old.balance

                if abs(change) > 50:  # 显著变动
                    movements.append({
                        'address': addr.address,
                        'change': change,
                        'direction': 'accumulation' if change > 0 else 'distribution',
                        'old_balance': old.balance,
                        'new_balance': addr.balance,
                        'timestamp': addr.last_active
                    })

        return sorted(movements, key=lambda x: abs(x['change']), reverse=True)

    @staticmethod
    def calculate_supply_distribution(addresses: List[AddressBalance],
                                     bins: List[Tuple[float, float]]) -> Dict:
        """
        供应分布分析

        Args:
            addresses: 地址列表
            bins: [(min, max), ...] 余额区间

        Returns:
            各区间的地址数量和占比
        """
        distribution = {}
        total_supply = sum(addr.balance for addr in addresses)

        for min_bal, max_bal in bins:
            addrs_in_bin = [a for a in addresses
                          if min_bal <= a.balance < max_bal]

            supply_in_bin = sum(a.balance for a in addrs_in_bin)

            key = f"{min_bal}-{max_bal}"
            distribution[key] = {
                'address_count': len(addrs_in_bin),
                'supply': supply_in_bin,
                'supply_pct': supply_in_bin / total_supply * 100 if total_supply > 0 else 0
            }

        return distribution

    @staticmethod
    def calculate_gini_coefficient(addresses: List[AddressBalance]) -> float:
        """
        计算基尼系数
        衡量财富分配不平等程度

        0 = 完全平等
        1 = 完全不平等

        Returns:
            基尼系数
        """
        if not addresses:
            return 0.0

        balances = sorted([a.balance for a in addresses])
        n = len(balances)

        if n == 0 or sum(balances) == 0:
            return 0.0

        cumsum = np.cumsum(balances)
        total = cumsum[-1]

        # 计算基尼系数
        gini = (2 * sum((i + 1) * bal for i, bal in enumerate(balances))) / (n * total) - (n + 1) / n

        return gini

    @staticmethod
    def analyze_entity_concentration(addresses: List[AddressBalance],
                                    top_n: int = 100) -> Dict:
        """
        分析实体集中度

        Returns:
            Top N地址持有量统计
        """
        sorted_addrs = sorted(addresses, key=lambda a: a.balance, reverse=True)
        top_addresses = sorted_addrs[:top_n]

        total_supply = sum(a.balance for a in addresses)
        top_supply = sum(a.balance for a in top_addresses)

        return {
            'top_n': top_n,
            'top_supply': top_supply,
            'top_supply_pct': top_supply / total_supply * 100 if total_supply > 0 else 0,
            'total_addresses': len(addresses),
            'concentration_ratio': top_supply / total_supply if total_supply > 0 else 0,
            'interpretation': (
                'Highly concentrated' if top_supply / total_supply > 0.5 else
                'Moderately concentrated' if top_supply / total_supply > 0.3 else
                'Well distributed'
            )
        }

    @staticmethod
    def identify_smart_money(addresses: List[AddressBalance],
                           price_history: List[Tuple[datetime, float]]) -> List[Dict]:
        """
        识别聪明钱地址

        特征：
        - 在低点买入
        - 在高点卖出
        - 长期盈利
        """
        smart_money = []
        price_map = {ts: price for ts, price in price_history}

        for addr in addresses:
            if addr.transaction_count < 5:
                continue

            # 简化判断：活跃且持有时间长
            age_days = addr.age_days
            if age_days > 365 and addr.balance > 10:
                score = 0

                # 长期持有加分
                if age_days > 1000:
                    score += 3

                # 较少交易（不是交易所）
                if addr.transaction_count < 100:
                    score += 2

                # 余额稳定增长
                if addr.balance > 0:
                    score += 1

                if score >= 4:
                    smart_money.append({
                        'address': addr.address,
                        'balance': addr.balance,
                        'age_days': age_days,
                        'score': score,
                        'type': 'accumulator'
                    })

        return sorted(smart_money, key=lambda x: x['score'], reverse=True)

    @staticmethod
    def calculate_address_activity_ratio(snapshots: List[OnChainSnapshot]) -> float:
        """
        地址活跃率

        Active Addresses / Total Addresses

        高活跃率表示网络使用活跃
        """
        if not snapshots:
            return 0.0

        recent = snapshots[-1]
        # 简化：假设总地址数
        total_addresses = recent.active_addresses * 10  # 估算

        return recent.active_addresses / total_addresses if total_addresses > 0 else 0.0

    @staticmethod
    def detect_accumulation_addresses(current: List[AddressBalance],
                                     historical: Dict[str, AddressBalance],
                                     min_increase: float = 10) -> List[Dict]:
        """
        检测正在积累的地址

        Args:
            current: 当前地址状态
            historical: 历史状态
            min_increase: 最小增加量

        Returns:
            积累地址列表
        """
        accumulators = []

        for addr in current:
            if addr.address in historical:
                old = historical[addr.address]
                increase = addr.balance - old.balance

                if increase >= min_increase:
                    days_diff = (addr.last_active - old.last_active).days
                    daily_rate = increase / days_diff if days_diff > 0 else 0

                    accumulators.append({
                        'address': addr.address,
                        'increase': increase,
                        'old_balance': old.balance,
                        'new_balance': addr.balance,
                        'days': days_diff,
                        'daily_rate': daily_rate,
                        'total_pct_increase': increase / old.balance * 100 if old.balance > 0 else 0
                    })

        return sorted(accumulators, key=lambda x: x['increase'], reverse=True)

    @staticmethod
    def analyze_dormant_coins(addresses: List[AddressBalance],
                             dormant_threshold_days: int = 365) -> Dict:
        """
        分析休眠币

        长期未移动的币

        Returns:
            休眠币统计
        """
        dormant_addrs = [a for a in addresses
                        if (datetime.now() - a.last_active).days >= dormant_threshold_days]

        total_supply = sum(a.balance for a in addresses)
        dormant_supply = sum(a.balance for a in dormant_addrs)

        age_groups = {
            '1-2y': [a for a in dormant_addrs if 365 <= a.age_days < 730],
            '2-3y': [a for a in dormant_addrs if 730 <= a.age_days < 1095],
            '3-5y': [a for a in dormant_addrs if 1095 <= a.age_days < 1825],
            '5y+': [a for a in dormant_addrs if a.age_days >= 1825]
        }

        return {
            'dormant_addresses': len(dormant_addrs),
            'dormant_supply': dormant_supply,
            'dormant_supply_pct': dormant_supply / total_supply * 100 if total_supply > 0 else 0,
            'age_breakdown': {
                age: {
                    'count': len(addrs),
                    'supply': sum(a.balance for a in addrs)
                }
                for age, addrs in age_groups.items()
            },
            'interpretation': (
                'High HODLing sentiment' if dormant_supply / total_supply > 0.6 else
                'Moderate HODLing' if dormant_supply / total_supply > 0.4 else
                'Low HODLing, active trading'
            )
        }
