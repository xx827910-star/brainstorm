# 🔗 Crypto On-Chain Analyzer

一个强大的加密货币链上数据分析工具包，无需外部API调用，支持离线分析。

## ✨ 特性

### 核心链上指标

- **MVRV (Market Value to Realized Value)** - 市场价值与已实现价值比率
- **MVRV Z-Score** - 标准化MVRV指标
- **NUPL (Net Unrealized Profit/Loss)** - 净未实现盈亏
- **SOPR (Spent Output Profit Ratio)** - 已花费输出利润率
- **aSOPR** - 调整后SOPR（过滤短期交易）
- **NVT (Network Value to Transactions)** - 网络价值与交易比率
- **RVT (Realized Value to Transactions)** - 已实现价值与交易比率
- **Reserve Risk** - 储备风险指标
- **Supply in Profit** - 盈利供应量占比

### 交易所分析

- **净流入/流出分析** - 追踪资金在交易所的流动
- **巨鲸转账检测** - 识别大额转账
- **交易所储备比率** - Exchange Supply Ratio (ESR)
- **积累/分配阶段识别** - 判断市场处于积累还是分配阶段
- **卖压检测** - 识别潜在的卖出压力
- **交易所主导地位分析** - 各交易所储备占比

### 矿工行为分析

- **Puell Multiple** - 矿工收入倍数
- **矿工持仓指数 (MPI)** - Miner Position Index
- **矿工投降分析** - 识别矿工投降信号
- **Hash Ribbons** - 算力带指标
- **Difficulty Ribbon** - 难度带及压缩分析
- **矿工资金流动模式** - 追踪矿工卖出行为

### 地址分析

- **活跃地址趋势** - Active Address Analysis
- **巨鲸识别和追踪** - Whale Tracking
- **供应分布分析** - Supply Distribution
- **基尼系数** - Gini Coefficient（财富不平等度）
- **休眠币分析** - Dormant Coins Analysis
- **HODL Waves** - 持币时间分布
- **聪明钱识别** - Smart Money Detection
- **实体集中度分析** - Entity Concentration

### 可视化工具

- **ASCII线图** - 终端友好的价格趋势图
- **柱状图** - 数据对比可视化
- **仪表盘** - 指标状态显示
- **迷你图 (Sparkline)** - 紧凑的趋势展示
- **表格** - 结构化数据展示

## 🚀 快速开始

### 安装依赖

```bash
pip install numpy
```

### 运行演示

```bash
# 生成完整的链上分析报告（使用演示数据）
python -m crypto_onchain_analyzer.cli report --demo

# 交互式模式
python -m crypto_onchain_analyzer.cli interactive
```

## 📊 使用示例

### 1. 生成完整报告

```bash
# 使用演示数据
python -m crypto_onchain_analyzer.cli report --demo

# 使用自己的数据
python -m crypto_onchain_analyzer.cli report \
  --snapshots data/snapshots.csv \
  --addresses data/addresses.csv \
  --exchanges data/exchanges.csv \
  --miners data/miners.csv
```

### 2. 生成示例数据

```bash
# 生成365天的示例数据
python -m crypto_onchain_analyzer.cli generate --days 365 --output ./data/
```

### 3. 计算单个指标

```bash
# 计算MVRV
python -m crypto_onchain_analyzer.cli metric --type mvrv --snapshots data/snapshots.csv

# 计算NUPL
python -m crypto_onchain_analyzer.cli metric --type nupl --snapshots data/snapshots.csv
```

### 4. Python API使用

```python
from crypto_onchain_analyzer import (
    DataLoader,
    OnChainMetrics,
    ReportGenerator
)

# 加载数据
loader = DataLoader()
snapshots = loader.create_sample_snapshot_data(365)

# 计算指标
metrics = OnChainMetrics()
latest = snapshots[-1]
mvrv = metrics.calculate_mvrv(
    latest.market_cap,
    latest.realized_cap
)
print(f"MVRV: {mvrv:.2f}")

# 生成报告
generator = ReportGenerator()
report = generator.generate_full_report(snapshots)
print(report)
```

## 📁 数据格式

### 快照数据 (snapshots.csv)

```csv
timestamp,price,market_cap,realized_cap,circulating_supply,active_addresses,...
2024-01-01T00:00:00,40000,760000000000,532000000000,19000000,950000,...
```

### 地址数据 (addresses.csv)

```csv
address,balance,first_seen,last_active,transaction_count,total_received,total_sent
bc1q...,1500.5,2020-01-01T00:00:00,2024-01-01T00:00:00,150,2000.0,500.5
```

### 交易所流动 (exchanges.csv)

```csv
timestamp,exchange_name,inflow,outflow,net_flow,reserve
2024-01-01T00:00:00,Binance,1200.5,800.3,400.2,125000
```

### 矿工数据 (miners.csv)

