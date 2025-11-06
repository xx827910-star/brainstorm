"""
数据加载和导入工具
支持多种格式的链上数据导入
"""
import json
import csv
from typing import List, Dict, Optional
from datetime import datetime
from pathlib import Path
from ..core.models import (
    OnChainSnapshot, UTXOTransaction, AddressBalance,
    ExchangeFlow, MinerData
)


class DataLoader:
    """数据加载器"""

    @staticmethod
    def load_snapshots_from_csv(file_path: str) -> List[OnChainSnapshot]:
        """
        从CSV加载链上快照数据

        CSV格式：
        timestamp,price,market_cap,realized_cap,circulating_supply,active_addresses,...
        """
        snapshots = []

        with open(file_path, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                snapshot = OnChainSnapshot(
                    timestamp=datetime.fromisoformat(row['timestamp']),
                    price=float(row['price']),
                    market_cap=float(row['market_cap']),
                    circulating_supply=float(row['circulating_supply']),
                    realized_cap=float(row.get('realized_cap', 0)),
                    active_addresses=int(row.get('active_addresses', 0)),
                    new_addresses=int(row.get('new_addresses', 0)),
                    transaction_count=int(row.get('transaction_count', 0)),
                    transaction_volume=float(row.get('transaction_volume', 0)),
                    total_fees=float(row.get('total_fees', 0)),
                    avg_fee=float(row.get('avg_fee', 0)),
                    miner_revenue=float(row.get('miner_revenue', 0)),
                    hash_rate=float(row.get('hash_rate', 0)) if row.get('hash_rate') else None,
                    difficulty=float(row.get('difficulty', 0)) if row.get('difficulty') else None
                )
                snapshots.append(snapshot)

        return snapshots

    @staticmethod
    def load_transactions_from_json(file_path: str) -> List[UTXOTransaction]:
        """
        从JSON加载交易数据

        JSON格式：
        [
            {
                "txid": "...",
                "timestamp": "2024-01-01T00:00:00",
                "inputs": [{"address": "...", "value": 1.5, "age": 30}],
                "outputs": [{"address": "...", "value": 1.0}],
                ...
            }
        ]
        """
        with open(file_path, 'r') as f:
            data = json.load(f)

        transactions = []
        for tx_data in data:
            tx = UTXOTransaction(
                txid=tx_data['txid'],
                timestamp=datetime.fromisoformat(tx_data['timestamp']),
                block_height=tx_data['block_height'],
                inputs=tx_data['inputs'],
                outputs=tx_data['outputs'],
                fee=tx_data['fee'],
                total_input=tx_data['total_input'],
                total_output=tx_data['total_output']
            )
            transactions.append(tx)

        return transactions

    @staticmethod
    def load_addresses_from_csv(file_path: str) -> List[AddressBalance]:
        """
        从CSV加载地址余额数据

        CSV格式：
        address,balance,first_seen,last_active,transaction_count,total_received,total_sent
        """
        addresses = []

        with open(file_path, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                addr = AddressBalance(
                    address=row['address'],
                    balance=float(row['balance']),
                    first_seen=datetime.fromisoformat(row['first_seen']),
                    last_active=datetime.fromisoformat(row['last_active']),
                    transaction_count=int(row['transaction_count']),
                    total_received=float(row['total_received']),
                    total_sent=float(row['total_sent'])
                )
                addresses.append(addr)

        return addresses

    @staticmethod
    def load_exchange_flows_from_csv(file_path: str) -> List[ExchangeFlow]:
        """
        从CSV加载交易所流动数据

        CSV格式：
        timestamp,exchange_name,inflow,outflow,net_flow,reserve
        """
        flows = []

        with open(file_path, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                flow = ExchangeFlow(
                    timestamp=datetime.fromisoformat(row['timestamp']),
                    exchange_name=row['exchange_name'],
                    inflow=float(row['inflow']),
                    outflow=float(row['outflow']),
                    net_flow=float(row['net_flow']),
                    reserve=float(row['reserve'])
                )
                flows.append(flow)

        return flows

    @staticmethod
    def load_miner_data_from_csv(file_path: str) -> List[MinerData]:
        """
        从CSV加载矿工数据

        CSV格式：
        timestamp,miner_address,revenue,fees_collected,coins_moved,reserve
        """
        miner_data = []

        with open(file_path, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                data = MinerData(
                    timestamp=datetime.fromisoformat(row['timestamp']),
                    miner_address=row['miner_address'],
                    revenue=float(row['revenue']),
                    fees_collected=float(row['fees_collected']),
                    coins_moved=float(row['coins_moved']),
                    reserve=float(row['reserve'])
                )
                miner_data.append(data)

        return miner_data

    @staticmethod
    def export_to_json(data: List, output_path: str):
        """导出数据为JSON"""
        with open(output_path, 'w') as f:
            json.dump([vars(item) for item in data], f, indent=2, default=str)

    @staticmethod
    def create_sample_snapshot_data(days: int = 365) -> List[OnChainSnapshot]:
        """
        生成示例快照数据（用于演示）

        Args:
            days: 生成天数

        Returns:
            模拟的链上快照数据
        """
        import random
        import numpy as np

        snapshots = []
        base_date = datetime(2024, 1, 1)
        base_price = 40000
        base_supply = 19_000_000

        for i in range(days):
            # 模拟价格波动
            price = base_price * (1 + 0.5 * np.sin(i / 30) + random.uniform(-0.05, 0.05))
            price = max(price, 20000)

            # 模拟其他指标
            market_cap = price * base_supply
            realized_cap = market_cap * (0.6 + 0.2 * np.sin(i / 60))

            snapshot = OnChainSnapshot(
                timestamp=base_date.replace(day=1) + timedelta(days=i),
                price=price,
                market_cap=market_cap,
                circulating_supply=base_supply + i * 900 / 365,  # 每天增加900个
                realized_cap=realized_cap,
                active_addresses=random.randint(800_000, 1_200_000),
                new_addresses=random.randint(30_000, 60_000),
                transaction_count=random.randint(250_000, 350_000),
                transaction_volume=random.uniform(2_000_000, 5_000_000) * price,
                total_fees=random.uniform(15, 30),
                avg_fee=random.uniform(2, 8),
                miner_revenue=random.uniform(20, 35) * price,
                hash_rate=random.uniform(300, 500) * 1e18,
                difficulty=random.uniform(50, 70) * 1e12
            )
            snapshots.append(snapshot)

        return snapshots


# 为了兼容导入
from datetime import timedelta
