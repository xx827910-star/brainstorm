"""
Real OpenBB API Demo

演示如何使用真实的 OpenBB Platform API
注意：需要安装 openbb 包并配置 API Keys
"""

import asyncio
import sys
import os
from datetime import datetime, timedelta

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data_abstraction import DataAbstractionLayer


async def test_real_openbb():
    """测试真实 OpenBB API"""

    print("\n" + "="*80)
    print("🔌 Testing Real OpenBB Platform API")
    print("="*80 + "\n")

    # 配置使用真实 OpenBB
    config = {
        'use_mock': False,  # 使用真实 API
        'openbb': {
            'provider_preference': {
                'equity_historical': 'yfinance',      # 免费
                'equity_fundamentals': 'yfinance',    # 免费
                'news': 'yfinance',                   # 免费
            }
        }
    }

    try:
        print("⚙️  Initializing Data Abstraction Layer with Real OpenBB...")
        dal = DataAbstractionLayer(config)
        print("✅ Data layer initialized\n")

        # 测试 1: 获取历史数据
        print("📊 Test 1: Fetching historical data for AAPL...")
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=30)

            df = await dal.get_historical_price(
                symbol='AAPL',
                start_date=start_date.strftime('%Y-%m-%d'),
                end_date=end_date.strftime('%Y-%m-%d'),
                use_cache=False  # 不使用缓存，直接测试 API
            )

            print(f"✅ Success! Retrieved {len(df)} days of data")
            print(f"   Latest close: ${df['Close'].iloc[-1]:.2f}")
            print(f"   Data source: {df['data_source'].iloc[0]}")
            print()

        except Exception as e:
            print(f"❌ Failed to fetch historical data: {str(e)}")
            print(f"   Error type: {type(e).__name__}")
            print()

        # 测试 2: 获取基本面数据
        print("💼 Test 2: Fetching fundamental data for TSLA...")
        try:
            fundamentals = await dal.get_fundamentals(symbol='TSLA')

            print(f"✅ Success! Retrieved fundamental data")
            if fundamentals and 'profile' in fundamentals:
                print(f"   Company: {fundamentals['profile'].get('company_name', 'N/A')}")
                print(f"   Sector: {fundamentals['profile'].get('sector', 'N/A')}")
            print()

        except Exception as e:
            print(f"❌ Failed to fetch fundamentals: {str(e)}")
            print(f"   Error type: {type(e).__name__}")
            print()

        # 测试 3: 获取新闻
        print("📰 Test 3: Fetching news for NVDA...")
        try:
            news = await dal.get_news(symbol='NVDA', limit=5)

            print(f"✅ Success! Retrieved {len(news)} news articles")
            if news:
                print(f"   Latest: {news[0]['title'][:60]}...")
            print()

        except Exception as e:
            print(f"❌ Failed to fetch news: {str(e)}")
            print(f"   Error type: {type(e).__name__}")
            print()

    except ImportError as e:
        print("❌ OpenBB is not installed!")
        print(f"\n💡 To install OpenBB, run:")
        print(f"   pip install openbb")
        print(f"\n📚 For more information, visit:")
        print(f"   https://docs.openbb.co/platform/installation")
        return

    except Exception as e:
        print(f"❌ Error initializing OpenBB: {str(e)}")
        return

    print("="*80)
    print("✅ Real OpenBB API Test Complete")
    print("="*80 + "\n")


async def compare_mock_vs_real():
    """对比 Mock 数据和真实 API 的性能"""

    print("\n" + "="*80)
    print("⚖️  Comparing Mock Data vs Real OpenBB API")
    print("="*80 + "\n")

    symbol = 'AAPL'
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)

    # 测试 Mock 数据
    print("🧪 Testing Mock Provider...")
    mock_config = {'use_mock': True}
    mock_dal = DataAbstractionLayer(mock_config)

    mock_start = datetime.now()
    try:
        mock_df = await mock_dal.get_historical_price(
            symbol=symbol,
            start_date=start_date.strftime('%Y-%m-%d'),
            end_date=end_date.strftime('%Y-%m-%d')
        )
        mock_time = (datetime.now() - mock_start).total_seconds()
        print(f"✅ Mock data fetched in {mock_time:.3f} seconds")
        print(f"   Rows: {len(mock_df)}")
        print(f"   Latest close: ${mock_df['Close'].iloc[-1]:.2f}")
    except Exception as e:
        print(f"❌ Mock provider failed: {str(e)}")
        mock_time = None

    print()

    # 测试真实 API
    print("🔌 Testing Real OpenBB API...")
    real_config = {
        'use_mock': False,
        'openbb': {'provider_preference': {'equity_historical': 'yfinance'}}
    }

    try:
        real_dal = DataAbstractionLayer(real_config)

        real_start = datetime.now()
        real_df = await real_dal.get_historical_price(
            symbol=symbol,
            start_date=start_date.strftime('%Y-%m-%d'),
            end_date=end_date.strftime('%Y-%m-%d'),
            use_cache=False
        )
        real_time = (datetime.now() - real_start).total_seconds()
        print(f"✅ Real API data fetched in {real_time:.3f} seconds")
        print(f"   Rows: {len(real_df)}")
        print(f"   Latest close: ${real_df['Close'].iloc[-1]:.2f}")

        # 性能对比
        if mock_time:
            print(f"\n📊 Performance Comparison:")
            print(f"   Mock: {mock_time:.3f}s")
            print(f"   Real: {real_time:.3f}s")
            print(f"   Ratio: {real_time/mock_time:.1f}x slower")

    except ImportError:
        print("❌ OpenBB is not installed")
        print("   Install with: pip install openbb")
    except Exception as e:
        print(f"❌ Real API failed: {str(e)}")

    print()
    print("="*80 + "\n")


async def main():
    """主函数"""

    print("\n" + "="*80)
    print("🚀 OpenBB Platform Integration Test Suite")
    print("="*80)

    # 测试真实 OpenBB API
    await test_real_openbb()

    # 对比 Mock vs Real
    print("\n" + "="*80)
    print("⏭️  Would you like to compare Mock vs Real performance?")
    print("   (This requires OpenBB to be installed)")
    print("="*80 + "\n")

    # 如果有 OpenBB，运行对比测试
    try:
        import openbb
        await compare_mock_vs_real()
    except ImportError:
        print("⏭️  Skipping performance comparison (OpenBB not installed)")
        print()


if __name__ == '__main__':
    asyncio.run(main())