```csv
timestamp,miner_address,revenue,fees_collected,coins_moved,reserve
2024-01-01T00:00:00,miner_1,25.5,2.3,15.0,3500
```

## 🎯 核心指标解读

### MVRV (Market Value to Realized Value)

- **> 3.7**: 历史顶部区域，极度高估
- **> 2.4**: 可能过热，需谨慎
- **1.0 - 2.4**: 合理估值范围
- **< 1.0**: 历史底部区域，价值投资机会

### NUPL (Net Unrealized Profit/Loss)

- **> 0.75**: 贪婪/狂热阶段
- **0.5 - 0.75**: 乐观/焦虑
- **0.25 - 0.5**: 希望/恐惧
- **0 - 0.25**: 投降/愤怒
- **< 0**: 投降/绝望

### Puell Multiple

- **> 4**: 矿工收入极高，可能接近顶部
- **0.5 - 4**: 正常范围
- **< 0.5**: 矿工收入极低，可能接近底部

### Exchange Supply Ratio (ESR)

- **下降**: 供应离开交易所，看涨信号
- **上升**: 供应流入交易所，可能准备卖出

## 🏗️ 架构设计

```
crypto_onchain_analyzer/
├── core/                   # 核心数据模型
│   └── models.py          # OnChainSnapshot, UTXOTransaction等
├── indicators/            # 指标计算引擎
│   ├── onchain_metrics.py    # 核心链上指标
│   ├── exchange_analytics.py # 交易所分析
│   ├── miner_analytics.py    # 矿工分析
│   └── address_analytics.py  # 地址分析
├── data/                  # 数据加载
│   └── data_loader.py    # CSV/JSON数据导入
├── utils/                 # 工具
│   ├── visualizer.py     # ASCII可视化
│   └── report_generator.py # 报告生成
└── cli.py                # 命令行接口
```

## 🔬 高级功能

### 自定义指标计算

```python
from crypto_onchain_analyzer.indicators.onchain_metrics import OnChainMetrics

metrics = OnChainMetrics()

# 计算多个指标
mvrv = metrics.calculate_mvrv(market_cap, realized_cap)
nupl = metrics.calculate_nupl(market_cap, realized_cap, supply)
nvt = metrics.calculate_nvt(market_cap, tx_volume)
```

### 交易所流动分析

```python
from crypto_onchain_analyzer.indicators.exchange_analytics import ExchangeAnalytics

analytics = ExchangeAnalytics()

# 检测积累/分配阶段
phase = analytics.identify_accumulation_distribution(flows, 30)
print(f"Market Phase: {phase}")

# 检测巨鲸转账
whale_movements = analytics.detect_whale_movements(flows, threshold=100)
```

### 矿工行为分析

```python
from crypto_onchain_analyzer.indicators.miner_analytics import MinerAnalytics

miner = MinerAnalytics()

# 计算Puell Multiple
puell = miner.calculate_puell_multiple(miner_data)

# 分析投降状态
capitulation = miner.analyze_miner_capitulation(snapshots, miner_data)
print(f"Status: {capitulation['status']}")
```

## 📈 实际应用场景

1. **量化交易策略开发**
   - 基于链上指标构建交易信号
   - 回测历史数据验证策略有效性

2. **市场周期判断**
   - 识别市场顶部和底部
   - 判断当前处于牛市还是熊市阶段

3. **风险管理**
   - 监控链上异常活动
   - 评估市场恐慌和贪婪程度

4. **投资决策支持**
   - 长期投资时机选择
   - 资产配置优化

5. **研究和教育**
   - 学习链上数据分析方法
   - 理解市场运作机制

## 🛠️ 扩展开发

### 添加自定义指标

```python
# 在 indicators/onchain_metrics.py 中添加新方法

@staticmethod
def calculate_custom_metric(data: List[float]) -> float:
    """
    自定义指标计算
    """
    # 你的计算逻辑
    return result
```

### 添加新的数据源

```python
# 在 data/data_loader.py 中添加新的加载器

@staticmethod
def load_from_custom_source(source: str) -> List[OnChainSnapshot]:
    """
    从自定义数据源加载
    """
    # 你的加载逻辑
    return snapshots
```

## 🤝 贡献

欢迎贡献代码、报告问题或提出新功能建议！

## 📄 许可证

MIT License

## 🙏 致谢

- Bitcoin 和 Ethereum 社区的链上分析研究
- Glassnode, CryptoQuant 等平台提供的指标灵感
- 开源社区的支持

## 📚 参考资料

- [Glassnode Academy](https://academy.glassnode.com/)
- [Bitcoin On-Chain Analysis](https://bitcoin.org)
- [Ethereum Analytics](https://ethereum.org)

---

**注意**: 本工具仅供研究和教育目的。投资决策应基于多方面分析，链上数据只是其中一个参考维度。
