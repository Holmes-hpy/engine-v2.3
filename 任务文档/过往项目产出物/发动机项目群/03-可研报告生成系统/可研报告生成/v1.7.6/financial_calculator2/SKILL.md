---
name: financial_calculator2
description: 可研报告财务指标计算模块。提供FIRR、FNPV、投资回收期、盈亏平衡点、DSCR、ICR的纯Python计算函数。由Leader在渲染阶段调用，不直接参与文本生成。
---

# 可研报告财务指标计算模块

本SKILL包含企业投资项目可行性研究报告中6大核心财务指标的纯Python计算函数。

**调用方**：Leader Agent（步骤11渲染阶段）
**输入**：`财务计算输入数据.json`（由Writer-6输出）
**输出**：计算结果字典（JSON格式）

## 1. 数据接口规范

输入JSON文件 `财务计算输入数据.json` 的字段定义：

```json
{
  "initial_investment": 50000,
  "construction_period": 1,
  "cash_flows": [-50000, 8000, 12000, 18000, 25000, 30000],
  "discount_rate": 0.10,
  "fixed_costs": 5000,
  "variable_cost_ratio": 0.6,
  "revenue": 50000,
  "annual_principal": [5000, 5000, 5000, 5000, 5000],
  "annual_interest": [2250, 1800, 1350, 900, 450],
  "annual_ebit": [12000, 15000, 20000, 25000, 28000],
  "tax_rate": 0.25
}
```

字段说明：

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `initial_investment` | float | 是 | 初始总投资（万元），建设期第0年现金流出 |
| `construction_period` | int | 是 | 建设期（年），通常为1 |
| `cash_flows` | list[float] | 是 | 完整现金流序列（万元），第0年为负（投资），后续为正（净现金流） |
| `discount_rate` | float | 是 | 基准折现率，默认0.10（10%） |
| `fixed_costs` | float | 否 | 年固定成本（万元），用于盈亏平衡计算 |
| `variable_cost_ratio` | float | 否 | 变动成本率（0~1），用于盈亏平衡计算 |
| `revenue` | float | 否 | 年营业收入（万元），用于盈亏平衡计算 |
| `annual_principal` | list[float] | 否 | 各年还本金额（万元），用于DSCR计算 |
| `annual_interest` | list[float] | 否 | 各年付息金额（万元），用于DSCR和ICR计算 |
| `annual_ebit` | list[float] | 否 | 各年息税前利润（万元），用于ICR计算 |
| `tax_rate` | float | 否 | 所得税率，默认0.25（25%），用于税后FIRR计算 |

## 2. Python计算代码

