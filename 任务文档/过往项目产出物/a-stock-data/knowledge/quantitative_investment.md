# 🤖 量化投资：从定性到定量

---

## 一、量化投资基础

### 1.1 量化投资概述

#### 定义
- **量化投资**：使用数学模型和统计方法进行投资决策
- **核心思想**：通过数据寻找规律，利用计算机执行策略

#### 量化投资特点
- **系统化**：基于规则，排除主观判断
- **纪律性**：严格执行策略
- **可验证**：通过历史数据回测验证策略

### 1.2 常见量化因子

#### 价值因子（Value Factors）
| 因子 | 计算方法 | 解读 |
|------|---------|------|
| **PE** | 市盈率 = 股价/每股收益 | 越低越好 |
| **PB** | 市净率 = 股价/每股净资产 | 越低越好 |
| **PS** | 市销率 = 股价/每股销售额 | 越低越好 |
| **EV/EBITDA** | 企业价值/息税折旧摊销前利润 | 越低越好 |

#### 成长因子（Growth Factors）
| 因子 | 计算方法 | 解读 |
|------|---------|------|
| **营收增速** | 同比营收增长率 | 越高越好 |
| **净利润增速** | 同比净利润增长率 | 越高越好 |
| **ROE增速** | 同比ROE增长率 | 越高越好 |
| **EPS增速** | 同比每股收益增长率 | 越高越好 |

#### 质量因子（Quality Factors）
| 因子 | 计算方法 | 解读 |
|------|---------|------|
| **ROE** | 净资产收益率 | 越高越好 |
| **毛利率** | 毛利率 | 越高越好 |
| **净利率** | 净利率 | 越高越好 |
| **经营现金流** | 经营活动产生的现金流 | 越高越好 |

#### 动量因子（Momentum Factors）
| 因子 | 计算方法 | 解读 |
|------|---------|------|
| **1月动量** | 过去1个月收益率 | 越高越好 |
| **3月动量** | 过去3个月收益率 | 越高越好 |
| **6月动量** | 过去6个月收益率 | 越高越好 |
| **12月动量** | 过去12个月收益率（排除最近1个月） | 越高越好 |

---

## 二、因子有效性分析

### 2.1 因子回测方法

```python
def factor_backtest(factor_data, price_data):
    """
    因子回测
    
    参数：
    - factor_data: 因子数据（包含因子值和股票代码）
    - price_data: 股票价格数据
    
    返回：
    - 因子收益率曲线
    - 夏普比率
    - 最大回撤
    """
    # 按月分组
    groups = factor_data.groupby('month')
    
    # 计算每组收益
    returns = []
    for month, group in groups:
        # 按因子值排序，分成5组
        group = group.sort_values('factor_value')
        quintiles = pd.qcut(group['factor_value'], 5, labels=False)
        
        # 计算每组下月收益
        next_month = month + 1
        group['next_return'] = group['code'].map(
            lambda x: price_data.loc[next_month, x] / price_data.loc[month, x] - 1
        )
        
        # 记录第5组（因子值最高）的收益
        top_quintile = group[quintiles == 4]
        returns.append(top_quintile['next_return'].mean())
    
    # 计算统计指标
    cumulative_return = (1 + pd.Series(returns)).cumprod()
    sharpe_ratio = np.mean(returns) / np.std(returns) * np.sqrt(12)
    max_drawdown = (cumulative_return / cumulative_return.cummax() - 1).min()
    
    return {
        'returns': returns,
        'cumulative_return': cumulative_return,
        'sharpe_ratio': sharpe_ratio,
        'max_drawdown': max_drawdown
    }
```

### 2.2 因子有效性判断标准

| 标准 | 优秀 | 良好 | 一般 | 差 |
|------|------|------|------|------|
| **IC值** | >0.15 | 0.1-0.15 | 0.05-0.1 | <0.05 |
| **IR值** | >0.5 | 0.3-0.5 | 0.1-0.3 | <0.1 |
| **年化收益** | >15% | 10%-15% | 5%-10% | <5% |
| **夏普比率** | >1.5 | 1.0-1.5 | 0.5-1.0 | <0.5 |

### 2.3 因子正交化

