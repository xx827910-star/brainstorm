"""
Data Abstraction Layer

统一的数据访问接口，支持多数据源路由和故障切换
"""

from typing import Dict, Any, List, Optional
import pandas as pd
from datetime import datetime
import asyncio


class DataAbstractionLayer:
    """
    统一数据访问层

    提供统一的API接口，内部处理：
    - 多数据源路由
    - 故障切换
    - 数据缓存
    - 数据标准化
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.providers = {}
        self.provider_routing = self.config.get('provider_routing', {})

        # 初始化缓存（简化版，实际应使用 Redis）
        self._cache = {}

        # 注册数据提供商
        self._register_providers()

    def _register_providers(self):
        """注册所有数据提供商"""
        # 检查是否使用 Mock 数据
        use_mock = self.config.get('use_mock', True)
        provider_type = self.config.get('provider_type', 'openbb')  # 'openbb', 'yahoo', or 'mock'

        if use_mock:
            from providers.openbb.mock_provider import MockOpenBBProvider
            self.providers['openbb'] = MockOpenBBProvider(self.config.get('openbb', {}))
            print("✅ Using Mock OpenBB Provider (test data)")
        else:
            # 支持多种真实 API 提供商
            if provider_type == 'yahoo':
                try:
                    from providers.openbb.yahoo_provider import YahooFinanceProvider
                    self.providers['openbb'] = YahooFinanceProvider(self.config.get('yahoo', {}))
                    print("✅ Using Yahoo Finance Provider (real API)")
                except ImportError as e:
                    print(f"Warning: Yahoo Finance provider not available: {e}, falling back to Mock")
                    from providers.openbb.mock_provider import MockOpenBBProvider
                    self.providers['openbb'] = MockOpenBBProvider(self.config.get('openbb', {}))
            else:
                try:
                    from providers.openbb.openbb_provider import OpenBBProvider
                    self.providers['openbb'] = OpenBBProvider(self.config.get('openbb', {}))
                    print("✅ Using OpenBB Platform Provider (real API)")
                except ImportError:
                    print("Warning: Real OpenBB provider not available, falling back to Mock")
                    from providers.openbb.mock_provider import MockOpenBBProvider
                    self.providers['openbb'] = MockOpenBBProvider(self.config.get('openbb', {}))

    def _detect_market(self, symbol: str) -> str:
        """
        检测股票所属市场

        Args:
            symbol: 股票代码

        Returns:
            市场代码: 'US', 'CN', 'HK', 'crypto'
        """
        symbol_upper = symbol.upper()

        if symbol_upper.endswith('.SS') or symbol_upper.endswith('.SZ'):
            return 'CN'
        elif symbol_upper.endswith('.HK'):
            return 'HK'
        elif '-' in symbol_upper or symbol_upper.endswith('USD'):
            return 'crypto'
        else:
            return 'US'

    def _get_provider_order(self, market: str, data_type: str) -> List[str]:
        """
        获取数据源优先级顺序

        Args:
            market: 市场代码
            data_type: 数据类型

        Returns:
            数据源列表（按优先级排序）
        """
        # 默认路由规则
        default_routing = {
            'US': {'historical': ['openbb'], 'fundamentals': ['openbb'], 'news': ['openbb']},
            'CN': {'historical': ['openbb'], 'fundamentals': ['openbb'], 'news': ['openbb']},
            'HK': {'historical': ['openbb'], 'fundamentals': ['openbb'], 'news': ['openbb']},
            'crypto': {'historical': ['openbb'], 'fundamentals': ['openbb'], 'news': ['openbb']},
        }

        routing = self.provider_routing or default_routing
        return routing.get(market, {}).get(data_type, ['openbb'])

    def _get_from_cache(self, cache_key: str) -> Optional[Any]:
        """从缓存获取数据"""
        if cache_key in self._cache:
            cached_item = self._cache[cache_key]
            # 检查是否过期（这里简化处理，实际应使用 Redis TTL）
            if cached_item.get('expire_at', float('inf')) > datetime.now().timestamp():
                return cached_item['data']
        return None

    def _set_to_cache(self, cache_key: str, data: Any, ttl: int = 3600):
        """写入缓存"""
        self._cache[cache_key] = {
            'data': data,
            'expire_at': datetime.now().timestamp() + ttl
        }

    async def get_historical_price(
        self,
        symbol: str,
        start_date: str,
        end_date: str,
        use_cache: bool = True
    ) -> pd.DataFrame:
        """
        获取历史价格数据

        Args:
            symbol: 股票代码
            start_date: 开始日期 (YYYY-MM-DD)
            end_date: 结束日期 (YYYY-MM-DD)
            use_cache: 是否使用缓存

        Returns:
            历史价格 DataFrame
        """
        # 检查缓存
        if use_cache:
            cache_key = f"historical:{symbol}:{start_date}:{end_date}"
            cached_data = self._get_from_cache(cache_key)
            if cached_data is not None:
                return cached_data

        # 检测市场并获取数据源优先级
        market = self._detect_market(symbol)
        provider_order = self._get_provider_order(market, 'historical')

        # 尝试从数据源获取数据（按优先级）
        last_error = None
        for provider_name in provider_order:
            try:
                provider = self.providers.get(provider_name)
                if provider is None:
                    continue

                df = await provider.get_equity_historical(
                    symbol=symbol,
                    start_date=start_date,
                    end_date=end_date
                )

                # 缓存结果
                if use_cache:
                    self._set_to_cache(cache_key, df, ttl=3600)

                return df

            except Exception as e:
                last_error = e
                print(f"Provider {provider_name} failed: {str(e)}")
                continue

        # 所有数据源都失败
        raise DataFetchError(
            f"All providers failed for {symbol}. Last error: {str(last_error)}"
        )

    async def get_fundamentals(
        self,
        symbol: str,
        use_cache: bool = True
    ) -> Dict[str, Any]:
        """
        获取基本面数据

        Args:
            symbol: 股票代码
            use_cache: 是否使用缓存

        Returns:
            基本面数据字典
        """
        # 检查缓存
        if use_cache:
            cache_key = f"fundamentals:{symbol}"
            cached_data = self._get_from_cache(cache_key)
            if cached_data is not None:
                return cached_data

        # 检测市场并获取数据源优先级
        market = self._detect_market(symbol)
        provider_order = self._get_provider_order(market, 'fundamentals')

        # 尝试从数据源获取数据
        last_error = None
        for provider_name in provider_order:
            try:
                provider = self.providers.get(provider_name)
                if provider is None:
                    continue

                fundamentals = await provider.get_equity_fundamentals(symbol=symbol)

                # 缓存结果
                if use_cache:
                    self._set_to_cache(cache_key, fundamentals, ttl=86400)  # 24小时

                return fundamentals

            except Exception as e:
                last_error = e
                print(f"Provider {provider_name} failed: {str(e)}")
                continue

        raise DataFetchError(
            f"All providers failed for {symbol}. Last error: {str(last_error)}"
        )

    async def get_news(
        self,
        symbol: str,
        limit: int = 20,
        use_cache: bool = True
    ) -> List[Dict[str, Any]]:
        """
        获取新闻数据

        Args:
            symbol: 股票代码
            limit: 新闻数量限制
            use_cache: 是否使用缓存

        Returns:
            新闻列表
        """
        # 检查缓存
        if use_cache:
            cache_key = f"news:{symbol}:{limit}"
            cached_data = self._get_from_cache(cache_key)
            if cached_data is not None:
                return cached_data

        # 检测市场并获取数据源优先级
        market = self._detect_market(symbol)
        provider_order = self._get_provider_order(market, 'news')

        # 尝试从数据源获取数据
        last_error = None
        for provider_name in provider_order:
            try:
                provider = self.providers.get(provider_name)
                if provider is None:
                    continue

                news = await provider.get_news(symbol=symbol, limit=limit)

                # 缓存结果
                if use_cache:
                    self._set_to_cache(cache_key, news, ttl=1800)  # 30分钟

                return news

            except Exception as e:
                last_error = e
                print(f"Provider {provider_name} failed: {str(e)}")
                continue

        raise DataFetchError(
            f"All providers failed for {symbol}. Last error: {str(last_error)}"
        )

    def get_historical_price_sync(self, symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
        """
        同步版本的历史数据获取（用于兼容旧代码）

        注意：这个方法应该在非async环境中使用。
        如果在async函数中，请直接使用 await get_historical_price()
        """
        try:
            loop = asyncio.get_running_loop()
            # 已经在async环境中了，不能使用 asyncio.run()
            raise RuntimeError(
                "Cannot use sync method in async context. "
                "Use: await dal.get_historical_price() instead"
            )
        except RuntimeError:
            # 不在async环境中，可以安全使用
            return asyncio.run(self.get_historical_price(symbol, start_date, end_date))

    def get_fundamentals_sync(self, symbol: str) -> Dict[str, Any]:
        """同步版本的基本面数据获取"""
        try:
            loop = asyncio.get_running_loop()
            raise RuntimeError(
                "Cannot use sync method in async context. "
                "Use: await dal.get_fundamentals() instead"
            )
        except RuntimeError:
            return asyncio.run(self.get_fundamentals(symbol))

    def get_news_sync(self, symbol: str, limit: int = 20) -> List[Dict[str, Any]]:
        """同步版本的新闻获取"""
        try:
            loop = asyncio.get_running_loop()
            raise RuntimeError(
                "Cannot use sync method in async context. "
                "Use: await dal.get_news() instead"
            )
        except RuntimeError:
            return asyncio.run(self.get_news(symbol, limit))


class DataFetchError(Exception):
    """数据获取错误"""
    pass