```python
"""
可研报告财务指标计算模块
调用方式：python3 calc_financial.py 财务计算输入数据.json 计算结果.json
"""
import json
import sys


def calculate_npv(cash_flows, discount_rate):
    """
    计算净现值（NPV）
    NPV = sum(CF_t / (1 + r)^t for t in range(len(cash_flows)))
    """
    if not cash_flows or discount_rate is None:
        return None
    npv = 0.0
    for t, cf in enumerate(cash_flows):
        npv += cf / ((1 + discount_rate) ** t)
    return npv


def calculate_irr(cash_flows, initial_guess=0.1, max_iter=100, tol=1e-6):
    """
    计算内部收益率（IRR）
    使用牛顿迭代法求解 NPV(r) = 0
    
    参数:
        cash_flows: 现金流序列
        initial_guess: 初始猜测值（默认10%）
        max_iter: 最大迭代次数
        tol: 收敛容差
    
    返回:
        IRR值（小数），不收敛返回None
    """
    if not cash_flows:
        return None
    
    # 检查现金流是否有符号变化（IRR存在的前提）
    positives = sum(1 for cf in cash_flows if cf > 0)
    negatives = sum(1 for cf in cash_flows if cf < 0)
    if positives == 0 or negatives == 0:
        return None  # 无符号变化，IRR无意义
    
    def npv(rate):
        return sum(cf / ((1 + rate) ** t) for t, cf in enumerate(cash_flows))
    
    def npv_derivative(rate):
        """NPV对r的导数"""
        return sum(-t * cf / ((1 + rate) ** (t + 1)) for t, cf in enumerate(cash_flows) if t > 0)
    
    r = initial_guess
    for i in range(max_iter):
        npv_val = npv(r)
        if abs(npv_val) < tol:
            return r
        
        deriv = npv_derivative(r)
        if abs(deriv) < 1e-10:
            return None  # 导数接近0，牛顿法失效
        
        r_new = r - npv_val / deriv
        if r_new <= -1:
            r_new = -0.99  # 防止发散
        if abs(r_new - r) < tol:
            return r_new
        r = r_new
    
    return None  # 未收敛


def calculate_firr(cash_flows, tax_rate=0.25):
    """
    计算税前和税后财务内部收益率（FIRR）
    
    税前FIRR：基于税前现金流计算
    税后FIRR：税后现金流 = 税前现金流 * (1 - tax_rate)（简化处理，第0年投资不扣税）
    
    返回: {"pre_tax": float or None, "post_tax": float or None}
    """
    if not cash_flows:
        return {"pre_tax": None, "post_tax": None}
    
    # 税前FIRR
    pre_tax_irr = calculate_irr(cash_flows)
    
    # 税后现金流：第0年投资不扣税，运营期现金流扣税
    post_tax_cash_flows = []
    for t, cf in enumerate(cash_flows):
        if t == 0:
            post_tax_cash_flows.append(cf)  # 投资不扣税
        elif cf > 0:
            post_tax_cash_flows.append(cf * (1 - tax_rate))
        else:
            post_tax_cash_flows.append(cf)
    
    post_tax_irr = calculate_irr(post_tax_cash_flows)
    
    return {
        "pre_tax": pre_tax_irr,
        "post_tax": post_tax_irr
    }


def calculate_fnpv(cash_flows, discount_rate):
    """
    计算财务净现值（FNPV）
    """
    npv_val = calculate_npv(cash_flows, discount_rate)
    return npv_val


def calculate_payback_period(cash_flows):
    """
    计算静态投资回收期
    
    算法：累计净现金流量由负转正的年份
    如果累计现金流在最后一年仍为负，返回None
    """
    if not cash_flows:
        return None
    
    cumulative = 0.0
    for t, cf in enumerate(cash_flows):
        cumulative += cf
        if cumulative >= 0 and t > 0:  # t=0是投资，不算回收
            # 线性插值：假设当年内均匀回收
            prev_cumulative = cumulative - cf
            fraction = abs(prev_cumulative) / cf if cf > 0 else 0
            return t - 1 + fraction
    
    return None  # 未在预测期内收回


def calculate_discounted_payback(cash_flows, discount_rate):
    """
    计算动态投资回收期（基于折现现金流）
    """
    if not cash_flows or discount_rate is None:
        return None
    
    cumulative = 0.0
    for t, cf in enumerate(cash_flows):
        discounted_cf = cf / ((1 + discount_rate) ** t)
        cumulative += discounted_cf
        if cumulative >= 0 and t > 0:
            prev_cumulative = cumulative - discounted_cf
            fraction = abs(prev_cumulative) / discounted_cf if discounted_cf > 0 else 0
            return t - 1 + fraction
    
    return None


def calculate_bep(fixed_costs, variable_cost_ratio, revenue):
    """
    计算盈亏平衡点（BEP）
    
    BEP收入 = 固定成本 / (1 - 变动成本率)
    BEP产量率 = BEP收入 / 正常营业收入 * 100%
    
    返回: {"revenue": float, "quantity_rate": float}
    """
    if fixed_costs is None or variable_cost_ratio is None or revenue is None:
        return {"revenue": None, "quantity_rate": None}
    
    if variable_cost_ratio >= 1:
        return {"revenue": None, "quantity_rate": None}  # 变动成本率≥100%无意义
    
    bep_revenue = fixed_costs / (1 - variable_cost_ratio)
    bep_quantity_rate = (bep_revenue / revenue) * 100 if revenue > 0 else None
    
    return {
        "revenue": bep_revenue,
        "quantity_rate": bep_quantity_rate
    }


def calculate_dscr(annual_ebitda, annual_tax, annual_principal, annual_interest):
    """
    计算偿债备付率（DSCR）
    
    DSCR = (EBITDA - 所得税) / (当期还本 + 当期利息)
    
    简化处理：annual_ebitda传annual_ebit（因折旧摊销数据通常缺失，用EBIT近似）
    
    参数:
        annual_ebitda: 各年EBITDA列表（万元）
        annual_tax: 各年所得税列表（万元），如缺失传[0]*n
        annual_principal: 各年还本金额列表（万元）
        annual_interest: 各年付息金额列表（万元）
    
    返回: {"values": list[float], "min_value": float, "min_year": int}
    """
    if not annual_principal or not annual_interest:
        return {"values": [], "min_value": None, "min_year": None}
    
    n = min(len(annual_principal), len(annual_interest))
    if annual_ebitda is None:
        annual_ebitda = [0] * n
    if annual_tax is None:
        annual_tax = [0] * n
    
    dscr_values = []
    for i in range(n):
        ebitda = annual_ebitda[i] if i < len(annual_ebitda) else 0
        tax = annual_tax[i] if i < len(annual_tax) else 0
        principal = annual_principal[i]
        interest = annual_interest[i]
        
        denominator = principal + interest
        if denominator <= 0:
            dscr_values.append(None)
        else:
            dscr = (ebitda - tax) / denominator
            dscr_values.append(dscr)
    
    valid_values = [(v, i+1) for i, v in enumerate(dscr_values) if v is not None]
    if not valid_values:
        return {"values": dscr_values, "min_value": None, "min_year": None}
    
    min_val, min_year = min(valid_values, key=lambda x: x[0])
    return {
        "values": dscr_values,
        "min_value": min_val,
        "min_year": min_year
    }


def calculate_icr(annual_ebit, annual_interest):
    """
    计算利息备付率（ICR）
    
    ICR = EBIT / 当期应付利息
    
    参数:
        annual_ebit: 各年息税前利润列表（万元）
        annual_interest: 各年应付利息列表（万元）
    
    返回: {"values": list[float], "min_value": float, "min_year": int}
    """
    if not annual_ebit or not annual_interest:
        return {"values": [], "min_value": None, "min_year": None}
    
    n = min(len(annual_ebit), len(annual_interest))
    icr_values = []
    
    for i in range(n):
        ebit = annual_ebit[i]
        interest = annual_interest[i]
        
        if interest <= 0:
            icr_values.append(None)
        else:
            icr = ebit / interest
            icr_values.append(icr)
    
    valid_values = [(v, i+1) for i, v in enumerate(icr_values) if v is not None]
    if not valid_values:
        return {"values": icr_values, "min_value": None, "min_year": None}
    
    min_val, min_year = min(valid_values, key=lambda x: x[0])
    return {
        "values": icr_values,
        "min_value": min_val,
        "min_year": min_year
    }


def calculate_all(data):
    """
    执行全部财务指标计算
    
    参数:
        data: dict，解析后的JSON数据
    
    返回:
        dict，包含所有计算结果
    """
    results = {}
    
    # 必要参数检查
    cash_flows = data.get("cash_flows")
    discount_rate = data.get("discount_rate", 0.10)
    tax_rate = data.get("tax_rate", 0.25)
    
    if not cash_flows:
        results["error"] = "缺少必要参数: cash_flows"
        return results
    
    # 1. FIRR（税前/税后）
    firr_result = calculate_firr(cash_flows, tax_rate)
    results["FIRR"] = {
        "pre_tax_pct": round(firr_result["pre_tax"] * 100, 2) if firr_result["pre_tax"] else None,
        "post_tax_pct": round(firr_result["post_tax"] * 100, 2) if firr_result["post_tax"] else None,
        "pre_tax": firr_result["pre_tax"],
        "post_tax": firr_result["post_tax"]
    }
    
    # 2. FNPV
    fnpv_val = calculate_fnpv(cash_flows, discount_rate)
    results["FNPV"] = {
        "value": round(fnpv_val, 2) if fnpv_val is not None else None,
        "discount_rate": discount_rate
    }
    
    # 3. 静态回收期
    payback = calculate_payback_period(cash_flows)
    results["payback_static"] = round(payback, 2) if payback is not None else None
    
    # 4. 动态回收期
    payback_dyn = calculate_discounted_payback(cash_flows, discount_rate)
    results["payback_dynamic"] = round(payback_dyn, 2) if payback_dyn is not None else None
    
    # 5. 盈亏平衡点
    fixed_costs = data.get("fixed_costs")
    variable_cost_ratio = data.get("variable_cost_ratio")
    revenue = data.get("revenue")
    bep_result = calculate_bep(fixed_costs, variable_cost_ratio, revenue)
    results["BEP"] = {
        "revenue": round(bep_result["revenue"], 2) if bep_result["revenue"] else None,
        "quantity_rate_pct": round(bep_result["quantity_rate"], 2) if bep_result["quantity_rate"] else None
    }
    
    # 6. DSCR
    annual_principal = data.get("annual_principal")
    annual_interest = data.get("annual_interest")
    annual_ebit = data.get("annual_ebit")
    if annual_principal and annual_interest:
        # EBITDA近似：EBIT（因折旧摊销数据通常缺失）
        dscr_result = calculate_dscr(annual_ebit, None, annual_principal, annual_interest)
        results["DSCR"] = {
            "values": [round(v, 2) if v else None for v in dscr_result["values"]],
            "min_value": round(dscr_result["min_value"], 2) if dscr_result["min_value"] else None,
            "min_year": dscr_result["min_year"]
        }
    else:
        results["DSCR"] = {"values": [], "min_value": None, "min_year": None}
    
    # 7. ICR
    if annual_ebit and annual_interest:
        icr_result = calculate_icr(annual_ebit, annual_interest)
        results["ICR"] = {
            "values": [round(v, 2) if v else None for v in icr_result["values"]],
            "min_value": round(icr_result["min_value"], 2) if icr_result["min_value"] else None,
            "min_year": icr_result["min_year"]
        }
    else:
        results["ICR"] = {"values": [], "min_value": None, "min_year": None}
    
    return results


def main():
    if len(sys.argv) < 3:
        print("用法: python3 calc_financial.py 输入.json 输出.json")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    results = calculate_all(data)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"计算完成，结果已保存至: {output_file}")


if __name__ == "__main__":
    main()
```

