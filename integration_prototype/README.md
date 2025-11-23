# TradingAgents-CN + OpenBB Integration Prototype

这是一个将 **TradingAgents-CN** 与 **OpenBB Platform** 整合的项目，**支持真实 API 和 Mock 数据**。

🎉 **真实 API 整合已完成！** 详见 [REAL_API_INTEGRATION.md](REAL_API_INTEGRATION.md)

## 📋 项目结构

```
integration_prototype/
├── providers/                           # 数据提供商
│   └── openbb/
│       ├── __init__.py
│       ├── mock_provider.py             # Mock Provider（测试用）
│       ├── yahoo_provider.py            # Yahoo Finance Provider（真实 API）✨NEW
│       └── openbb_provider.py           # OpenBB Platform Provider（真实 API）
├── tests/                               # 测试代码
│   ├── __init__.py
│   ├── test_mock_provider.py            # Mock Provider 测试
│   └── test_agent_integration.py        # Agent 集成测试
├── examples/                            # 示例代码
│   ├── basic_usage.py                   # 基础使用示例
│   ├── agent_demo.py                    # Agent 演示
│   ├── real_openbb_demo.py              # OpenBB 真实 API 演示
│   └── real_api_integration_demo.py     # 真实 API 完整演示 ✨NEW
├── config/                              # 配置文件
│   └── provider_config.yaml             # 数据源配置
├── data_abstraction.py                  # 数据抽象层（支持多数据源）
├── migration_guide.py                   # 迁移指南
├── README.md                            # 本文件
└── REAL_API_INTEGRATION.md              # 真实 API 整合文档 ✨NEW
```

## 🚀 快速开始

### 1. 安装依赖

**基础依赖（必需）：**
```bash
pip install pandas numpy pytest pytest-asyncio pyyaml
```

**真实 API 支持：**
```bash
# 使用 Yahoo Finance API（推荐，免费）
pip install aiohttp

# 或使用完整 OpenBB Platform（可选）
pip install openbb
```

### 2. 运行示例代码

**使用 Mock 数据（无需网络）：**
```bash
cd integration_prototype
python examples/basic_usage.py
```

**使用真实 API（需要网络）：**
```bash
cd integration_prototype
python examples/real_api_integration_demo.py
```

**Agent 完整演示：**
```bash
cd integration_prototype
python examples/agent_demo.py
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

## 🎯 已完成工作

- [x] ✅ Mock Provider 完整实现（9个测试全部通过）
- [x] ✅ 数据抽象层实现（支持多数据源路由和故障切换）
- [x] ✅ 与 Agent 层集成（SimplifiedMarketAnalyst 演示）
- [x] ✅ 11个集成测试全部通过
- [x] ✅ 完整的迁移指南和文档
- [x] ✅ **真实 Yahoo Finance API 集成完成** ✨NEW
- [x] ✅ **多数据源支持（Mock / Yahoo / OpenBB）** ✨NEW
- [x] ✅ **完整的真实 API 演示和文档** ✨NEW

## 🚀 下一步计划

- [ ] 配置真实 OpenBB API Keys
- [ ] 集成 Redis 缓存
- [ ] 与真实 TradingAgents 代码集成
- [ ] 添加更多数据类型支持（期权、期货等）
- [ ] 性能优化和压力测试
- [ ] 生产环境部署

## 📚 相关文档

- [整合设计文档](../INTEGRATION_DESIGN.md) - 详细的架构设计和实现计划
- [OpenBB 文档](https://docs.openbb.co/) - OpenBB Platform 官方文档
- [TradingAgents-CN](https://github.com/hsliuping/TradingAgents-CN) - TradingAgents 中文版

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

本项目遵循原项目的许可证。
