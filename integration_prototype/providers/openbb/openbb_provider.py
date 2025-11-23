"""
Real OpenBB Provider

使用真实的 OpenBB Platform SDK 获取金融数据
注意：需要安装 openbb 包和配置 API Keys
"""

from typing import Dict, Any, List, Optional
import pandas as pd
from datetime import datetime

try:
    from openbb import obb
    OPENBB_AVAILABLE = True
except ImportError:
    OPENBB_AVAILABLE = False
    print("Warning: OpenBB not installed. Please install with: pip install openbb")


class OpenBBProvider:
    """
    OpenBB 数据提供商适配器
    将 OpenBB Platform 数据转换为 TradingAgents 标准格式
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        if not OPENBB_AVAILABLE:
            raise ImportError(
                "OpenBB is not installed. Please install with: pip install openbb"
            )

        self.config = config or {}

        # 数据提供商偏好设置
        self.provider_preference = self.config.get('provider_preference', {
            'equity_historical': 'yfinance',
            'equity_fundamentals': 'fmp',
            'news': 'benzinga',
        })

    async def get_equity_historical(
        self,
        symbol: str,
        start_date: str,
        end_date: str,
        interval: str = "1d",
        provider: Optional[str] = None
    ) -> pd.DataFrame:
        """
        获取股票历史价格数据

        Args:
            symbol: 股票代码
            start_date: 开始日期 (YYYY-MM-DD)
            end_date: 结束日期 (YYYY-MM-DD)
            interval: 时间间隔 (1d, 1h, etc.)
            provider: 指定数据提供商 (可选)

        Returns:
            标准化的 DataFrame
        """
        try:
            # 选择数据提供商
            provider = provider or self.provider_preference.get('equity_historical')

            # 调用 OpenBB API
            output = obb.equity.price.historical(
                symbol=symbol,
                start_date=start_date,
                end_date=end_date,
                interval=interval,
                provider=provider
            )

            # 转换为 DataFrame
            df = output.to_dataframe()

            # 标准化列名
            df = self._standardize_columns(df, 'equity_historical')

            # 添加元数据
            df['symbol'] = symbol
            df['data_source'] = f'openbb_{provider}'
            df['fetch_time'] = datetime.now()

            return df

        except Exception as e:
            raise DataFetchError(f"Failed to fetch historical data from OpenBB: {str(e)}")

    async def get_equity_fundamentals(
        self,
        symbol: str,
        provider: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        获取股票基本面数据

        Args:
            symbol: 股票代码
            provider: 指定数据提供商

        Returns:
            基本面数据字典
        """
        try:
            provider = provider or self.provider_preference.get('equity_fundamentals')

            # 获取公司概况
            profile = obb.equity.profile(symbol=symbol, provider=provider)

            # 获取财务指标
            metrics = obb.equity.fundamental.metrics(symbol=symbol, provider=provider)

            # 获取财务报表（最近4期）
            income = obb.equity.fundamental.income(
                symbol=symbol,
                provider=provider,
                limit=4
            )
            balance = obb.equity.fundamental.balance(
                symbol=symbol,
                provider=provider,
                limit=4
            )

            # 整合数据
            fundamentals = {
                'profile': self._to_dict_safe(profile),
                'metrics': self._to_dict_safe(metrics),
                'income_statement': self._to_records_safe(income),
                'balance_sheet': self._to_records_safe(balance),
                'data_source': f'openbb_{provider}',
                'fetch_time': datetime.now().isoformat(),
            }

            return fundamentals

        except Exception as e:
            raise DataFetchError(f"Failed to fetch fundamentals from OpenBB: {str(e)}")

    async def get_news(
        self,
        symbol: str,
        limit: int = 20,
        provider: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        获取新闻数据

        Args:
            symbol: 股票代码
            limit: 新闻数量限制
            provider: 指定数据提供商

        Returns:
            新闻列表
        """
        try:
            provider = provider or self.provider_preference.get('news')

            output = obb.news.company(
                symbol=symbol,
                limit=limit,
                provider=provider
            )

            news_df = output.to_dataframe()
            news_list = news_df.to_dict('records')

            # 标准化新闻格式
            standardized_news = []
            for news_item in news_list:
                standardized_news.append({
                    'title': news_item.get('title', ''),
                    'content': news_item.get('text', news_item.get('description', '')),
                    'url': news_item.get('url', ''),
                    'published_at': news_item.get('date', news_item.get('published_utc', '')),
                    'source': news_item.get('source', provider),
                    'symbols': [symbol],
                })

            return standardized_news

        except Exception as e:
            raise DataFetchError(f"Failed to fetch news from OpenBB: {str(e)}")

    def _standardize_columns(self, df: pd.DataFrame, data_type: str) -> pd.DataFrame:
        """
        标准化列名到 TradingAgents 格式

        Args:
            df: 原始 DataFrame
            data_type: 数据类型

        Returns:
            标准化后的 DataFrame
        """
        if data_type == 'equity_historical':
            # OpenBB 可能使用的列名变体
            column_mapping = {
                'date': 'Date',
                'open': 'Open',
                'high': 'High',
                'low': 'Low',
                'close': 'Close',
                'volume': 'Volume',
                'adj_close': 'Adj Close',
            }

            # 只映射存在的列
            existing_mapping = {
                k: v for k, v in column_mapping.items()
                if k in df.columns or k.capitalize() in df.columns
            }

            df = df.rename(columns=existing_mapping)

            # 确保日期列存在
            if 'Date' not in df.columns and df.index.name == 'date':
                df = df.reset_index()
                df = df.rename(columns={'date': 'Date'})

        return df

    def _to_dict_safe(self, output) -> Dict:
        """安全转换为字典"""
        if hasattr(output, 'to_dict'):
            return output.to_dict()
        elif hasattr(output, 'to_dataframe'):
            return output.to_dataframe().to_dict('records')[0]
        else:
            return {}

    def _to_records_safe(self, output) -> List[Dict]:
        """安全转换为记录列表"""
        if hasattr(output, 'to_dataframe'):
            return output.to_dataframe().to_dict('records')
        elif isinstance(output, pd.DataFrame):
            return output.to_dict('records')
        else:
            return []


class DataFetchError(Exception):
    """数据获取错误"""
    pass
