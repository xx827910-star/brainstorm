"""
Crypto On-Chain Analyzer
加密货币链上数据分析工具包
"""

__version__ = "1.0.0"
__author__ = "Chain Analytics Team"

from .core.models import (
    OnChainSnapshot,
    UTXOTransaction,
    AddressBalance,
    ExchangeFlow,
    MinerData,
    ChainType
)

from .indicators.onchain_metrics import OnChainMetrics
from .indicators.exchange_analytics import ExchangeAnalytics
from .indicators.miner_analytics import MinerAnalytics
from .indicators.address_analytics import AddressAnalytics

from .data.data_loader import DataLoader
from .utils.visualizer import TerminalVisualizer
from .utils.report_generator import ReportGenerator

__all__ = [
    # Models
    'OnChainSnapshot',
    'UTXOTransaction',
    'AddressBalance',
    'ExchangeFlow',
    'MinerData',
    'ChainType',

    # Analytics
    'OnChainMetrics',
    'ExchangeAnalytics',
    'MinerAnalytics',
    'AddressAnalytics',

    # Tools
    'DataLoader',
    'TerminalVisualizer',
    'ReportGenerator',
]