```python
def factor_orthogonalization(factor_matrix):
    """
    因子正交化
    
    使用逐步回归消除因子之间的相关性
    
    参数：
    - factor_matrix: 因子矩阵（每行一个股票，每列一个因子）
    
    返回：
    - 正交化后的因子矩阵
    """
    orthogonal_factors = pd.DataFrame(index=factor_matrix.index)
    
    for i, factor in enumerate(factor_matrix.columns):
        if i == 0:
            # 第一个因子保持不变
            orthogonal_factors[factor] = factor_matrix[factor]
        else:
            # 对前面的因子做回归，取残差作为正交化因子
            X = orthogonal_factors.iloc[:, :i]
            y = factor_matrix[factor]
            model = LinearRegression().fit(X, y)
            orthogonal_factors[factor] = y - model.predict(X)
    
    return orthogonal_factors
```

---

## 三、多因子模型构建

### 3.1 多因子模型框架

```python
class MultiFactorModel:
    """
    多因子选股模型
    
    步骤：
    1. 因子选择与预处理
    2. 因子正交化
    3. 因子权重确定
    4. 股票评分计算
    5. 组合构建
    """
    
    def __init__(self, factors):
        self.factors = factors
        self.weights = {}
        self.model = None
    
    def train(self, factor_data, return_data):
        """训练模型"""
        # 因子正交化
        orthogonal_factors = factor_orthogonalization(factor_data)
        
        # 使用线性回归确定因子权重
        self.model = LinearRegression()
        self.model.fit(orthogonal_factors, return_data)
        
        # 保存权重
        for i, factor in enumerate(self.factors):
            self.weights[factor] = self.model.coef_[i]
    
    def predict(self, factor_data):
        """预测股票收益"""
        orthogonal_factors = factor_orthogonalization(factor_data)
        return self.model.predict(orthogonal_factors)
    
    def score_stocks(self, factor_data):
        """给股票打分"""
        # 计算综合得分
        score = pd.Series(0, index=factor_data.index)
        for factor, weight in self.weights.items():
            score += factor_data[factor] * weight
        return score
```

### 3.2 因子权重确定方法

#### 方法1：回归法
- 使用历史数据进行线性回归
- 系数即为因子权重

#### 方法2：IC加权
- 按因子IC值加权
- IC值越高的因子权重越大

#### 方法3：机器学习方法
- 使用随机森林、梯度提升等算法
- 自动学习因子权重

### 3.3 多因子模型实战

```python
def build_multi_factor_model():
    """
    构建多因子选股模型
    
    选择的因子：
    - 价值因子：PE、PB
    - 质量因子：ROE、毛利率
    - 成长因子：营收增速、净利润增速
    - 动量因子：6月动量
    """
    # 初始化模型
    factors = ['pe', 'pb', 'roe', 'gross_margin', 'revenue_growth', 'profit_growth', 'momentum_6m']
    model = MultiFactorModel(factors)
    
    # 获取训练数据
    factor_data = get_factor_data(start_date='2020-01-01', end_date='2023-12-31')
    return_data = get_return_data(start_date='2020-01-01', end_date='2023-12-31')
    
    # 训练模型
    model.train(factor_data, return_data)
    
    # 输出因子权重
    print("因子权重：")
    for factor, weight in model.weights.items():
        print(f"  {factor}: {weight:.4f}")
    
    return model
```

---

## 四、策略回测与验证

### 4.1 回测基本流程

```python
def backtest_strategy(strategy, data, initial_capital=1000000):
    """
    策略回测
    
    参数：
    - strategy: 策略函数
    - data: 回测数据
    - initial_capital: 初始资金
    
    返回：
    - 账户净值曲线
    - 收益统计指标
    """
    # 初始化账户
    portfolio = {
        'cash': initial_capital,
        'stocks': {},
        'nav': [initial_capital]
    }
    
    # 按时间顺序执行策略
    for date in data.index[:-1]:
        # 获取当日数据
        today_data = data.loc[date]
        
        # 执行策略
        portfolio = strategy(today_data, portfolio)
        
        # 更新净值
        total_value = portfolio['cash']
        for stock, shares in portfolio['stocks'].items():
            price = data.loc[date, stock]
            total_value += shares * price
        portfolio['nav'].append(total_value)
    
    # 计算统计指标
    nav_series = pd.Series(portfolio['nav'], index=data.index)
    returns = nav_series.pct_change().dropna()
    
    stats = {
        'total_return': (nav_series.iloc[-1] / nav_series.iloc[0] - 1) * 100,
        'annualized_return': (1 + returns.mean()) ** 252 - 1,
        'max_drawdown': (nav_series / nav_series.cummax() - 1).min() * 100,
        'sharpe_ratio': returns.mean() / returns.std() * np.sqrt(252),
        'win_rate': (returns > 0).mean() * 100
    }
    
    return nav_series, stats
```

### 4.2 回测常见陷阱

