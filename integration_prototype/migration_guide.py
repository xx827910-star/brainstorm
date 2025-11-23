"""
Migration Guide: TradingAgents Dataflows → Data Abstraction Layer

演示如何将现有的 TradingAgents 数据获取函数迁移到新的数据抽象层
"""

import asyncio
import sys
import os
from datetime import datetime, timedelta
import pandas as pd

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from data_abstraction import DataAbstractionLayer


# ========================================================================
# 原始 TradingAgents 风格的数据获取函数
# ========================================================================

class OriginalTradingAgentsDataflow:
    """模拟原始 TradingAgents 的 dataflows"""

    @staticmethod
    def get_YFin_data(ticker: str, start_date: str, end_date: str) -> pd.DataFrame:
        """
        原始方式：使用 yfinance 直接获取数据
        问题：
        - 单一数据源，没有备用选项
        - 没有缓存机制
        - 没有错误处理和重试
        """
        try:
            import yfinance as yf
            df = yf.download(ticker, start=start_date, end=end_date, progress=False)
            return df
        except Exception as e:
            print(f"❌ yfinance failed: {str(e)}")
            return pd.DataFrame()

    @staticmethod
    def get_stock_fundamentals(ticker: str) -> dict:
        """
        原始方式：使用单一数据源获取基本面
        问题：
        - API 限制
        - 没有故障切换
        - 格式不统一
        """
        try:
            import yfinance as yf
            stock = yf.Ticker(ticker)
            info = stock.info
            return info
        except Exception as e:
            print(f"❌ Failed to get fundamentals: {str(e)}")
            return {}


# ========================================================================
# 新的数据抽象层方式
# ========================================================================

class ModernTradingAgentsDataflow:
    """使用新的数据抽象层"""

    def __init__(self, config: dict = None):
        """初始化数据抽象层"""
        self.dal = DataAbstractionLayer(config or {'use_mock': True})

    async def get_YFin_data(self, ticker: str, start_date: str, end_date: str) -> pd.DataFrame:
        """
        新方式：通过数据抽象层获取数据
        优势：
        - 多数据源支持（OpenBB 提供 35+ 数据源）
        - 自动故障切换
        - 内置缓存
        - 统一的错误处理
        """
        try:
            df = await self.dal.get_historical_price(
                symbol=ticker,
                start_date=start_date,
                end_date=end_date
            )
            return df
        except Exception as e:
            print(f"❌ All data sources failed: {str(e)}")
            return pd.DataFrame()

    async def get_stock_fundamentals(self, ticker: str) -> dict:
        """
        新方式：通过数据抽象层获取基本面
        优势：
        - 多数据源（FMP, yfinance, Intrinio 等）
        - 标准化格式
        - 自动缓存
        """
        try:
            fundamentals = await self.dal.get_fundamentals(symbol=ticker)
            return fundamentals
        except Exception as e:
            print(f"❌ Failed to get fundamentals: {str(e)}")
            return {}

    def get_YFin_data_sync(self, ticker: str, start_date: str, end_date: str) -> pd.DataFrame:
        """同步版本（兼容旧代码）"""
        return asyncio.run(self.get_YFin_data(ticker, start_date, end_date))

    def get_stock_fundamentals_sync(self, ticker: str) -> dict:
        """同步版本（兼容旧代码）"""
        return asyncio.run(self.get_stock_fundamentals(ticker))


# ========================================================================
# 适配器模式：无缝替换
# ========================================================================

class DataflowAdapter:
    """
    适配器：将数据抽象层接口转换为 TradingAgents 原始接口

    用法：
    1. 替换原始的 dataflows import
    2. 使用相同的函数名
    3. 无需修改 Agent 代码
    """

    def __init__(self, dal: DataAbstractionLayer):
        self.dal = dal

    def get_YFin_data(self, ticker: str, start_date: str, end_date: str) -> pd.DataFrame:
        """兼容原始接口"""
        return self.dal.get_historical_price_sync(ticker, start_date, end_date)

    def get_stock_fundamentals(self, ticker: str) -> dict:
        """兼容原始接口"""
        return self.dal.get_fundamentals_sync(ticker)

    def get_stock_news(self, ticker: str, limit: int = 20) -> list:
        """新增功能：获取新闻"""
        return self.dal.get_news_sync(ticker, limit)


# ========================================================================
# 演示和对比
# ========================================================================

