# TradingAgents-CN + OpenBB Integration Prototype

这是一个将 **TradingAgents-CN** 与 **OpenBB Platform** 整合的原型项目，使用 Mock 数据进行测试。

## 📋 项目结构

```
integration_prototype/
├── providers/                    # 数据提供商
│   └── openbb/
│       ├── __init__.py
│       ├── mock_provider.py      # Mock OpenBB Provider（测试用）
│       └── openbb_provider.py    # 真实 OpenBB Provider
├── tests/                        # 测试代码
│   ├── __init__.py
│   └── test_mock_provider.py     # Mock Provider 测试
├── examples/                     # 示例代码
│   └── basic_usage.py            # 基础使用示例
├── config/                       # 配置文件
│   └── provider_config.yaml      # 数据源配置
└── README.md                     # 本文件
```

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install pandas numpy pytest pytest-asyncio pyyaml
```

如果要使用真实的 OpenBB（可选）：
```bash
pip install openbb
```

### 2. 运行示例代码

运行基础使用示例（使用 Mock 数据）：

```bash
cd integration_prototype
python examples/basic_usage.py
```

### 3. 运行测试

运行所有测试：

```bash
cd integration_prototype
pytest tests/ -v
```

运行特定测试：

```bash
pytest tests/test_mock_provider.py::test_get_equity_historical -v
```

## 📊 功能演示

### 获取历史价格数据

```python
import asyncio
from providers.openbb.mock_provider import MockOpenBBProvider

async def get_stock_data():
    provider = MockOpenBBProvider()

    # 获取 AAPL 历史数据
    df = await provider.get_equity_historical(
        symbol='AAPL',
        start_date='2024-01-01',
        end_date='2024-05-10'
    )

    print(df.tail())

asyncio.run(get_stock_data())
```

### 获取基本面数据

```python
async def get_fundamentals():
    provider = MockOpenBBProvider()

    # 获取基本面数据
    fundamentals = await provider.get_equity_fundamentals(symbol='TSLA')

    print(f"Company: {fundamentals['profile']['company_name']}")
    print(f"P/E Ratio: {fundamentals['metrics']['pe_ratio']}")

asyncio.run(get_fundamentals())
```

### 获取新闻数据

```python
async def get_news():
    provider = MockOpenBBProvider()

    # 获取新闻
    news = await provider.get_news(symbol='NVDA', limit=5)

    for item in news:
        print(f"- {item['title']}")

asyncio.run(get_news())
```

## 🧪 测试覆盖

当前测试覆盖的功能：

- ✅ Mock Provider 初始化
- ✅ 历史价格数据获取
- ✅ 日期过滤功能
- ✅ 基本面数据获取
- ✅ 新闻数据获取
- ✅ 市场概况获取
- ✅ 中国股票数据（A股）
- ✅ 数据一致性验证
- ✅ 动态股票数据生成

运行测试：
```bash
pytest tests/test_mock_provider.py -v --cov=providers
```

## 📈 支持的股票市场

Mock Provider 支持以下市场：

- **美股**：AAPL, TSLA, NVDA, MSFT, GOOGL 等
- **A股**：000001.SS, 600519.SS 等（上交所：.SS，深交所：.SZ）
- **港股**：0700.HK, 9988.HK 等
- **任意股票代码**：自动生成 Mock 数据

## 🔧 配置说明

配置文件位于 `config/provider_config.yaml`：

### 使用 Mock 数据（默认）

```yaml
data_sources:
  openbb:
    use_mock: true  # 使用 Mock 数据
```

### 切换到真实 OpenBB

```yaml
data_sources:
  openbb:
    use_mock: false  # 使用真实 API
    api_keys:
      fmp: your_fmp_api_key
      polygon: your_polygon_api_key
```

## 📝 Mock 数据特性

Mock Provider 生成的数据具有以下特性：

1. **确定性**：同一股票代码生成的数据是一致的（基于哈希种子）
2. **真实性**：价格遵循几何布朗运动，模拟真实市场波动
3. **完整性**：包含 OHLCV、基本面、新闻等完整数据
4. **一致性**：High >= max(Open, Close)，Low <= min(Open, Close)
5. **可缓存**：支持数据缓存，提高性能

## 🎯 下一步计划

- [ ] 实现数据抽象层（Data Abstraction Layer）
- [ ] 集成 Redis 缓存
- [ ] 实现数据源路由和故障切换
- [ ] 与 TradingAgents 的 Agent 层集成
- [ ] 添加更多数据类型支持（期权、期货等）
- [ ] 性能优化和压力测试

## 📚 相关文档

- [整合设计文档](../INTEGRATION_DESIGN.md) - 详细的架构设计和实现计划
- [OpenBB 文档](https://docs.openbb.co/) - OpenBB Platform 官方文档
- [TradingAgents-CN](https://github.com/hsliuping/TradingAgents-CN) - TradingAgents 中文版

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

本项目遵循原项目的许可证。
