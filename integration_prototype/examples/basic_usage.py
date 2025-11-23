"""
Basic Usage Example - Mock OpenBB Provider

演示如何使用 Mock OpenBB Provider 获取金融数据
"""

import asyncio
import sys
import os
from datetime import datetime, timedelta

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from providers.openbb.mock_provider import MockOpenBBProvider


async def main():
    """主函数"""
    print("=" * 80)
    print("TradingAgents-CN + OpenBB Integration - Mock Data Demo")
    print("=" * 80)
    print()

    # 初始化 Mock Provider
    provider = MockOpenBBProvider()
    print("✅ Mock OpenBB Provider initialized")
    print()

    # 示例 1: 获取美股历史数据
    print("📊 Example 1: Get US Stock Historical Data (AAPL)")
    print("-" * 80)
    # 使用最近的日期范围（Mock 数据生成最近90天的数据）
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)  # 最近30天
    df_aapl = await provider.get_equity_historical(
        symbol='AAPL',
        start_date=start_date.strftime('%Y-%m-%d'),
        end_date=end_date.strftime('%Y-%m-%d')
    )
    print(f"Retrieved {len(df_aapl)} days of data for AAPL")
    print("\nLast 5 days:")
    print(df_aapl[['Date', 'Open', 'High', 'Low', 'Close', 'Volume']].tail())
    print()

    # 示例 2: 获取 A股历史数据
    print("📊 Example 2: Get China A-Share Historical Data (000001.SS)")
    print("-" * 80)
    df_cn = await provider.get_equity_historical(
        symbol='000001.SS',
        start_date=start_date.strftime('%Y-%m-%d'),
        end_date=end_date.strftime('%Y-%m-%d')
    )
    print(f"Retrieved {len(df_cn)} days of data for 000001.SS")
    print("\nLast 5 days:")
    print(df_cn[['Date', 'Open', 'High', 'Low', 'Close', 'Volume']].tail())
    print()

    # 示例 3: 获取基本面数据
    print("💼 Example 3: Get Fundamental Data (TSLA)")
    print("-" * 80)
    fundamentals = await provider.get_equity_fundamentals(symbol='TSLA')

    print("Company Profile:")
    profile = fundamentals['profile']
    print(f"  - Company: {profile['company_name']}")
    print(f"  - Sector: {profile['sector']}")
    print(f"  - Market Cap: ${profile['market_cap']:,.0f}")
    print()

    print("Key Metrics:")
    metrics = fundamentals['metrics']
    print(f"  - P/E Ratio: {metrics['pe_ratio']}")
    print(f"  - P/B Ratio: {metrics['pb_ratio']}")
    print(f"  - Dividend Yield: {metrics['dividend_yield']}%")
    print(f"  - Beta: {metrics['beta']}")
    print()

    print("Recent Quarterly Revenue:")
    income = fundamentals['income_statement']
    for quarter in income:
        print(f"  - {quarter['date']}: ${quarter['revenue']:,.0f}")
    print()

    # 示例 4: 获取新闻数据
    print("📰 Example 4: Get News (NVDA)")
    print("-" * 80)
    news = await provider.get_news(symbol='NVDA', limit=3)

    for i, news_item in enumerate(news, 1):
        print(f"\nNews {i}:")
        print(f"  Title: {news_item['title']}")
        print(f"  Source: {news_item['source']}")
        print(f"  Published: {news_item['published_at'][:10]}")
        print(f"  Sentiment: {news_item['sentiment']}")
        print(f"  URL: {news_item['url']}")
    print()

    # 示例 5: 获取市场概况
    print("🌍 Example 5: Get Market Summary")
    print("-" * 80)
    summary = await provider.get_market_summary(market='US')

    print(f"Market: {summary['market']}")
    print(f"Date: {summary['date']}")
    print(f"Main Index: {summary['indices']['main_index']['value']:.2f}")
    print(f"Change: {summary['indices']['main_index']['change']:.2f} "
          f"({summary['indices']['main_index']['change_percent']:.2f}%)")
    print(f"Total Volume: {summary['volume']:,.0f}")
    print(f"Advancing: {summary['advancing']}, Declining: {summary['declining']}")
    print()

    # 示例 6: 多只股票对比
    print("📈 Example 6: Compare Multiple Stocks")
    print("-" * 80)
    symbols = ['AAPL', 'TSLA', 'NVDA']

    # 使用最近10天的数据
    compare_end = datetime.now()
    compare_start = compare_end - timedelta(days=10)

    for symbol in symbols:
        df = await provider.get_equity_historical(
            symbol=symbol,
            start_date=compare_start.strftime('%Y-%m-%d'),
            end_date=compare_end.strftime('%Y-%m-%d')
        )
        latest_close = df['Close'].iloc[-1]
        first_close = df['Close'].iloc[0]
        change_pct = ((latest_close - first_close) / first_close) * 100

        print(f"{symbol:6s}: ${latest_close:7.2f}  "
              f"Change: {change_pct:+6.2f}%")

    print()
    print("=" * 80)
    print("✅ Demo completed successfully!")
    print("=" * 80)


if __name__ == '__main__':
    asyncio.run(main())
