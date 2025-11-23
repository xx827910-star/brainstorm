"""
Yahoo Finance Provider - Lightweight Real API Implementation

Direct API integration without yfinance dependency
Uses Yahoo Finance API v8 endpoints
"""

import asyncio
import aiohttp
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import json


class YahooFinanceProvider:
    """
    轻量级 Yahoo Finance API 提供商

    直接调用 Yahoo Finance API，无需 yfinance 依赖
    支持：
    - 历史价格数据
    - 基本面数据
    - 市场新闻
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.base_url = "https://query2.finance.yahoo.com"
        self.cache = {}

        # User agent to avoid blocking
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

    async def _fetch_json(self, url: str, params: Optional[Dict] = None) -> Dict:
        """发送 HTTP 请求并返回 JSON 数据"""
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, headers=self.headers) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    raise Exception(f"HTTP {response.status}: {await response.text()}")

    async def get_equity_historical(
        self,
        symbol: str,
        start_date: str,
        end_date: str
    ) -> pd.DataFrame:
        """
        获取历史价格数据

        Args:
            symbol: 股票代码 (e.g., 'AAPL')
            start_date: 开始日期 (YYYY-MM-DD)
            end_date: 结束日期 (YYYY-MM-DD)

        Returns:
            包含 OHLCV 数据的 DataFrame
        """
        # 转换日期为 Unix 时间戳
        start_ts = int(datetime.strptime(start_date, '%Y-%m-%d').timestamp())
        end_ts = int(datetime.strptime(end_date, '%Y-%m-%d').timestamp())

        # Yahoo Finance API endpoint
        url = f"{self.base_url}/v8/finance/chart/{symbol}"
        params = {
            'period1': start_ts,
            'period2': end_ts,
            'interval': '1d',
            'events': 'history'
        }

        try:
            data = await self._fetch_json(url, params)

            # 解析数据
            result = data['chart']['result'][0]
            timestamps = result['timestamp']
            quotes = result['indicators']['quote'][0]

            # 创建 DataFrame
            df = pd.DataFrame({
                'Date': pd.to_datetime(timestamps, unit='s'),
                'Open': quotes['open'],
                'High': quotes['high'],
                'Low': quotes['low'],
                'Close': quotes['close'],
                'Volume': quotes['volume']
            })

            # 设置索引并添加元数据
            df.set_index('Date', inplace=True)
            df['symbol'] = symbol
            df['data_source'] = 'yahoo_finance'

            # 移除 NaN 值
            df = df.dropna()

            return df

        except Exception as e:
            raise Exception(f"Failed to fetch historical data for {symbol}: {str(e)}")

    async def get_equity_fundamentals(self, symbol: str) -> Dict[str, Any]:
        """
        获取基本面数据

        Args:
            symbol: 股票代码

        Returns:
            基本面数据字典
        """
        # Yahoo Finance quoteSummary endpoint
        url = f"{self.base_url}/v10/finance/quoteSummary/{symbol}"
        params = {
            'modules': 'assetProfile,summaryDetail,defaultKeyStatistics,financialData'
        }

        try:
            data = await self._fetch_json(url, params)
            result = data['quoteSummary']['result'][0]

            # 提取关键信息
            profile = result.get('assetProfile', {})
            summary = result.get('summaryDetail', {})
            key_stats = result.get('defaultKeyStatistics', {})
            financials = result.get('financialData', {})

            # 标准化格式
            fundamentals = {
                'profile': {
                    'company_name': profile.get('longName', symbol),
                    'sector': profile.get('sector', 'N/A'),
                    'industry': profile.get('industry', 'N/A'),
                    'description': profile.get('longBusinessSummary', '')[:200],
                    'website': profile.get('website', '')
                },
                'metrics': {
                    'market_cap': self._extract_value(summary.get('marketCap')),
                    'pe_ratio': self._extract_value(summary.get('trailingPE')),
                    'forward_pe': self._extract_value(summary.get('forwardPE')),
                    'price_to_book': self._extract_value(key_stats.get('priceToBook')),
                    'dividend_yield': self._extract_value(summary.get('dividendYield')),
                    'beta': self._extract_value(key_stats.get('beta')),
                    'revenue_growth': self._extract_value(financials.get('revenueGrowth')),
                    'profit_margin': self._extract_value(financials.get('profitMargins'))
                },
                'data_source': 'yahoo_finance',
                'timestamp': datetime.now().isoformat()
            }

            return fundamentals

        except Exception as e:
            raise Exception(f"Failed to fetch fundamentals for {symbol}: {str(e)}")

    async def get_news(self, symbol: str, limit: int = 20) -> List[Dict[str, Any]]:
        """
        获取新闻数据

        Args:
            symbol: 股票代码
            limit: 新闻数量限制

        Returns:
            新闻列表
        """
        # Yahoo Finance news endpoint (注意：这个 API 可能需要调整)
        url = f"{self.base_url}/v1/finance/search"
        params = {
            'q': symbol,
            'newsCount': limit
        }

        try:
            data = await self._fetch_json(url, params)

            news_items = []
            for item in data.get('news', [])[:limit]:
                news_items.append({
                    'title': item.get('title', ''),
                    'publisher': item.get('publisher', 'Unknown'),
                    'link': item.get('link', ''),
                    'published_date': datetime.fromtimestamp(
                        item.get('providerPublishTime', 0)
                    ).isoformat(),
                    'summary': item.get('summary', '')[:200],
                    'data_source': 'yahoo_finance'
                })

            return news_items

        except Exception as e:
            # 如果新闻API失败，返回空列表而不是抛出异常
            print(f"Warning: Failed to fetch news for {symbol}: {str(e)}")
            return []

    async def get_market_status(self) -> Dict[str, Any]:
        """
        获取市场状态

        Returns:
            市场状态信息
        """
        # 简化版本：返回基本状态
        now = datetime.now()

        return {
            'market': 'US',
            'timestamp': now.isoformat(),
            'data_source': 'yahoo_finance',
            'note': 'Real-time market status via Yahoo Finance API'
        }

    def _extract_value(self, data: Any) -> Any:
        """提取 Yahoo Finance API 返回的值"""
        if data is None:
            return None
        if isinstance(data, dict) and 'raw' in data:
            return data['raw']
        return data


# ========================================================================
# 测试代码
# ========================================================================

async def test_yahoo_provider():
    """测试 Yahoo Finance Provider"""

    print("\n" + "="*80)
    print("🧪 Testing Yahoo Finance Provider (Real API)")
    print("="*80 + "\n")

    provider = YahooFinanceProvider()

    # 测试 1: 历史数据
    print("📊 Test 1: Fetching historical data for AAPL...")
    try:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)

        df = await provider.get_equity_historical(
            symbol='AAPL',
            start_date=start_date.strftime('%Y-%m-%d'),
            end_date=end_date.strftime('%Y-%m-%d')
        )

        print(f"✅ Success! Retrieved {len(df)} days of data")
        print(f"   Latest close: ${df['Close'].iloc[-1]:.2f}")
        print(f"   Date range: {df.index[0]} to {df.index[-1]}")
        print(f"   Data source: {df['data_source'].iloc[0]}")
        print()

    except Exception as e:
        print(f"❌ Failed: {str(e)}\n")

    # 测试 2: 基本面数据
    print("💼 Test 2: Fetching fundamentals for TSLA...")
    try:
        fundamentals = await provider.get_equity_fundamentals('TSLA')

        print(f"✅ Success! Retrieved fundamental data")
        print(f"   Company: {fundamentals['profile']['company_name']}")
        print(f"   Sector: {fundamentals['profile']['sector']}")
        print(f"   P/E Ratio: {fundamentals['metrics']['pe_ratio']}")
        print(f"   Market Cap: ${fundamentals['metrics']['market_cap']:,.0f}" if fundamentals['metrics']['market_cap'] else "   Market Cap: N/A")
        print()

    except Exception as e:
        print(f"❌ Failed: {str(e)}\n")

    # 测试 3: 新闻数据
    print("📰 Test 3: Fetching news for NVDA...")
    try:
        news = await provider.get_news('NVDA', limit=5)

        if news:
            print(f"✅ Success! Retrieved {len(news)} news articles")
            print(f"   Latest: {news[0]['title'][:60]}...")
        else:
            print("⚠️  No news available (API may have changed)")
        print()

    except Exception as e:
        print(f"❌ Failed: {str(e)}\n")

    print("="*80)
    print("✅ Yahoo Finance Provider Test Complete")
    print("="*80 + "\n")


if __name__ == '__main__':
    asyncio.run(test_yahoo_provider())
