"""
链上数据模型定义
定义了UTXO链（BTC等）和账户链（ETH等）的数据结构
"""
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional, Dict
from enum import Enum


class ChainType(Enum):
    """区块链类型"""
    UTXO = "utxo"  # Bitcoin-like
    ACCOUNT = "account"  # Ethereum-like


@dataclass
class UTXOTransaction:
    """UTXO交易数据"""
    txid: str
    timestamp: datetime
    block_height: int
    inputs: List[Dict]  # [{"address": str, "value": float, "age": int}]
    outputs: List[Dict]  # [{"address": str, "value": float}]
    fee: float
    total_input: float
    total_output: float

    @property
    def realized_price(self) -> float:
        """计算已实现价格（输入的平均成本）"""
        if not self.inputs:
            return 0.0
        total_value = sum(inp.get('value', 0) for inp in self.inputs)
        return total_value / len(self.inputs) if self.inputs else 0.0


@dataclass
class OnChainSnapshot:
    """链上快照数据（某个时间点的状态）"""
    timestamp: datetime
    price: float  # 当前价格
    market_cap: float  # 市值

    # UTXO相关
    circulating_supply: float  # 流通供应量
    realized_cap: Optional[float] = None  # 已实现市值

    # 地址和交易
    active_addresses: int = 0  # 活跃地址数
    new_addresses: int = 0  # 新增地址数
    transaction_count: int = 0  # 交易数量
    transaction_volume: float = 0.0  # 交易量

    # 费用
    total_fees: float = 0.0  # 总手续费
    avg_fee: float = 0.0  # 平均手续费

    # 矿工相关
    miner_revenue: float = 0.0  # 矿工收入（区块奖励+手续费）
    hash_rate: Optional[float] = None  # 算力
    difficulty: Optional[float] = None  # 难度

    # 高级指标原始数据
    transferred_volume: float = 0.0  # 转移量
    dormancy_flow: float = 0.0  # 休眠流


@dataclass
class AddressBalance:
    """地址余额数据"""
    address: str
    balance: float
    first_seen: datetime
    last_active: datetime
    transaction_count: int
    total_received: float
    total_sent: float

    @property
    def age_days(self) -> int:
        """地址年龄（天）"""
        return (datetime.now() - self.first_seen).days


@dataclass
class ExchangeFlow:
    """交易所流入流出数据"""
    timestamp: datetime
    exchange_name: str
    inflow: float  # 流入
    outflow: float  # 流出
    net_flow: float  # 净流入
    reserve: float  # 储备金


@dataclass
class MinerData:
    """矿工行为数据"""
    timestamp: datetime
    miner_address: str
    revenue: float  # 收入
    fees_collected: float  # 收取的手续费
    coins_moved: float  # 转移的币量
    reserve: float  # 持有量