#### 幸存者偏差（Survivorship Bias）
- **问题**：只考虑当前存在的股票，忽略已退市的股票
- **解决方法**：使用包含退市股票的完整数据库

#### 未来函数（Look-ahead Bias）
- **问题**：使用了未来的数据
- **解决方法**：确保只使用历史数据

#### 过拟合（Overfitting）
- **问题**：模型在历史数据上表现好，但未来表现差
- **解决方法**：
  - 使用样本外数据验证
  - 限制参数数量
  - 使用正则化

### 4.3 策略评价指标

| 指标 | 计算公式 | 解读 |
|------|---------|------|
| **总收益率** | (期末净值-期初净值)/期初净值 | 策略总收益 |
| **年化收益率** | (1+日收益率)^252 - 1 | 年化收益能力 |
| **最大回撤** | 最大(净值/最高净值 - 1) | 风险承受能力 |
| **夏普比率** | 年化收益率/年化波动率 | 风险调整后收益 |
| **胜率** | 盈利天数/总交易天数 | 策略准确性 |
| **盈亏比** | 平均盈利/平均亏损 | 收益质量 |

---

## 五、多因子选股实战

### 5.1 选股流程

```python
def multi_factor_selection(model, factor_data, top_n=10):
    """
    使用多因子模型选股
    
    参数：
    - model: 训练好的多因子模型
    - factor_data: 最新因子数据
    - top_n: 选出的股票数量
    
    返回：
    - 选出的股票列表
    """
    # 计算股票得分
    scores = model.score_stocks(factor_data)
    
    # 选出得分最高的股票
    top_stocks = scores.sort_values(ascending=False).head(top_n)
    
    return top_stocks.index.tolist()
```

### 5.2 每周选股示例

```python
def weekly_factor_selection():
    """
    每周多因子选股
    
    流程：
    1. 获取最新因子数据
    2. 使用模型打分
    3. 选出前10只股票
    4. 生成投资建议
    """
    # 加载模型
    model = load_model('multi_factor_model.pkl')
    
    # 获取最新数据
    factor_data = get_latest_factor_data()
    
    # 选股
    selected_stocks = multi_factor_selection(model, factor_data, top_n=10)
    
    # 输出结果
    print("📊 本周多因子选股结果：")
    for i, stock in enumerate(selected_stocks, 1):
        print(f"{i}. {stock}")
    
    return selected_stocks
```

### 5.3 风险控制

#### 仓位限制
- **单只股票仓位**：不超过10%-15%
- **单一行业仓位**：不超过30%

#### 止损策略
- **止损线**：单只股票亏损10%止损
- **动态止损**：随盈利提高止损线

---

## 六、量化策略优化与迭代

### 6.1 策略优化方法

#### 参数优化
- 使用网格搜索或遗传算法优化参数
- 避免过度优化

#### 因子更新
- 定期评估因子有效性
- 加入新的有效因子
- 移除失效因子

### 6.2 策略监控

```python
def monitor_strategy(strategy, live_data):
    """
    实时监控策略表现
    
    参数：
    - strategy: 策略名称
    - live_data: 实时市场数据
    """
    # 检查策略表现
    current_return = calculate_current_return(strategy)
    max_drawdown = calculate_max_drawdown(strategy)
    
    # 检查预警条件
    if max_drawdown > -20:  # 回撤超过20%
        print(f"⚠️ {strategy}回撤超过20%，需要检查")
    
    if current_return < -10:  # 当月亏损超过10%
        print(f"⚠️ {strategy}当月亏损超过10%，需要检查")
```

### 6.3 策略迭代

#### 迭代流程
1. **监控表现**：定期检查策略表现
2. **分析问题**：找出表现不佳的原因
3. **优化调整**：调整因子权重或加入新因子
4. **回测验证**：使用历史数据验证调整效果
5. **实盘测试**：小仓位实盘测试

---

## 七、总结与建议

### 7.1 关键要点
1. **因子选择**：选择有效且稳定的因子
2. **模型构建**：使用多因子模型提高选股准确性
3. **回测验证**：充分回测，避免过拟合
4. **风险控制**：设置仓位限制和止损

### 7.2 投资建议
- **从简单开始**：先从单因子策略开始
- **逐步复杂**：逐步增加因子数量
- **持续学习**：跟踪最新的量化研究成果
- **保持谨慎**：量化策略也可能失效

---

## 📚 参考资料

- 《量化投资：策略与技术》（丁鹏）
- 《主动投资组合管理》（Richard Grinold）
- Barra风险模型
- 多因子模型研究论文

---

*最后更新：2026年5月*
*版本：1.0*