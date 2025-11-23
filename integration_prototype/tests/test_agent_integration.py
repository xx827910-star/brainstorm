"""
Tests for Agent Integration

测试数据抽象层与 Agent 的集成
"""

import pytest
import sys
import os
from datetime import datetime, timedelta

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data_abstraction import DataAbstractionLayer
from agent_demo import SimplifiedMarketAnalyst


@pytest.mark.asyncio
async def test_data_abstraction_layer_initialization():
    """测试数据抽象层初始化"""
    config = {'use_mock': True}
    dal = DataAbstractionLayer(config)

    assert dal is not None
    assert 'openbb' in dal.providers
    assert dal.config['use_mock'] is True


@pytest.mark.asyncio
async def test_get_historical_price_with_dal():
    """测试通过数据抽象层获取历史数据"""
    config = {'use_mock': True}
    dal = DataAbstractionLayer(config)

    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)

    df = await dal.get_historical_price(
        symbol='AAPL',
        start_date=start_date.strftime('%Y-%m-%d'),
        end_date=end_date.strftime('%Y-%m-%d')
    )

    assert not df.empty
    assert 'Close' in df.columns
    assert 'Volume' in df.columns


@pytest.mark.asyncio
async def test_get_fundamentals_with_dal():
    """测试通过数据抽象层获取基本面数据"""
    config = {'use_mock': True}
    dal = DataAbstractionLayer(config)

    fundamentals = await dal.get_fundamentals(symbol='TSLA')

    assert fundamentals is not None
    assert 'profile' in fundamentals
    assert 'metrics' in fundamentals
    assert fundamentals['profile']['symbol'] == 'TSLA'


@pytest.mark.asyncio
async def test_get_news_with_dal():
    """测试通过数据抽象层获取新闻"""
    config = {'use_mock': True}
    dal = DataAbstractionLayer(config)

    news = await dal.get_news(symbol='NVDA', limit=5)

    assert isinstance(news, list)
    assert len(news) > 0
    assert 'title' in news[0]
    assert 'content' in news[0]


@pytest.mark.asyncio
async def test_market_detection():
    """测试市场检测功能"""
    config = {'use_mock': True}
    dal = DataAbstractionLayer(config)

    assert dal._detect_market('AAPL') == 'US'
    assert dal._detect_market('000001.SS') == 'CN'
    assert dal._detect_market('0700.HK') == 'HK'
    assert dal._detect_market('BTC-USD') == 'crypto'


@pytest.mark.asyncio
async def test_cache_functionality():
    """测试缓存功能"""
    config = {'use_mock': True}
    dal = DataAbstractionLayer(config)

    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)

    # 第一次请求（应该会缓存）
    df1 = await dal.get_historical_price(
        symbol='AAPL',
        start_date=start_date.strftime('%Y-%m-%d'),
        end_date=end_date.strftime('%Y-%m-%d'),
        use_cache=True
    )

    # 第二次请求（应该从缓存读取）
    df2 = await dal.get_historical_price(
        symbol='AAPL',
        start_date=start_date.strftime('%Y-%m-%d'),
        end_date=end_date.strftime('%Y-%m-%d'),
        use_cache=True
    )

    # 验证两次请求返回的数据相同
    assert len(df1) == len(df2)
    assert df1['Close'].iloc[-1] == df2['Close'].iloc[-1]


@pytest.mark.asyncio
async def test_simplified_market_analyst():
    """测试简化版市场分析师"""
    config = {'use_mock': True}
    dal = DataAbstractionLayer(config)
    analyst = SimplifiedMarketAnalyst(dal)

    assert analyst is not None
    assert analyst.data_layer is not None


@pytest.mark.asyncio
async def test_market_analyst_analysis():
    """测试市场分析师分析功能"""
    config = {'use_mock': True}
    dal = DataAbstractionLayer(config)
    analyst = SimplifiedMarketAnalyst(dal)

    # 运行分析
    report = await analyst.analyze_stock('AAPL')

    # 验证报告结构
    assert report is not None
    assert 'symbol' in report
    assert 'current_price' in report
    assert 'indicators' in report
    assert 'trend_analysis' in report
    assert 'score' in report
    assert 'recommendation' in report
    assert 'report_text' in report

    # 验证报告内容
    assert report['symbol'] == 'AAPL'
    assert report['current_price'] > 0
    assert 0 <= report['score'] <= 100
    assert report['recommendation'] in ['强烈买入', '买入', '持有', '观望']


@pytest.mark.asyncio
async def test_market_analyst_indicators():
    """测试技术指标计算"""
    config = {'use_mock': True}
    dal = DataAbstractionLayer(config)
    analyst = SimplifiedMarketAnalyst(dal)

    # 获取历史数据
    end_date = datetime.now()
    start_date = end_date - timedelta(days=90)

    df = await dal.get_historical_price(
        symbol='TSLA',
        start_date=start_date.strftime('%Y-%m-%d'),
        end_date=end_date.strftime('%Y-%m-%d')
    )

    # 计算指标
    indicators = analyst._calculate_indicators(df)

    # 验证指标
    assert 'current_price' in indicators
    assert 'ma_5' in indicators
    assert 'ma_20' in indicators
    assert 'ma_50' in indicators
    assert 'price_change_1d' in indicators
    assert 'volume_ratio' in indicators

    # 验证指标值合理
    assert indicators['current_price'] > 0
    assert indicators['ma_5'] > 0
    assert indicators['ma_20'] > 0
    assert indicators['volume_ratio'] > 0


@pytest.mark.asyncio
async def test_market_analyst_trend_analysis():
    """测试趋势分析"""
    config = {'use_mock': True}
    dal = DataAbstractionLayer(config)
    analyst = SimplifiedMarketAnalyst(dal)

    # 获取历史数据
    end_date = datetime.now()
    start_date = end_date - timedelta(days=90)

    df = await dal.get_historical_price(
        symbol='NVDA',
        start_date=start_date.strftime('%Y-%m-%d'),
        end_date=end_date.strftime('%Y-%m-%d')
    )

    # 分析趋势
    trend = analyst._analyze_trend(df)

    # 验证趋势分析结果
    assert 'short_term' in trend
    assert 'medium_term' in trend
    assert 'volatility' in trend

    assert trend['short_term'] in ['强势上涨', '温和上涨', '温和下跌', '强势下跌']
    assert trend['medium_term'] in ['强势上涨', '温和上涨', '温和下跌', '强势下跌']
    assert trend['volatility'] in ['高波动', '中等波动', '低波动']


@pytest.mark.asyncio
async def test_multiple_symbols_analysis():
    """测试多个股票分析"""
    config = {'use_mock': True}
    dal = DataAbstractionLayer(config)
    analyst = SimplifiedMarketAnalyst(dal)

    symbols = ['AAPL', '000001.SS', 'TSLA']
    reports = []

    for symbol in symbols:
        report = await analyst.analyze_stock(symbol)
        reports.append(report)

    # 验证所有报告都生成成功
    assert len(reports) == 3

    # 验证每个报告的符号正确
    for i, symbol in enumerate(symbols):
        assert reports[i]['symbol'] == symbol
        assert reports[i]['current_price'] > 0


if __name__ == '__main__':
    pytest.main([__file__, '-v', '-s'])
