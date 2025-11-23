"""
Simplified Market Analyst Demo

演示如何将新的数据抽象层与类似 TradingAgents 的 Agent 集成
使用 Mock 数据进行完整的分析流程测试
"""

import asyncio
import sys
import os
from datetime import datetime, timedelta
from typing import Dict, Any, List

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from data_abstraction import DataAbstractionLayer


class SimplifiedMarketAnalyst:
    """
    简化版市场分析师

    模拟 TradingAgents Market Analyst 的核心功能：
    - 获取历史价格数据
    - 计算技术指标
    - 分析市场趋势
    - 生成分析报告
    """

    def __init__(self, data_layer: DataAbstractionLayer):
        self.data_layer = data_layer

    async def analyze_stock(
        self,
        symbol: str,
        analysis_date: str = None
    ) -> Dict[str, Any]:
        """
        分析股票

        Args:
            symbol: 股票代码
            analysis_date: 分析日期（默认为今天）

        Returns:
            分析结果字典
        """
        print(f"\n{'='*80}")
        print(f"📊 Market Analyst - Analyzing {symbol}")
        print(f"{'='*80}\n")

        if analysis_date is None:
            analysis_date = datetime.now().strftime('%Y-%m-%d')

        # 步骤 1: 获取历史数据
        print("📈 Step 1: Fetching historical price data...")
        end_date = datetime.strptime(analysis_date, '%Y-%m-%d')
        start_date = end_date - timedelta(days=90)  # 90天历史数据

        historical_data = await self.data_layer.get_historical_price(
            symbol=symbol,
            start_date=start_date.strftime('%Y-%m-%d'),
            end_date=end_date.strftime('%Y-%m-%d')
        )

        print(f"✅ Retrieved {len(historical_data)} days of historical data")
        print(f"   Date range: {historical_data['Date'].min()} to {historical_data['Date'].max()}")
        print(f"   Latest close: ${historical_data['Close'].iloc[-1]:.2f}")

        # 步骤 2: 计算技术指标
        print("\n📊 Step 2: Calculating technical indicators...")
        indicators = self._calculate_indicators(historical_data)
        print(f"✅ Calculated indicators:")
        for key, value in indicators.items():
            if isinstance(value, float):
                print(f"   - {key}: {value:.2f}")
            else:
                print(f"   - {key}: {value}")

        # 步骤 3: 分析价格趋势
        print("\n📉 Step 3: Analyzing price trend...")
        trend_analysis = self._analyze_trend(historical_data)
        print(f"✅ Trend analysis:")
        print(f"   - Short-term trend: {trend_analysis['short_term']}")
        print(f"   - Medium-term trend: {trend_analysis['medium_term']}")
        print(f"   - Volatility: {trend_analysis['volatility']}")

        # 步骤 4: 获取基本面数据
        print("\n💼 Step 4: Fetching fundamental data...")
        try:
            fundamentals = await self.data_layer.get_fundamentals(symbol=symbol)
            print(f"✅ Retrieved fundamental data:")
            print(f"   - Company: {fundamentals['profile']['company_name']}")
            print(f"   - Sector: {fundamentals['profile']['sector']}")
            print(f"   - P/E Ratio: {fundamentals['metrics']['pe_ratio']:.2f}")
            print(f"   - Market Cap: ${fundamentals['profile']['market_cap']:,.0f}")
        except Exception as e:
            print(f"⚠️  Could not retrieve fundamentals: {str(e)}")
            fundamentals = None

        # 步骤 5: 获取新闻数据
        print("\n📰 Step 5: Fetching news...")
        try:
            news = await self.data_layer.get_news(symbol=symbol, limit=5)
            print(f"✅ Retrieved {len(news)} news articles:")
            for i, article in enumerate(news[:3], 1):
                print(f"   {i}. {article['title']}")
                print(f"      Sentiment: {article.get('sentiment', 'N/A')}")
        except Exception as e:
            print(f"⚠️  Could not retrieve news: {str(e)}")
            news = []

        # 步骤 6: 生成分析报告
        print("\n📝 Step 6: Generating analysis report...")
        report = self._generate_report(
            symbol=symbol,
            historical_data=historical_data,
            indicators=indicators,
            trend_analysis=trend_analysis,
            fundamentals=fundamentals,
            news=news
        )

        print(f"\n{'='*80}")
        print("✅ Analysis Complete!")
        print(f"{'='*80}\n")

        return report

    def _calculate_indicators(self, df) -> Dict[str, float]:
        """计算技术指标"""
        # 移动平均线
        ma_5 = df['Close'].tail(5).mean()
        ma_20 = df['Close'].tail(20).mean()
        ma_50 = df['Close'].tail(50).mean()

        # 当前价格
        current_price = df['Close'].iloc[-1]

        # 价格变化
        price_change_1d = ((df['Close'].iloc[-1] - df['Close'].iloc[-2]) / df['Close'].iloc[-2]) * 100
        price_change_5d = ((df['Close'].iloc[-1] - df['Close'].iloc[-6]) / df['Close'].iloc[-6]) * 100
        price_change_20d = ((df['Close'].iloc[-1] - df['Close'].iloc[-21]) / df['Close'].iloc[-21]) * 100

        # 成交量
        avg_volume = df['Volume'].tail(20).mean()
        current_volume = df['Volume'].iloc[-1]
        volume_ratio = current_volume / avg_volume

        return {
            'current_price': current_price,
            'ma_5': ma_5,
            'ma_20': ma_20,
            'ma_50': ma_50,
            'price_change_1d': price_change_1d,
            'price_change_5d': price_change_5d,
            'price_change_20d': price_change_20d,
            'avg_volume': avg_volume,
            'current_volume': current_volume,
            'volume_ratio': volume_ratio,
        }

    def _analyze_trend(self, df) -> Dict[str, str]:
        """分析价格趋势"""
        # 短期趋势（5天）
        short_term_change = ((df['Close'].iloc[-1] - df['Close'].iloc[-6]) / df['Close'].iloc[-6]) * 100

        if short_term_change > 2:
            short_term = "强势上涨"
        elif short_term_change > 0:
            short_term = "温和上涨"
        elif short_term_change > -2:
            short_term = "温和下跌"
        else:
            short_term = "强势下跌"

        # 中期趋势（20天）
        medium_term_change = ((df['Close'].iloc[-1] - df['Close'].iloc[-21]) / df['Close'].iloc[-21]) * 100

        if medium_term_change > 5:
            medium_term = "强势上涨"
        elif medium_term_change > 0:
            medium_term = "温和上涨"
        elif medium_term_change > -5:
            medium_term = "温和下跌"
        else:
            medium_term = "强势下跌"

        # 波动率
        volatility = df['Close'].tail(20).std() / df['Close'].tail(20).mean() * 100

        if volatility > 3:
            volatility_level = "高波动"
        elif volatility > 1.5:
            volatility_level = "中等波动"
        else:
            volatility_level = "低波动"

        return {
            'short_term': short_term,
            'medium_term': medium_term,
            'volatility': volatility_level,
            'short_term_change_pct': short_term_change,
            'medium_term_change_pct': medium_term_change,
            'volatility_pct': volatility,
        }

    def _generate_report(
        self,
        symbol: str,
        historical_data,
        indicators: Dict,
        trend_analysis: Dict,
        fundamentals: Dict,
        news: List[Dict]
    ) -> Dict[str, Any]:
        """生成分析报告"""

        # 综合评分
        score = 0

        # 趋势评分
        if trend_analysis['short_term'] in ['强势上涨', '温和上涨']:
            score += 20
        if trend_analysis['medium_term'] in ['强势上涨', '温和上涨']:
            score += 20

        # 技术指标评分
        if indicators['current_price'] > indicators['ma_20']:
            score += 15
        if indicators['ma_5'] > indicators['ma_20']:
            score += 15

        # 成交量评分
        if indicators['volume_ratio'] > 1.2:
            score += 10

        # 基本面评分（如果有）
        if fundamentals:
            pe = fundamentals['metrics'].get('pe_ratio', 0)
            if 10 < pe < 30:  # 合理的PE范围
                score += 10

        # 新闻情绪评分
        if news:
            positive_count = sum(1 for n in news if n.get('sentiment') == 'positive')
            if positive_count > len(news) / 2:
                score += 10

        # 综合建议
        if score >= 70:
            recommendation = "强烈买入"
        elif score >= 50:
            recommendation = "买入"
        elif score >= 30:
            recommendation = "持有"
        else:
            recommendation = "观望"

        # 生成报告
        report = {
            'symbol': symbol,
            'analysis_date': datetime.now().strftime('%Y-%m-%d'),
            'current_price': indicators['current_price'],
            'indicators': indicators,
            'trend_analysis': trend_analysis,
            'fundamentals': fundamentals,
            'news_summary': {
                'total_articles': len(news),
                'recent_articles': news[:3] if news else []
            },
            'score': score,
            'recommendation': recommendation,
            'report_text': self._format_report_text(
                symbol, indicators, trend_analysis, fundamentals, news, score, recommendation
            )
        }

        return report

    def _format_report_text(
        self,
        symbol: str,
        indicators: Dict,
        trend_analysis: Dict,
        fundamentals: Dict,
        news: List,
        score: int,
        recommendation: str
    ) -> str:
        """格式化报告文本"""

        lines = [
            f"\n{'='*80}",
            f"📊 Market Analysis Report - {symbol}",
            f"{'='*80}",
            f"\n📈 Current Market Status:",
            f"   Price: ${indicators['current_price']:.2f}",
            f"   1-Day Change: {indicators['price_change_1d']:+.2f}%",
            f"   5-Day Change: {indicators['price_change_5d']:+.2f}%",
            f"   20-Day Change: {indicators['price_change_20d']:+.2f}%",
            f"\n📊 Technical Indicators:",
            f"   MA(5): ${indicators['ma_5']:.2f}",
            f"   MA(20): ${indicators['ma_20']:.2f}",
            f"   MA(50): ${indicators['ma_50']:.2f}",
            f"   Volume Ratio: {indicators['volume_ratio']:.2f}x",
            f"\n📉 Trend Analysis:",
            f"   Short-term (5d): {trend_analysis['short_term']} ({trend_analysis['short_term_change_pct']:+.2f}%)",
            f"   Medium-term (20d): {trend_analysis['medium_term']} ({trend_analysis['medium_term_change_pct']:+.2f}%)",
            f"   Volatility: {trend_analysis['volatility']} ({trend_analysis['volatility_pct']:.2f}%)",
        ]

        if fundamentals:
            lines.extend([
                f"\n💼 Fundamental Data:",
                f"   Company: {fundamentals['profile']['company_name']}",
                f"   Sector: {fundamentals['profile']['sector']}",
                f"   P/E Ratio: {fundamentals['metrics']['pe_ratio']:.2f}",
                f"   P/B Ratio: {fundamentals['metrics']['pb_ratio']:.2f}",
                f"   Market Cap: ${fundamentals['profile']['market_cap']:,.0f}",
            ])

        if news:
            lines.extend([
                f"\n📰 Recent News ({len(news)} articles):",
            ])
            for i, article in enumerate(news[:3], 1):
                lines.append(f"   {i}. {article['title'][:60]}...")
                lines.append(f"      Sentiment: {article.get('sentiment', 'N/A')}")

        lines.extend([
            f"\n🎯 Overall Analysis:",
            f"   Score: {score}/100",
            f"   Recommendation: {recommendation}",
            f"\n{'='*80}",
        ])

        return '\n'.join(lines)


