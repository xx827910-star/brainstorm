"""
Tests for Mock OpenBB Provider

测试 Mock Provider 的功能，确保生成的数据格式正确
"""

import pytest
import pandas as pd
from datetime import datetime, timedelta
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from providers.openbb.mock_provider import MockOpenBBProvider


@pytest.mark.asyncio
async def test_mock_provider_initialization():
    """测试 Mock Provider 初始化"""
    provider = MockOpenBBProvider()

    assert provider is not None
    assert 'AAPL' in provider.mock_data_cache
    assert '000001.SS' in provider.mock_data_cache


@pytest.mark.asyncio
async def test_get_equity_historical():
    """测试获取历史数据"""
    provider = MockOpenBBProvider()

    # 测试获取 AAPL 历史数据
    df = await provider.get_equity_historical(
        symbol='AAPL',
        start_date=(datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'),
        end_date=datetime.now().strftime('%Y-%m-%d')
    )

    # 验证返回的数据
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    assert 'Date' in df.columns
    assert 'Open' in df.columns
    assert 'High' in df.columns
    assert 'Low' in df.columns
    assert 'Close' in df.columns
    assert 'Volume' in df.columns
    assert 'symbol' in df.columns
    assert 'data_source' in df.columns

    # 验证数据质量
    assert df['symbol'].iloc[0] == 'AAPL'
    assert df['data_source'].iloc[0] == 'mock_openbb'
    assert (df['High'] >= df['Low']).all()
    assert (df['High'] >= df['Open']).all()
    assert (df['High'] >= df['Close']).all()
    assert (df['Low'] <= df['Open']).all()
    assert (df['Low'] <= df['Close']).all()


@pytest.mark.asyncio
async def test_get_equity_historical_date_filter():
    """测试日期过滤功能"""
    provider = MockOpenBBProvider()

    start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    end_date = datetime.now().strftime('%Y-%m-%d')

    df = await provider.get_equity_historical(
        symbol='TSLA',
        start_date=start_date,
        end_date=end_date
    )

    # 验证日期范围
    assert (df['Date'] >= pd.to_datetime(start_date)).all()
    assert (df['Date'] <= pd.to_datetime(end_date)).all()


@pytest.mark.asyncio
async def test_get_equity_fundamentals():
    """测试获取基本面数据"""
    provider = MockOpenBBProvider()

    fundamentals = await provider.get_equity_fundamentals(symbol='AAPL')

    # 验证基本面数据结构
    assert isinstance(fundamentals, dict)
    assert 'profile' in fundamentals
    assert 'metrics' in fundamentals
    assert 'income_statement' in fundamentals
    assert 'balance_sheet' in fundamentals
    assert 'data_source' in fundamentals

    # 验证 profile
    profile = fundamentals['profile']
    assert 'symbol' in profile
    assert 'company_name' in profile
    assert 'sector' in profile
    assert profile['symbol'] == 'AAPL'

    # 验证 metrics
    metrics = fundamentals['metrics']
    assert 'pe_ratio' in metrics
    assert 'pb_ratio' in metrics
    assert 'dividend_yield' in metrics
    assert 'beta' in metrics

    # 验证收益表
    income_statement = fundamentals['income_statement']
    assert isinstance(income_statement, list)
    assert len(income_statement) == 4  # 4个季度
    assert 'revenue' in income_statement[0]
    assert 'net_income' in income_statement[0]

    # 验证资产负债表
    balance_sheet = fundamentals['balance_sheet']
    assert isinstance(balance_sheet, list)
    assert len(balance_sheet) == 4
    assert 'total_assets' in balance_sheet[0]
    assert 'total_equity' in balance_sheet[0]


@pytest.mark.asyncio
async def test_get_news():
    """测试获取新闻数据"""
    provider = MockOpenBBProvider()

    news = await provider.get_news(symbol='NVDA', limit=5)

    # 验证新闻数据
    assert isinstance(news, list)
    assert len(news) == 5

    # 验证每条新闻的结构
    for news_item in news:
        assert 'title' in news_item
        assert 'content' in news_item
        assert 'url' in news_item
        assert 'published_at' in news_item
        assert 'source' in news_item
        assert 'symbols' in news_item
        assert 'sentiment' in news_item

        # 验证新闻内容不为空
        assert news_item['title']
        assert news_item['content']
        assert 'NVDA' in news_item['symbols']


@pytest.mark.asyncio
async def test_get_market_summary():
    """测试获取市场概况"""
    provider = MockOpenBBProvider()

    summary = await provider.get_market_summary(market='US')

    # 验证市场概况数据
    assert isinstance(summary, dict)
    assert 'market' in summary
    assert 'date' in summary
    assert 'indices' in summary
    assert 'volume' in summary
    assert summary['market'] == 'US'


@pytest.mark.asyncio
async def test_chinese_stock():
    """测试中国股票数据"""
    provider = MockOpenBBProvider()

    # 测试 A股
    df = await provider.get_equity_historical(
        symbol='000001.SS',
        start_date=(datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'),
        end_date=datetime.now().strftime('%Y-%m-%d')
    )

    assert not df.empty
    assert df['symbol'].iloc[0] == '000001.SS'

    # 测试基本面
    fundamentals = await provider.get_equity_fundamentals(symbol='600519.SS')
    assert fundamentals['profile']['symbol'] == '600519.SS'


@pytest.mark.asyncio
async def test_data_consistency():
    """测试数据一致性（同一股票多次请求应返回相同数据）"""
    provider = MockOpenBBProvider()

    # 第一次请求
    df1 = await provider.get_equity_historical(
        symbol='AAPL',
        start_date='2024-03-01',
        end_date='2024-03-31'
    )

    # 第二次请求
    df2 = await provider.get_equity_historical(
        symbol='AAPL',
        start_date='2024-03-01',
        end_date='2024-03-31'
    )

    # 验证两次请求返回的数据相同
    pd.testing.assert_frame_equal(
        df1[['Date', 'Close']],
        df2[['Date', 'Close']]
    )


@pytest.mark.asyncio
async def test_dynamic_stock_generation():
    """测试动态生成新股票数据"""
    provider = MockOpenBBProvider()

    # 请求一个不在预加载列表中的股票
    new_symbol = 'NEWSTOCK'
    df = await provider.get_equity_historical(
        symbol=new_symbol,
        start_date=(datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'),
        end_date=datetime.now().strftime('%Y-%m-%d')
    )

    # 验证动态生成的数据
    assert not df.empty
    assert df['symbol'].iloc[0] == new_symbol

    # 验证股票已被缓存
    assert new_symbol in provider.mock_data_cache


if __name__ == '__main__':
    # 运行测试
    pytest.main([__file__, '-v', '-s'])
