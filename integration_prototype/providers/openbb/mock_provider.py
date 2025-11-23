"""
Mock OpenBB Provider for Testing

提供模拟数据，用于测试 TradingAgents 与 OpenBB 的整合逻辑，
无需真实的 API 调用和 API Key。
"""

from typing import Dict, Any, List, Optional
import pandas as pd
from datetime import datetime, timedelta
import numpy as np


class MockOpenBBProvider:
    """
    Mock OpenBB Provider for testing
    返回模拟数据，用于测试整合逻辑
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.mock_data_cache = {}

        # 预加载常用股票的模拟数据
        self._preload_mock_data()

    def _preload_mock_data(self):
        """预加载常见股票的模拟数据"""
        common_symbols = {
            'AAPL': {'name': 'Apple Inc.', 'base_price': 180.0, 'sector': 'Technology'},
            'TSLA': {'name': 'Tesla Inc.', 'base_price': 250.0, 'sector': 'Automotive'},
            'NVDA': {'name': 'NVIDIA Corporation', 'base_price': 450.0, 'sector': 'Technology'},
            '000001.SS': {'name': '平安银行', 'base_price': 15.0, 'sector': 'Finance'},
            '600519.SS': {'name': '贵州茅台', 'base_price': 1800.0, 'sector': 'Consumer'},
        }

        for symbol, info in common_symbols.items():
            self.mock_data_cache[symbol] = self._generate_stock_data(
                symbol=symbol,
                company_name=info['name'],
                base_price=info['base_price'],
                sector=info['sector']
            )

    def _generate_stock_data(
        self,
        symbol: str,
        company_name: str,
        base_price: float,
        sector: str = 'Technology'
    ) -> Dict[str, Any]:
        """
        生成单个股票的完整模拟数据

        Args:
            symbol: 股票代码
            company_name: 公司名称
            base_price: 基础价格
            sector: 行业

        Returns:
            包含历史数据、基本面、新闻的字典
        """
        # 1. 生成历史价格数据（90天）
        historical_df = self._generate_historical_data(symbol, base_price)

        # 2. 生成基本面数据
        fundamentals = self._generate_fundamentals(symbol, company_name, sector, base_price)

        # 3. 生成新闻数据
        news = self._generate_news(symbol, company_name)

        return {
            'historical': historical_df,
            'fundamentals': fundamentals,
            'news': news,
        }

    def _generate_historical_data(self, symbol: str, base_price: float) -> pd.DataFrame:
        """生成历史价格数据"""
        # 生成 90 天的交易日期
        dates = pd.date_range(
            end=datetime.now(),
            periods=90,
            freq='D'
        )

        # 生成价格数据（几何布朗运动模拟）
        np.random.seed(hash(symbol) % 2**32)  # 确保同一股票数据一致
        returns = np.random.randn(90) * 0.02  # 2% 日波动率
        prices = base_price * np.exp(np.cumsum(returns))

        # 生成 OHLCV 数据
        df = pd.DataFrame({
            'Date': dates,
            'Open': prices * (1 + np.random.randn(90) * 0.005),
            'High': prices * (1 + np.abs(np.random.randn(90) * 0.015)),
            'Low': prices * (1 - np.abs(np.random.randn(90) * 0.015)),
            'Close': prices,
            'Volume': np.random.randint(
                int(base_price * 50000),
                int(base_price * 200000),
                90
            ),
        })

        # 确保 High >= max(Open, Close) and Low <= min(Open, Close)
        df['High'] = df[['High', 'Open', 'Close']].max(axis=1)
        df['Low'] = df[['Low', 'Open', 'Close']].min(axis=1)

        # 添加元数据
        df['symbol'] = symbol
        df['data_source'] = 'mock_openbb'
        df['fetch_time'] = datetime.now()

        return df

    def _generate_fundamentals(
        self,
        symbol: str,
        company_name: str,
        sector: str,
        base_price: float
    ) -> Dict[str, Any]:
        """生成基本面数据"""
        # 根据 symbol 生成确定性的随机种子
        np.random.seed(hash(symbol) % 2**32)

        # 公司概况
        profile = {
            'symbol': symbol,
            'company_name': company_name,
            'sector': sector,
            'industry': f'{sector} - Subsector',
            'market_cap': int(base_price * 1e9 * (1 + np.random.rand())),
            'employees': int(50000 + np.random.randint(0, 150000)),
            'founded': str(1980 + np.random.randint(0, 40)),
            'description': f'{company_name} is a leading company in the {sector} sector.',
        }

        # 财务指标
        metrics = {
            'pe_ratio': round(15 + np.random.randn() * 5, 2),
            'pb_ratio': round(3 + np.random.randn() * 2, 2),
            'ps_ratio': round(5 + np.random.randn() * 2, 2),
            'dividend_yield': round(np.abs(np.random.randn() * 2), 2),
            'beta': round(0.8 + np.random.randn() * 0.3, 2),
            'eps': round(base_price * 0.1 * (1 + np.random.randn() * 0.2), 2),
            'roe': round(15 + np.random.randn() * 5, 2),
            'roa': round(8 + np.random.randn() * 3, 2),
            'debt_to_equity': round(0.5 + np.random.rand() * 1.5, 2),
        }

        # 收益表（最近4个季度）
        quarters = pd.date_range(end=datetime.now(), periods=4, freq='QE')  # QE = Quarter End
        base_revenue = base_price * 1e8

        income_statement = []
        for i, quarter in enumerate(quarters):
            growth = (1 + 0.05) ** i  # 5% 季度增长
            income_statement.append({
                'date': quarter.strftime('%Y-%m-%d'),
                'revenue': int(base_revenue * growth * (1 + np.random.randn() * 0.1)),
                'cost_of_revenue': int(base_revenue * growth * 0.6 * (1 + np.random.randn() * 0.1)),
                'gross_profit': int(base_revenue * growth * 0.4 * (1 + np.random.randn() * 0.1)),
                'operating_income': int(base_revenue * growth * 0.2 * (1 + np.random.randn() * 0.1)),
                'net_income': int(base_revenue * growth * 0.15 * (1 + np.random.randn() * 0.1)),
            })

        # 资产负债表
        balance_sheet = []
        for quarter in quarters:
            balance_sheet.append({
                'date': quarter.strftime('%Y-%m-%d'),
                'total_assets': int(base_revenue * 5 * (1 + np.random.randn() * 0.1)),
                'total_liabilities': int(base_revenue * 2 * (1 + np.random.randn() * 0.1)),
                'total_equity': int(base_revenue * 3 * (1 + np.random.randn() * 0.1)),
                'cash': int(base_revenue * 1.5 * (1 + np.random.randn() * 0.1)),
                'debt': int(base_revenue * 1.2 * (1 + np.random.randn() * 0.1)),
            })

        return {
            'profile': profile,
            'metrics': metrics,
            'income_statement': income_statement,
            'balance_sheet': balance_sheet,
            'data_source': 'mock_openbb',
            'fetch_time': datetime.now().isoformat(),
        }

    def _generate_news(self, symbol: str, company_name: str) -> List[Dict[str, Any]]:
        """生成新闻数据"""
        news_templates = [
            f'{company_name} announces new product innovation',
            f'{company_name} Q4 earnings beat analyst expectations',
            f'{company_name} CEO discusses future growth strategy',
            f'Analysts upgrade {symbol} rating to Buy',
            f'{company_name} expands into new markets',
            f'{company_name} reports strong quarterly results',
            f'Market watch: {symbol} shows resilience amid volatility',
        ]

        news = []
        for i, template in enumerate(news_templates[:5]):  # 返回5条新闻
            news.append({
                'title': template,
                'content': f'Mock news content for {company_name}. This is a simulated news article about {symbol}. '
                          f'The company has shown strong performance and continues to innovate in its sector.',
                'url': f'https://example.com/news/{symbol}/{i+1}',
                'published_at': (datetime.now() - timedelta(days=i+1)).isoformat(),
                'source': 'Mock Financial News',
                'symbols': [symbol],
                'sentiment': ['positive', 'neutral', 'positive', 'positive', 'neutral'][i],
            })

        return news

    async def get_equity_historical(
        self,
        symbol: str,
        start_date: str,
        end_date: str,
        interval: str = '1d',
        **kwargs
    ) -> pd.DataFrame:
        """
        获取股票历史价格数据

        Args:
            symbol: 股票代码
            start_date: 开始日期 (YYYY-MM-DD)
            end_date: 结束日期 (YYYY-MM-DD)
            interval: 时间间隔 (默认: 1d)

        Returns:
            历史价格 DataFrame
        """
        # 如果缓存中没有，则生成新数据
        if symbol not in self.mock_data_cache:
            self.mock_data_cache[symbol] = self._generate_stock_data(
                symbol=symbol,
                company_name=f'Company {symbol}',
                base_price=100.0 + hash(symbol) % 500,
                sector='Technology'
            )

        # 获取历史数据
        df = self.mock_data_cache[symbol]['historical'].copy()

        # 按日期过滤
        df['Date'] = pd.to_datetime(df['Date'])
        start = pd.to_datetime(start_date)
        end = pd.to_datetime(end_date)
        df = df[(df['Date'] >= start) & (df['Date'] <= end)]

        # 重置索引
        df = df.reset_index(drop=True)

        return df

    async def get_equity_fundamentals(
        self,
        symbol: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        获取股票基本面数据

        Args:
            symbol: 股票代码

        Returns:
            基本面数据字典
        """
        if symbol not in self.mock_data_cache:
            self.mock_data_cache[symbol] = self._generate_stock_data(
                symbol=symbol,
                company_name=f'Company {symbol}',
                base_price=100.0 + hash(symbol) % 500,
                sector='Technology'
            )

        return self.mock_data_cache[symbol]['fundamentals']

    async def get_news(
        self,
        symbol: str,
        limit: int = 20,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """
        获取新闻数据

        Args:
            symbol: 股票代码
            limit: 新闻数量限制

        Returns:
            新闻列表
        """
        if symbol not in self.mock_data_cache:
            self.mock_data_cache[symbol] = self._generate_stock_data(
                symbol=symbol,
                company_name=f'Company {symbol}',
                base_price=100.0 + hash(symbol) % 500,
                sector='Technology'
            )

        return self.mock_data_cache[symbol]['news'][:limit]

    async def get_market_summary(self, market: str = 'US') -> Dict[str, Any]:
        """
        获取市场概况

        Args:
            market: 市场代码 (US, CN, HK, etc.)

        Returns:
            市场概况数据
        """
        np.random.seed(hash(market) % 2**32)

        return {
            'market': market,
            'date': datetime.now().strftime('%Y-%m-%d'),
            'indices': {
                'main_index': {
                    'name': 'Market Index',
                    'value': 4500 + np.random.randn() * 100,
                    'change': round(np.random.randn() * 50, 2),
                    'change_percent': round(np.random.randn() * 1.5, 2),
                },
            },
            'volume': int(5e9 + np.random.randn() * 1e9),
            'advancing': int(1500 + np.random.randint(-200, 200)),
            'declining': int(1500 + np.random.randint(-200, 200)),
            'data_source': 'mock_openbb',
        }


class DataFetchError(Exception):
    """数据获取错误"""
    pass
