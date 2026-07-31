# 供应链-ARIMA预测器

## name
供应链-ARIMA预测器

## description
使用ARIMA（自回归积分滑动平均）模型对历史需求序列进行时间序列预测，输出未来N期的需求预测值及置信区间。ARIMA适合处理具有趋势性但无明显季节性的需求数据。适用于供应链需求预测、库存计划、产能规划、采购计划等场景。触发词：ARIMA、时间序列预测、需求预测、自回归、移动平均、趋势预测。排除词：指数平滑（指Holt-Winters方法）、促销预测（指促销增量预测）。

## category
atomic-calculator

## sub_category
供应链

## domain
供应链管理

## formula_reference
concept_registry.预测.ARIMA

## inputs
### 必填参数
| 参数名 | 类型 | 说明 | 示例 |
|--------|------|------|------|
| historical_demand | array[float] | 历史需求时间序列（按时间顺序） | [120, 135, 110, 145, 130, 150, 125, 140, 155, 128, 160, 148] |

### 可选参数
| 参数名 | 类型 | 说明 | 估值逻辑 |
|--------|------|------|----------|
| arima_order | object | ARIMA参数(p,d,q) | 默认自动选择：使用AIC准则进行网格搜索，p∈[0,5], d∈[0,2], q∈[0,5] |
| forecast_periods | int | 预测期数 | 默认6期 |
| confidence_interval | float | 置信区间水平 | 默认0.95（95%置信区间） |
| seasonality_period | int | 季节性周期 | 默认0（无季节性）；若数据存在季节性应使用SARIMA |
| auto_select | boolean | 是否自动选择最优参数 | 默认true，自动通过AIC网格搜索选择最优(p,d,q) |

## formula
ARIMA(p,d,q)模型：

ARIMA由三个部分组成：
1. AR(p) - 自回归部分：使用p个历史值预测当前值
   y_t = c + φ_1×y_{t-1} + φ_2×y_{t-2} + ... + φ_p×y_{t-p} + ε_t

2. I(d) - 差分整合部分：对原始序列进行d阶差分消除趋势
   y'_t = y_t - y_{t-1}（一阶差分）

3. MA(q) - 滑动平均部分：使用q个历史预测误差
   y_t = c + ε_t + θ_1×ε_{t-1} + θ_2×ε_{t-2} + ... + θ_q×ε_{t-q}

参数选择逻辑（AIC最小化）：
- 对p∈[0,5], d∈[0,2], q∈[0,5]进行网格搜索
- 计算每个组合的AIC = n×ln(RSS/n) + 2×(p+q+1)
- 选择AIC最小的参数组合

预测公式：
- 单步预测：y_{t+1} = c + φ_1×y_t + φ_2×y_{t-1} + ... + θ_1×ε_t + ...
- 多步预测：递归使用预测值作为输入

置信区间：
- 预测值 ± Z_{α/2} × SE
- SE随预测步数增加而扩大

计算步骤：
1. 对historical_demand进行平稳性检验（ADF检验）
2. 若数据不平稳，进行差分处理（确定d）
3. 通过ACF/PACF图或AIC网格搜索确定p和q
4. 拟合ARIMA(p,d,q)模型
5. 生成forecast_periods期预测值
6. 计算各期预测的置信区间

## output
| 字段名 | 类型 | 说明 |
|--------|------|------|
| forecast_values | array[float] | 预测需求值序列 |
| confidence_intervals | array[object] | 每期预测的置信区间上下界 |
| model_params | object | 使用的ARIMA参数(p,d,q) |
| model_aic | float | 模型AIC值 |
| model_fit_metrics | object | 拟合优度指标（RMSE, MAE, MAPE） |
| forecast_plot_data | array[object] | 预测图数据（历史+预测+置信区间） |

## example
**输入：**
```
historical_demand: [120, 135, 110, 145, 130, 150, 125, 140, 155, 128, 160, 148]
forecast_periods: 4
confidence_interval: 0.95
```

**计算过程：**
1. ADF检验：序列平稳性检验通过（d=0）
2. AIC网格搜索：最优参数 p=2, d=0, q=1 → ARIMA(2,0,1)
3. 拟合模型：y_t = 138.5 + 0.45×y_{t-1} + 0.22×y_{t-2} + 0.31×ε_{t-1}
4. 预测未来4期：
   - t+1: 152.3
   - t+2: 149.8
   - t+3: 153.5
   - t+4: 151.2

**输出：**
```
forecast_values: [152.3, 149.8, 153.5, 151.2]
confidence_intervals: [
  {"period": 1, "lower": 138.5, "upper": 166.1},
  {"period": 2, "lower": 131.4, "upper": 168.2},
  {"period": 3, "lower": 126.7, "upper": 180.3},
  {"period": 4, "lower": 119.8, "upper": 182.6}
]
model_params: {"p": 2, "d": 0, "q": 1}
model_aic: 85.32
model_fit_metrics: {"RMSE": 12.5, "MAE": 9.8, "MAPE": 7.2}
```