async def main():
    """主函数 - 演示完整的分析流程"""

    print("\n" + "="*80)
    print("🚀 TradingAgents + OpenBB Integration Demo")
    print("   Market Analyst with Mock Data")
    print("="*80 + "\n")

    # 初始化数据抽象层（使用 Mock 数据）
    config = {
        'use_mock': True,  # 使用 Mock 数据
        'provider_routing': {
            'US': {'historical': ['openbb'], 'fundamentals': ['openbb'], 'news': ['openbb']},
            'CN': {'historical': ['openbb'], 'fundamentals': ['openbb'], 'news': ['openbb']},
        }
    }

    print("⚙️  Initializing Data Abstraction Layer...")
    data_layer = DataAbstractionLayer(config)
    print("✅ Data layer initialized (using Mock data)\n")

    # 创建市场分析师
    print("🤖 Creating Market Analyst agent...")
    analyst = SimplifiedMarketAnalyst(data_layer)
    print("✅ Market Analyst created\n")

    # 分析多只股票
    symbols = ['AAPL', '000001.SS', 'TSLA']

    for symbol in symbols:
        try:
            # 运行分析
            report = await analyst.analyze_stock(symbol)

            # 打印报告
            print(report['report_text'])

            # 等待一秒，让输出更清晰
            await asyncio.sleep(1)

        except Exception as e:
            print(f"\n❌ Error analyzing {symbol}: {str(e)}\n")

    print("\n" + "="*80)
    print("✅ Demo Complete!")
    print("="*80 + "\n")


if __name__ == '__main__':
    asyncio.run(main())