## 3. 调用方式

### 命令行调用

```bash
python3 calc_financial.py 财务计算输入数据.json 计算结果.json
```

### Python模块调用

```python
import json
from calc_financial import calculate_all

with open('财务计算输入数据.json', 'r') as f:
    data = json.load(f)

results = calculate_all(data)
print(results)
```

## 4. 输出格式

`计算结果.json` 的格式：

```json
{
  "FIRR": {
    "pre_tax_pct": 18.52,
    "post_tax_pct": 14.31,
    "pre_tax": 0.1852,
    "post_tax": 0.1431
  },
  "FNPV": {
    "value": 12583.45,
    "discount_rate": 0.10
  },
  "payback_static": 3.42,
  "payback_dynamic": 4.15,
  "BEP": {
    "revenue": 12500.00,
    "quantity_rate_pct": 25.00
  },
  "DSCR": {
    "values": [2.35, 2.78, 3.42, 4.15, 4.88],
    "min_value": 2.35,
    "min_year": 1
  },
  "ICR": {
    "values": [5.33, 8.33, 14.81, 27.78, 62.22],
    "min_value": 5.33,
    "min_year": 1
  }
}
```

## 5. 异常处理说明

| 场景 | 处理方式 | 输出结果 |
|------|---------|---------|
| 现金流无符号变化（全正或全负） | IRR无意义，返回None | `FIRR.pre_tax: null` |
| IRR迭代不收敛 | 返回None | `FIRR.pre_tax: null` |
| 缺少必要参数（cash_flows） | 返回错误信息 | `error: "缺少必要参数: cash_flows"` |
| 变动成本率≥100% | BEP无意义，返回None | `BEP.revenue: null` |
| 预测期内未收回投资 | 回收期返回None | `payback_static: null` |
| 缺少DSCR/ICR数据 | 返回空数组+null | `DSCR.values: []` |