async def demo_migration():
    """演示迁移过程"""

    print("\n" + "="*80)
    print("📚 Migration Guide: TradingAgents Dataflows → Data Abstraction Layer")
    print("="*80 + "\n")

    # 示例参数
    ticker = "AAPL"
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    start_str = start_date.strftime('%Y-%m-%d')
    end_str = end_date.strftime('%Y-%m-%d')

    # ========================================
    # 方式 1: 原始方式（仅展示，不实际运行）
    # ========================================
    print("❌ Old Way (Original TradingAgents):")
    print("-" * 80)
    print("""
# 原始代码（存在问题）
from tradingagents.dataflows.interface import get_YFin_data

df = get_YFin_data('AAPL', '2025-01-01', '2025-11-23')

问题：
❌ 单一数据源（yfinance）
❌ 没有故障切换
❌ 没有缓存
❌ API 限制导致频繁失败
❌ 数据格式不一致
    """)
    print()

    # ========================================
    # 方式 2: 新方式（使用数据抽象层）
    # ========================================
    print("✅ New Way (Data Abstraction Layer):")
    print("-" * 80)

    config = {'use_mock': True}  # 使用 Mock 数据演示
    modern_df = ModernTradingAgentsDataflow(config)

    # 异步方式
    print("📊 Async API:")
    df = await modern_df.get_YFin_data(ticker, start_str, end_str)
    print(f"✅ Retrieved {len(df)} days of data")
    print(f"   Latest close: ${df['Close'].iloc[-1]:.2f}")
    print()

    # 同步方式（兼容旧代码） - 注释掉，因为在 async 环境中调用 sync 会冲突
    print("📊 Sync API (Compatible with old code):")
    print("   Note: Use sync version in non-async context")
    print("   Example: df = dal.get_historical_price_sync('AAPL', start, end)")
    print()

    # ========================================
    # 方式 3: 适配器模式（最简单的迁移）
    # ========================================
    print("🔌 Adapter Pattern (Easiest Migration):")
    print("-" * 80)
    print("   Note: Adapter sync methods work in non-async context")
    print("   In this async demo, we'll use the async API directly")
    print()

    # 获取基本面（使用 async API）
    fundamentals = await modern_df.get_stock_fundamentals(ticker)
    if fundamentals and 'profile' in fundamentals:
        print(f"✅ Retrieved fundamental data:")
        print(f"   Company: {fundamentals['profile']['company_name']}")
        print(f"   Sector: {fundamentals['profile']['sector']}")
    print()

    # ========================================
    # 优势对比
    # ========================================
    print("="*80)
    print("📊 Benefits of Data Abstraction Layer:")
    print("="*80)
    print("""
✅ Multi-Provider Support:
   - US stocks: OpenBB (35+ providers including yfinance, FMP, Polygon)
   - CN stocks: Tushare → OpenBB (automatic fallback)
   - HK stocks: OpenBB → Tushare

✅ Intelligent Routing:
   - Automatic market detection (US/CN/HK/crypto)
   - Provider selection based on market
   - Automatic fallback on failure

✅ Performance Optimization:
   - Built-in caching (memory/Redis)
   - Reduced API calls
   - Faster response time

✅ Error Handling:
   - Automatic retry
   - Multiple provider fallback
   - Graceful degradation

✅ Unified Interface:
   - Standardized data format
   - Consistent column names
   - Easy to use API
    """)
    print()


async def demo_migration_steps():
    """演示实际的迁移步骤"""

    print("\n" + "="*80)
    print("🔧 Step-by-Step Migration Guide")
    print("="*80 + "\n")

    print("""
Step 1: Initialize Data Abstraction Layer
==========================================
""")

    print("# In your TradingAgents initialization code:")
    print("""
from data_abstraction import DataAbstractionLayer

# Configure for production
config = {
    'use_mock': False,  # Use real OpenBB
    'openbb': {
        'provider_preference': {
            'equity_historical': 'yfinance',  # Free
            'equity_fundamentals': 'fmp',     # Requires API key
            'news': 'benzinga'                # Requires API key
        }
    },
    'provider_routing': {
        'US': {'historical': ['openbb']},
        'CN': {'historical': ['tushare', 'openbb']},  # Tushare first, then OpenBB
    }
}

dal = DataAbstractionLayer(config)
""")

    print("""
Step 2: Create Adapter
======================
""")

    print("# Create adapter for seamless integration:")
    print("""
from migration_guide import DataflowAdapter

adapter = DataflowAdapter(dal)

# Now you can use it exactly like the old interface:
df = adapter.get_YFin_data('AAPL', '2025-01-01', '2025-11-23')
""")

    print("""
Step 3: Replace in TradingAgents
=================================
""")

    print("# In tradingagents/dataflows/interface.py:")
    print("""
# OLD CODE:
# from .providers.us import get_data_in_range as get_YFin_data

# NEW CODE:
from data_abstraction import DataAbstractionLayer
from migration_guide import DataflowAdapter

# Initialize once
_dal = DataAbstractionLayer(config)
_adapter = DataflowAdapter(_dal)

# Replace functions
def get_YFin_data(ticker, start_date, end_date):
    return _adapter.get_YFin_data(ticker, start_date, end_date)

def get_stock_fundamentals(ticker):
    return _adapter.get_stock_fundamentals(ticker)
""")

    print("""
Step 4: Test
============
""")

    print("# Run your existing tests:")
    print("""
# All existing tests should pass without modification
pytest tests/
""")

    print()


async def main():
    """主函数"""

    # 演示迁移
    await demo_migration()

    # 演示迁移步骤
    await demo_migration_steps()

    print("="*80)
    print("✅ Migration Guide Complete!")
    print("="*80 + "\n")

    print("📚 Next Steps:")
    print("1. Review the code examples above")
    print("2. Install OpenBB: pip install openbb")
    print("3. Configure API keys (optional, yfinance is free)")
    print("4. Follow Step-by-Step Migration Guide")
    print("5. Run tests to verify")
    print()


if __name__ == '__main__':
    asyncio.run(main())
