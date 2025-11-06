"""
链上指标计算引擎
实现MVRV, SOPR, NUPL等核心链上指标
"""
import numpy as np
from typing import List, Tuple, Optional
from datetime import datetime, timedelta
from ..core.models import OnChainSnapshot, UTXOTransaction


class OnChainMetrics:
    """链上指标计算器"""

    @staticmethod
    def calculate_mvrv(market_cap: float, realized_cap: float) -> float:
        """
        Market Value to Realized Value (MVRV)
        市场价值与已实现价值比率

        MVRV = Market Cap / Realized Cap

        解读：
        - MVRV > 3.7: 历史顶部区域
        - MVRV > 2.4: 可能过热
        - MVRV < 1: 历史底部区域，价值投资机会

        Args:
            market_cap: 市值
            realized_cap: 已实现市值（所有币最后一次移动时的价格总和）

        Returns:
            MVRV比率
        """
        if realized_cap == 0:
            return 0.0
        return market_cap / realized_cap

    @staticmethod
    def calculate_mvrv_z_score(snapshots: List[OnChainSnapshot]) -> float:
        """
        MVRV Z-Score
        标准化的MVRV，考虑历史波动

        Z-Score = (Market Cap - Realized Cap) / StdDev(Market Cap)

        解读：
        - Z-Score > 7: 极度高估
        - Z-Score > 3: 可能高估
        - Z-Score < 0: 可能低估
        """
        if len(snapshots) < 2:
            return 0.0

        market_caps = [s.market_cap for s in snapshots]
        realized_caps = [s.realized_cap for s in snapshots if s.realized_cap]

        if not realized_caps:
            return 0.0

        current_mc = market_caps[-1]
        current_rc = realized_caps[-1]
        std_mc = np.std(market_caps)

        if std_mc == 0:
            return 0.0

        return (current_mc - current_rc) / std_mc

    @staticmethod
    def calculate_sopr(transactions: List[UTXOTransaction],
                       price_map: dict) -> float:
        """
        Spent Output Profit Ratio (SOPR)
        已花费输出利润率

        SOPR = Sold Price / Paid Price

        解读：
        - SOPR > 1: 平均而言，投资者在获利
        - SOPR < 1: 平均而言，投资者在亏损
        - SOPR = 1: 盈亏平衡点，通常是支撑位或阻力位

        Args:
            transactions: UTXO交易列表
            price_map: {timestamp: price} 价格映射

        Returns:
            SOPR值
        """
        if not transactions:
            return 1.0

        total_profit_ratio = 0.0
        valid_count = 0

        for tx in transactions:
            # 获取卖出价格
            sell_price = price_map.get(tx.timestamp, 0)
            if sell_price == 0:
                continue

            # 计算每个输入的利润率
            for inp in tx.inputs:
                buy_price = inp.get('price', 0)
                if buy_price > 0:
                    profit_ratio = sell_price / buy_price
                    total_profit_ratio += profit_ratio
                    valid_count += 1

        return total_profit_ratio / valid_count if valid_count > 0 else 1.0

    @staticmethod
    def calculate_nupl(market_cap: float, realized_cap: float,
                       circulating_supply: float) -> float:
        """
        Net Unrealized Profit/Loss (NUPL)
        净未实现盈亏

        NUPL = (Market Cap - Realized Cap) / Market Cap

        解读：
        - NUPL > 0.75: 贪婪/狂热
        - NUPL > 0.5: 乐观/焦虑
        - NUPL > 0.25: 希望/恐惧
        - NUPL > 0: 投降/愤怒
        - NUPL < 0: 投降/绝望
        """
        if market_cap == 0:
            return 0.0
        return (market_cap - realized_cap) / market_cap

    @staticmethod
    def calculate_reserve_risk(price: float, hodl_bank: float) -> float:
        """
        Reserve Risk
        储备风险

        Reserve Risk = Price / (HODL Bank × Confidence)

        低值表示持有者信心高，适合买入
        高值表示持有者信心低，可能卖压大
        """
        if hodl_bank == 0:
            return 0.0
        return price / hodl_bank

    @staticmethod
    def calculate_hodl_waves(snapshots: List[OnChainSnapshot],
                            age_bands: List[Tuple[int, int]]) -> dict:
        """
        HODL Waves
        持币时间分布

        显示不同持币时长的比例变化

        Args:
            snapshots: 快照列表
            age_bands: [(0, 7), (7, 30), (30, 90), ...] 天数区间

        Returns:
            {age_band: percentage} 各时间段占比
        """
        # 简化实现，实际需要UTXO集合数据
        waves = {}
        for start, end in age_bands:
            waves[f"{start}-{end}days"] = 0.0
        return waves

    @staticmethod
    def calculate_nvt(market_cap: float, transaction_volume: float,
                      window: int = 90) -> float:
        """
        Network Value to Transactions (NVT)
        网络价值与交易比率

        NVT = Market Cap / Daily Transaction Volume (90d MA)

        类似于股票的市盈率
        - 高NVT: 可能高估
        - 低NVT: 可能低估
        """
        if transaction_volume == 0:
            return 0.0
        return market_cap / transaction_volume

    @staticmethod
    def calculate_nvt_signal(snapshots: List[OnChainSnapshot],
                            window: int = 90) -> float:
        """
        NVT Signal
        NVT的改进版本，使用移动平均
        """
        if len(snapshots) < window:
            return 0.0

        recent = snapshots[-window:]
        avg_volume = np.mean([s.transaction_volume for s in recent])
        current_mc = snapshots[-1].market_cap

        if avg_volume == 0:
            return 0.0
        return current_mc / avg_volume

    @staticmethod
    def calculate_rvt(realized_cap: float, transaction_volume: float) -> float:
        """
        Realized Value to Transactions (RVT)
        已实现价值与交易比率
        """
        if transaction_volume == 0:
            return 0.0
        return realized_cap / transaction_volume

    @staticmethod
    def calculate_stock_to_flow(annual_supply: float,
                                circulating_supply: float) -> float:
        """
        Stock-to-Flow (S2F)
        存量流量比

        S2F = Circulating Supply / Annual New Supply

        用于衡量稀缺性
        """
        if annual_supply == 0:
            return 0.0
        return circulating_supply / annual_supply

    @staticmethod
    def calculate_puell_multiple(miner_revenue: float,
                                 revenue_ma_365: float) -> float:
        """
        Puell Multiple
        矿工收入倍数

        Puell = Daily Miner Revenue / 365d MA Revenue

        解读：
        - > 4: 矿工收入极高，可能接近顶部
        - < 0.5: 矿工收入极低,可能接近底部
        """
        if revenue_ma_365 == 0:
            return 0.0
        return miner_revenue / revenue_ma_365

    @staticmethod
    def calculate_difficulty_ribbon(difficulties: List[float],
                                    windows: List[int] = [9, 14, 25, 40, 60, 90, 128, 200]) -> dict:
        """
        Difficulty Ribbon
        难度带

        多条不同周期的难度移动平均线
        压缩时（较低机会成本）是买入机会
        """
        ribbons = {}
        for window in windows:
            if len(difficulties) >= window:
                ma = np.mean(difficulties[-window:])
                ribbons[f"MA{window}"] = ma
            else:
                ribbons[f"MA{window}"] = 0.0
        return ribbons

    @staticmethod
    def calculate_sopr_adjusted(transactions: List[UTXOTransaction],
                               price_map: dict,
                               min_age_days: int = 155) -> float:
        """
        aSOPR (Adjusted SOPR)
        调整后的SOPR，过滤掉短期交易（<155天）

        显示长期持有者的盈利状态
        """
        if not transactions:
            return 1.0

        total_profit_ratio = 0.0
        valid_count = 0

        for tx in transactions:
            sell_price = price_map.get(tx.timestamp, 0)
            if sell_price == 0:
                continue

            for inp in tx.inputs:
                age_days = inp.get('age', 0)
                if age_days < min_age_days:
                    continue

                buy_price = inp.get('price', 0)
                if buy_price > 0:
                    profit_ratio = sell_price / buy_price
                    total_profit_ratio += profit_ratio
                    valid_count += 1

        return total_profit_ratio / valid_count if valid_count > 0 else 1.0

    @staticmethod
    def calculate_rhodl_ratio(hodl_1w_1m: float, hodl_1y_2y: float) -> float:
        """
        RHODL Ratio
        短期与长期持有者比率

        RHODL = (1w-1m HODL Wave) / (1y-2y HODL Wave)

        高值表示短期持有者活跃，可能接近顶部
        低值表示长期持有者主导，可能接近底部
        """
        if hodl_1y_2y == 0:
            return 0.0
        return hodl_1w_1m / hodl_1y_2y

    @staticmethod
    def calculate_active_address_sentiment(active_addresses: List[int],
                                          prices: List[float],
                                          window: int = 28) -> float:
        """
        Active Address Sentiment
        活跃地址情绪指标

        比较活跃地址数量与价格的关系
        """
        if len(active_addresses) < window or len(prices) < window:
            return 0.0

        addr_change = (active_addresses[-1] - np.mean(active_addresses[-window:])) / np.mean(active_addresses[-window:])
        price_change = (prices[-1] - np.mean(prices[-window:])) / np.mean(prices[-window:])

        # 价格上涨但地址不活跃 = 负面信号
        # 地址活跃但价格不涨 = 正面信号（积累）
        return addr_change - price_change

    @staticmethod
    def calculate_supply_in_profit(price: float, utxo_set: List[dict]) -> float:
        """
        Supply in Profit
        盈利供应量占比

        计算当前价格下有多少供应量处于盈利状态

        Args:
            price: 当前价格
            utxo_set: [{"value": float, "price": float}] UTXO集合

        Returns:
            盈利供应量占比 (0-1)
        """
        if not utxo_set:
            return 0.0

        total_supply = sum(utxo['value'] for utxo in utxo_set)
        profit_supply = sum(utxo['value'] for utxo in utxo_set
                          if utxo.get('price', 0) < price)

        return profit_supply / total_supply if total_supply > 0 else 0.0

    @staticmethod
    def calculate_coin_days_destroyed(transactions: List[UTXOTransaction]) -> float:
        """
        Coin Days Destroyed (CDD)
        币天销毁

        CDD = Amount × Age (in days)

        衡量长期持有者的移动
        高CDD表示老币在移动
        """
        total_cdd = 0.0

        for tx in transactions:
            for inp in tx.inputs:
                value = inp.get('value', 0)
                age_days = inp.get('age', 0)
                total_cdd += value * age_days

        return total_cdd

    @staticmethod
    def calculate_liveliness(total_cdd: float,
                           circulating_supply: float,
                           days_since_genesis: int) -> float:
        """
        Liveliness
        活跃度

        Liveliness = CDD / (Circulating Supply × Days Since Genesis)

        衡量整体网络的币流动性
        上升 = 老币在移动（分配）
        下降 = 币在积累
        """
        denominator = circulating_supply * days_since_genesis
        if denominator == 0:
            return 0.0
        return total_cdd / denominator

    @staticmethod
    def calculate_dormancy_flow(total_cdd: float,
                               transaction_volume: float) -> float:
        """
        Dormancy Flow
        休眠流

        Dormancy = CDD / Transaction Volume

        高值表示移动的是老币
        """
        if transaction_volume == 0:
            return 0.0
        return total_cdd / transaction_volume
