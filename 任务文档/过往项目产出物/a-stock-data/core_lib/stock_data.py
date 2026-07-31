"""
A股数据核心功能模块
从 a-stock-data SKILL.md 自动生成

作者：Simon 林 · 抖音「Simon林」· 公众号「硅基世纪」
版本：V3.0 (2026-05-17)
"""

import requests
import pandas as pd
import re
import time
import secrets
import json
import os
import ssl
from pathlib import Path
from datetime import datetime, timedelta
from mootdx.quotes import Quotes
import urllib.request

# 禁用SSL验证（用于macOS等环境）
try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

# 创建全局requests会话（禁用代理，避免代理问题）
session = requests.Session()
session.trust_env = False  # 不使用环境变量中的代理设置
session.headers.update({
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Referer": "https://quote.eastmoney.com/",
})

# ==================== 全局常量 ====================

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
DATACENTER_URL = "https://datacenter-web.eastmoney.com/api/data/v1/get"
REPORT_API = "https://reportapi.eastmoney.com/report/list"
PDF_TPL = "https://pdf.dfcfw.com/pdf/H3_{info_code}_1.pdf"
THS_HOT_URL = "http://zx.10jqka.com.cn/event/api/getharden/"
HSGT_URL = "https://data.hexin.cn/market/hsgtApi/method/dayChart/"
BAIDU_PAE_URL = "https://finance.pae.baidu.com/api/getrelatedblock"
BAIDU_KLINE_URL = "https://finance.pae.baidu.com/selfselect/getstockquotation"
EASTMONEY_PUSH2_URL = "https://push2.eastmoney.com/api/qt/stock/fflow/kline/get"
EASTMONEY_NEWS_URL = "https://search-api-web.eastmoney.com/search/jsonp"
CLS_URL = "https://www.cls.cn/api/sw?app=CLS&sv=7.7.5"
EASTMONEY_GLOBAL_URL = "https://np-weblist.eastmoney.com/np"
SINA_FINANCE_URL = "https://quotes.sina.cn/cn/api/json_v2.php"
CNINFO_URL = "https://www.cninfo.com.cn/new/hisAnnouncement/query"
MOOTDX_CACHE_DIR = Path.home() / ".tradingagents" / "cache"

# iwencai 配置
IWENCAI_BASE = os.environ.get("IWENCAI_BASE_URL", "https://openapi.iwencai.com")
IWENCAI_KEY = os.environ.get("IWENCAI_API_KEY", "")

# ==================== 工具函数 ====================

def get_prefix(code: str) -> str:
    """6位代码 → 市场前缀"""
    if code.startswith(("6", "9")):
        return "sh"
    elif code.startswith("8"):
        return "bj"
    else:
        return "sz"

def normalize_code(code: str) -> str:
    """统一转为6位纯数字"""
    return re.sub(r'[^0-9]', '', code)

def _claw_headers(call_type: str = "normal") -> dict:
    """SkillHub 2.0 必须的 X-Claw 鉴权头"""
    return {
        "X-Claw-Call-Type": call_type,
        "X-Claw-Skill-Id": "report-search",
        "X-Claw-Skill-Version": "2.0.0",
        "X-Claw-Plugin-Id": "none",
        "X-Claw-Plugin-Version": "none",
        "X-Claw-Trace-Id": secrets.token_hex(32),
    }

# ==================== Layer 1: 行情层 ====================

def get_stock_quote(stock_code: str) -> dict:
    """获取股票实时行情（多API源容错机制）"""
    code = normalize_code(stock_code)
    
    if code.startswith(("6", "9")):
        prefixed = f"sh{code}"
        secid = f"1.{code}"
    elif code.startswith("8"):
        prefixed = f"bj{code}"
        secid = f"0.{code}"
    else:
        prefixed = f"sz{code}"
        secid = f"0.{code}"
    
    def safe_float(val):
        try:
            return float(val) if val and val not in ["-", "", "0", "0.00"] else 0.0
        except:
            return 0.0
    
    # 方案1：腾讯财经API（稳定性最好）
    try:
        import ssl
        context = ssl._create_unverified_context()
        url = f"https://qt.gtimg.cn/q={prefixed}"
        req = urllib.request.Request(url)
        req.add_header("User-Agent", UA)
        
        resp = urllib.request.urlopen(req, timeout=10, context=context)
        data = resp.read().decode("gbk")
        
        for line in data.strip().split(";"):
            if not line.strip() or "=" not in line or '"' not in line:
                continue
            vals = line.split('"')[1].split("~")
            if len(vals) < 35:
                continue
            
            result = {
                code: {
                    "name": vals[1],
                    "price": safe_float(vals[3]),
                    "last_close": safe_float(vals[4]),
                    "open": safe_float(vals[5]),
                    "change_amt": safe_float(vals[31]),
                    "change_pct": safe_float(vals[32]),
                    "high": safe_float(vals[33]),
                    "low": safe_float(vals[34]),
                    "amount_wan": safe_float(vals[37]),
                    "turnover_pct": safe_float(vals[38]),
                    "pe_ttm": safe_float(vals[39]),
                    "amplitude_pct": safe_float(vals[43]),
                    "mcap_yi": safe_float(vals[44]),
                    "float_mcap_yi": safe_float(vals[45]),
                    "pb": safe_float(vals[46]),
                    "limit_up": safe_float(vals[47]),
                    "limit_down": safe_float(vals[48]),
                    "vol_ratio": safe_float(vals[49]),
                    "pe_static": safe_float(vals[52]),
                    "volume": safe_float(vals[37]) * 10000,
                }
            }
            
            # 如果当前价格为0（非交易时段），使用昨收价
            if result[code]["price"] == 0 and result[code]["last_close"] > 0:
                result[code]["price"] = result[code]["last_close"]
            
            return result
    except Exception as e:
        pass
    
    # 方案2：新浪财经API（腾讯失败时的备用）
    try:
        url = f"https://hq.sinajs.cn/list={prefixed}"
        resp = session.get(url, timeout=10)
        resp.encoding = "gbk"
        data = resp.text
        
        if "hq_str_" in data:
            parts = data.split('"')[1].split(',')
            if len(parts) >= 10:
                result = {
                    code: {
                        "name": parts[0],
                        "price": safe_float(parts[3]) if safe_float(parts[3]) > 0 else safe_float(parts[2]),
                        "last_close": safe_float(parts[2]),
                        "open": safe_float(parts[1]),
                        "change_amt": 0,
                        "change_pct": 0,
                        "high": safe_float(parts[4]),
                        "low": safe_float(parts[5]),
                        "amount_wan": safe_float(parts[9]) / 10000,
                        "turnover_pct": 0,
                        "pe_ttm": 0,
                        "amplitude_pct": 0,
                        "mcap_yi": 0,
                        "float_mcap_yi": 0,
                        "pb": 0,
                        "limit_up": 0,
                        "limit_down": 0,
                        "vol_ratio": 0,
                        "pe_static": 0,
                        "volume": safe_float(parts[8]),
                    }
                }
                return result
    except Exception as e:
        pass
    
    # 方案3：东方财富批量查询API（最后的备用）
    try:
        url = "https://push2.eastmoney.com/api/qt/ulist.np/get"
        params = {
            "fltt": "2",
            "invt": "2",
            "fields": "f2,f3,f4,f5,f6,f7,f8,f9,f10,f12,f13,f14,f15,f16,f17,f18,f20,f21,f23",
            "secids": secid,
        }
        
        resp = session.get(url, params=params, timeout=10)
        data = resp.json()
        
        if data.get("rc") == 0 and data.get("data") and data["data"].get("diff"):
            diff_list = data["data"]["diff"]
            
            if len(diff_list) > 0:
                d = diff_list[0]
                
                result = {
                    code: {
                        "name": d.get("f14", ""),
                        "price": safe_float(d.get("f2")) if safe_float(d.get("f2")) > 0 else safe_float(d.get("f18")),
                        "last_close": safe_float(d.get("f18")),
                        "open": safe_float(d.get("f17")),
                        "change_amt": safe_float(d.get("f4")),
                        "change_pct": safe_float(d.get("f3")),
                        "high": safe_float(d.get("f15")),
                        "low": safe_float(d.get("f16")),
                        "amount_wan": safe_float(d.get("f6")) / 10000,
                        "turnover_pct": safe_float(d.get("f8")),
                        "pe_ttm": safe_float(d.get("f9")),
                        "amplitude_pct": safe_float(d.get("f7")),
                        "mcap_yi": safe_float(d.get("f20")) / 100000000,
                        "float_mcap_yi": safe_float(d.get("f21")) / 100000000,
                        "pb": safe_float(d.get("f23")),
                        "limit_up": 0.0,
                        "limit_down": 0.0,
                        "vol_ratio": safe_float(d.get("f10")),
                        "pe_static": safe_float(d.get("f9")),
                        "volume": safe_float(d.get("f5")),
                    }
                }
                return result
    except Exception as e:
        pass
    
    # 全部失败
    return {}

def get_historical_k_data(stock_code: str, period: str = "daily", days: int = 30) -> pd.DataFrame:
    """获取股票历史K线数据（mootdx）"""
    client = Quotes.factory(market='std')
    code = normalize_code(stock_code)

    category_map = {"daily": 4, "weekly": 5, "monthly": 6}
    category = category_map.get(period, 4)

    klines = client.bars(symbol=code, category=category, offset=days)
    return klines

def baidu_kline_with_ma(code: str, start_time: str = "") -> dict:
    """百度股市通K线（带MA5/MA10/MA20）"""
    url = BAIDU_KLINE_URL
    params = {
        "all": "1", "isIndex": "false", "isBk": "false", "isBlock": "false",
        "isFutures": "false", "isStock": "true", "newFormat": "1",
        "group": "quotation_kline_ab", "finClientType": "pc",
        "code": code, "start_time": start_time, "ktype": "1",
    }
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/vnd.finance-web.v1+json",
        "Origin": "https://gushitong.baidu.com",
        "Referer": "https://gushitong.baidu.com/",
    }
    r = requests.get(url, params=params, headers=headers, timeout=10)
    d = r.json()
    result = d.get("Result", {})
    md = result.get("newMarketData", {})
    keys = md.get("keys", [])
    rows = md.get("marketData", "").split(";")
    return {"keys": keys, "rows": rows}

def get_market_index() -> dict:
    """获取大盘指数实时数据（上证指数、深证成指、创业板指、科创50）"""
    index_list = [
        ("shanghai", "1.000001", "上证指数"),
        ("shenzhen", "0.399001", "深证成指"),
        ("chuangye", "0.399006", "创业板指"),
        ("kechuang", "1.000688", "科创50"),
    ]
    
    result = {}
    secids = ",".join([item[1] for item in index_list])
    
    url = "https://push2.eastmoney.com/api/qt/ulist.np/get"
    params = {
        "fltt": "2",
        "invt": "2",
        "fields": "f2,f3,f4,f5,f6,f7,f12,f13,f14,f15,f16,f17,f18",
        "secids": secids,
        "ut": "fa5fd1943c7b386f172d6893dbfba10b",
    }
    
    max_retries = 3
    for attempt in range(max_retries):
        try:
            resp = session.get(url, params=params, timeout=10)
            data = resp.json()
            
            if data.get("rc") == 0 and data.get("data") and data["data"].get("diff"):
                diff_list = data["data"]["diff"]
                
                # 建立secid到数据的映射
                data_map = {}
                for item in diff_list:
                    market = item.get("f13", "")
                    code = item.get("f12", "")
                    secid = f"{market}.{code}"
                    data_map[secid] = item
                
                # 填充结果
                for key, secid, name in index_list:
                    if secid in data_map:
                        d = data_map[secid]
                        def safe_float(val):
                            try:
                                return float(val) if val and val != "-" else 0.0
                            except:
                                return 0.0
                        
                        result[key] = {
                            "name": d.get("f14", name),
                            "price": safe_float(d.get("f2")),
                            "change_pct": safe_float(d.get("f3")),
                            "change_amt": safe_float(d.get("f4")),
                            "high": safe_float(d.get("f15")),
                            "low": safe_float(d.get("f16")),
                            "open": safe_float(d.get("f17")),
                            "last_close": safe_float(d.get("f18")),
                            "amplitude": safe_float(d.get("f7")),
                        }
                    else:
                        result[key] = {"name": name, "price": 0, "change_pct": 0}
                
                return result
            else:
                if attempt < max_retries - 1:
                    time.sleep(1)
                    continue
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(1)
                continue
            print(f"[get_market_index] 获取指数失败（重试{max_retries}次）: {e}")
    
    # 全部失败时返回默认值
    for key, secid, name in index_list:
        if key not in result:
            result[key] = {"name": name, "price": 0, "change_pct": 0}
    
    return result

# ==================== Layer 2: 研报层 ====================

def get_research_reports(stock_code: str, days: int = 90) -> list:
    """获取股票研报列表"""
    code = normalize_code(stock_code)
    session = requests.Session()
    session.headers.update({"User-Agent": UA, "Referer": "https://data.eastmoney.com/"})

    all_records = []
    max_pages = min(5, days // 20 + 1)

    for page in range(1, max_pages + 1):
        params = {
            "industryCode": "*", "pageSize": "100", "industry": "*",
            "rating": "*", "ratingChange": "*",
            "beginTime": "2000-01-01", "endTime": "2030-01-01",
            "pageNo": str(page), "fields": "", "qType": "0",
            "orgCode": "", "code": code, "rcode": "",
            "p": str(page), "pageNum": str(page), "pageNumber": str(page),
        }
        r = session.get(REPORT_API, params=params, timeout=30)
        d = r.json()
        rows = d.get("data") or []
        if not rows:
            break
        all_records.extend(rows)
        if page >= (d.get("TotalPage", 1) or 1):
            break
        time.sleep(0.3)

    return all_records

def ths_eps_forecast(code: str) -> pd.DataFrame:
    """同花顺机构一致预期EPS"""
    url = f"http://basic.10jqka.com.cn/{code}/profit.html"
    headers = {"User-Agent": UA, "Referer": "https://data.10jqka.com.cn/"}
    r = requests.get(url, headers=headers, timeout=15)
    dfs = pd.read_html(r.text)
    for df in dfs:
        if "预测指标" in df.columns or "预测年度" in df.columns:
            return df
    return pd.DataFrame()

def iwencai_search(query: str, channel: str = "report", size: int = 50) -> list:
    """iwencai 语义搜索"""
    headers = {
        "Authorization": f"Bearer {IWENCAI_KEY}",
        "Content-Type": "application/json",
        **_claw_headers(),
    }
    payload = {
        "channels": [channel],
        "app_id": "AIME_SKILL",
        "query": query,
        "size": size,
    }
    r = requests.post(
        f"{IWENCAI_BASE}/v1/comprehensive/search",
        json=payload, headers=headers, timeout=30,
    )
    if r.status_code != 200:
        raise RuntimeError(f"iwencai HTTP {r.status_code}: {r.text[:200]}")
    data = r.json()
    if data.get("status_code", 0) != 0:
        raise RuntimeError(f"iwencai error: {data.get('status_msg', '')}")
    return data.get("data") or []

def iwencai_query(query: str, page: int = 1, limit: int = 50) -> list:
    """iwencai NL数据查询"""
    headers = {
        "Authorization": f"Bearer {IWENCAI_KEY}",
        "Content-Type": "application/json",
        **_claw_headers(),
    }
    payload = {
        "query": query,
        "page": str(page),
        "limit": str(limit),
        "is_cache": "1",
        "expand_index": "true",
    }
    r = requests.post(
        f"{IWENCAI_BASE}/v1/query2data",
        json=payload, headers=headers, timeout=30,
    )
    if r.status_code != 200:
        raise RuntimeError(f"iwencai HTTP {r.status_code}: {r.text[:200]}")
    data = r.json()
    if data.get("status_code", 0) != 0:
        raise RuntimeError(f"iwencai error: {data.get('status_msg', '')}")
    return data.get("datas") or []

# ==================== Layer 3: 信号层 ====================

def ths_hot_reason(date: str = None) -> pd.DataFrame:
    """同花顺当日强势股归因"""
    from datetime import date as _date
    if date is None:
        date = _date.today().strftime("%Y-%m-%d")

    url = f"{THS_HOT_URL}date/{date}/orderby/date/orderway/desc/charset/GBK/"
    headers = {"User-Agent": UA}
    r = requests.get(url, headers=headers, timeout=10)
    data = r.json()
    if data.get("errocode", 0) != 0:
        raise RuntimeError(f"同花顺热点错误: {data.get('errormsg', '')}")

    rows = data.get("data") or []
    df = pd.DataFrame(rows)
    if df.empty:
        return df

    rename_map = {
        "name": "名称", "code": "代码", "reason": "题材归因",
        "close": "收盘价", "zhangdie": "涨跌额", "zhangfu": "涨幅%",
        "huanshou": "换手率%", "chengjiaoe": "成交额",
        "chengjiaoliang": "成交量", "ddejingliang": "大单净量",
        "market": "市场",
    }
    df = df.rename(columns=rename_map)
    return df

def hsgt_realtime() -> pd.DataFrame:
    """沪深股通当日实时分钟流向"""
    url = HSGT_URL
    r = requests.get(url, headers={"User-Agent": UA, "Host": "data.hexin.cn", "Referer": "https://data.hexin.cn/"}, timeout=10)
    d = r.json()
    times = d.get("time", [])
    hgt = d.get("hgt", [])
    sgt = d.get("sgt", [])

    n = len(times)
    return pd.DataFrame({
        "time": times,
        "hgt_yi": hgt[:n] + [None] * (n - len(hgt)),
        "sgt_yi": sgt[:n] + [None] * (n - len(sgt)),
    })

def get_northbound_flow() -> dict:
    """获取北向资金流入流出数据"""
    df = hsgt_realtime()
    if df.empty:
        return {"hgt": 0, "sgt": 0, "total": 0}

    last_valid = df.dropna().iloc[-1] if not df.dropna().empty else None
    if last_valid is not None:
        return {
            "hgt": float(last_valid["hgt_yi"]),
            "sgt": float(last_valid["sgt_yi"]),
            "total": float(last_valid["hgt_yi"]) + float(last_valid["sgt_yi"])
        }
    return {"hgt": 0, "sgt": 0, "total": 0}

def baidu_concept_blocks(code: str) -> dict:
    """百度股市通概念板块归属"""
    url = f"{BAIDU_PAE_URL}?code={code}&market=ab&typeCode=all&finClientType=pc"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/117.0.0.0",
        "Accept": "application/vnd.finance-web.v1+json",
        "Origin": "https://gushitong.baidu.com",
        "Referer": "https://gushitong.baidu.com/",
    }
    r = requests.get(url, headers=headers, timeout=10)
    d = r.json()
    if str(d.get("ResultCode", -1)) != "0":
        raise RuntimeError(f"百度PAE错误: {d}")

    result = {"industry": [], "concept": [], "region": [], "concept_tags": []}
    for block in d.get("Result", []):
        block_type = block.get("type", "")
        for item in block.get("list", []):
            entry = {
                "name": item.get("name", ""),
                "change_pct": item.get("increase", ""),
                "desc": item.get("desc", ""),
            }
            if "行业" in block_type:
                result["industry"].append(entry)
            elif "概念" in block_type:
                result["concept"].append(entry)
                result["concept_tags"].append(entry["name"])
            elif "地域" in block_type:
                result["region"].append(entry)
    return result

def eastmoney_fund_flow_minute(code: str) -> list:
    """个股资金流向（分钟级）"""
    secid = f"1.{code}" if code.startswith("6") else f"0.{code}"
    url = EASTMONEY_PUSH2_URL
    params = {
        "secid": secid, "klt": 1,
        "fields1": "f1,f2,f3,f7",
        "fields2": "f51,f52,f53,f54,f55,f56,f57",
    }
    r = requests.get(url, params=params, timeout=10)
    d = r.json()

    rows = []
    for line in d.get("data", {}).get("klines", []):
        parts = line.split(",")
        if len(parts) >= 6:
            rows.append({
                "time": parts[0],
                "main_net": float(parts[1]),
                "small_net": float(parts[2]),
                "mid_net": float(parts[3]),
                "large_net": float(parts[4]),
                "super_net": float(parts[5]),
            })
    return rows

def eastmoney_datacenter(report_name: str, columns: str = "ALL",
                         filter_str: str = "", page_size: int = 50,
                         sort_columns: str = "", sort_types: str = "-1") -> list:
    """东财数据中心统一查询"""
    params = {
        "reportName": report_name, "columns": columns,
        "filter": filter_str, "pageNumber": "1", "pageSize": str(page_size),
        "sortColumns": sort_columns, "sortTypes": sort_types,
        "source": "WEB", "client": "WEB",
    }
    r = requests.get(DATACENTER_URL, params=params, headers={"User-Agent": UA}, timeout=15)
    d = r.json()
    if d.get("result") and d["result"].get("data"):
        return d["result"]["data"]
    return []

def dragon_tiger_board(code: str, trade_date: str, look_back: int = 30) -> dict:
    """龙虎榜数据聚合"""
    start = datetime.strptime(trade_date, "%Y-%m-%d") - timedelta(days=look_back)
    start_str = start.strftime("%Y-%m-%d")

    records = []
    data = eastmoney_datacenter(
        "RPT_DAILYBILLBOARD_DETAILSNEW",
        filter_str=f"(TRADE_DATE>='{start_str}')(TRADE_DATE<='{trade_date}')(SECURITY_CODE=\"{code}\")",
        page_size=50,
        sort_columns="TRADE_DATE", sort_types="-1",
    )
    for row in data:
        records.append({
            "date": str(row.get("TRADE_DATE", ""))[:10],
            "reason": row.get("EXPLANATION", ""),
            "net_buy": round((row.get("BILLBOARD_NET_AMT") or 0) / 10000, 1),
            "turnover": round(float(row.get("TURNOVERRATE") or 0), 2),
        })

    seats = {"buy": [], "sell": []}
    if records:
        latest_date = records[0]["date"]
        buy_data = eastmoney_datacenter(
            "RPT_BILLBOARD_DAILYDETAILSBUY",
            filter_str=f"(TRADE_DATE='{latest_date}')(SECURITY_CODE=\"{code}\")",
            page_size=10, sort_columns="BUY", sort_types="-1",
        )
        for row in buy_data[:5]:
            seats["buy"].append({
                "name": row.get("OPERATEDEPT_NAME", ""),
                "buy_amt": round((row.get("BUY") or 0) / 10000, 1),
                "sell_amt": round((row.get("SELL") or 0) / 10000, 1),
                "net": round((row.get("NET") or 0) / 10000, 1),
            })
        sell_data = eastmoney_datacenter(
            "RPT_BILLBOARD_DAILYDETAILSSELL",
            filter_str=f"(TRADE_DATE='{latest_date}')(SECURITY_CODE=\"{code}\")",
            page_size=10, sort_columns="SELL", sort_types="-1",
        )
        for row in sell_data[:5]:
            seats["sell"].append({
                "name": row.get("OPERATEDEPT_NAME", ""),
                "buy_amt": round((row.get("BUY") or 0) / 10000, 1),
                "sell_amt": round((row.get("SELL") or 0) / 10000, 1),
                "net": round((row.get("NET") or 0) / 10000, 1),
            })

    institution = {"buy_amt": 0, "sell_amt": 0, "net_amt": 0}
    for detail_data, side in [(buy_data, "buy"), (sell_data, "sell")]:
        for row in detail_data:
            if str(row.get("OPERATEDEPT_CODE", "")) == "0":
                amt = (row.get("BUY") or 0) if side == "buy" else (row.get("SELL") or 0)
                if side == "buy":
                    institution["buy_amt"] += amt
                else:
                    institution["sell_amt"] += amt
    institution["buy_amt"] = round(institution["buy_amt"] / 10000, 1)
    institution["sell_amt"] = round(institution["sell_amt"] / 10000, 1)
    institution["net_amt"] = round(institution["buy_amt"] - institution["sell_amt"], 1)

    return {"records": records, "seats": seats, "institution": institution}

def get_dragon_tiger_board(date: str = None) -> dict:
    """获取龙虎榜数据（默认今日）"""
    if date is None:
        date = datetime.now().strftime("%Y-%m-%d")
    data = eastmoney_datacenter(
        "RPT_DAILYBILLBOARD_DETAILSNEW",
        filter_str=f"(TRADE_DATE='{date}')",
        page_size=100,
        sort_columns="BILLBOARD_NET_AMT", sort_types="-1",
    )
    return {"date": date, "records": data}

def lockup_expiry(code: str, trade_date: str, forward_days: int = 90) -> dict:
    """限售解禁日历"""
    history_data = eastmoney_datacenter(
        "RPT_LIFT_STAGE",
        filter_str=f"(SECURITY_CODE=\"{code}\")",
        page_size=15,
        sort_columns="FREE_DATE", sort_types="-1",
    )
    history = []
    for row in history_data:
        history.append({
            "date": str(row.get("FREE_DATE", ""))[:10],
            "type": row.get("LIMITED_STOCK_TYPE", ""),
            "shares": row.get("FREE_SHARES_NUM", 0),
            "ratio": row.get("FREE_RATIO", 0),
        })

    end_date = datetime.strptime(trade_date, "%Y-%m-%d") + timedelta(days=forward_days)
    end_str = end_date.strftime("%Y-%m-%d")
    upcoming_data = eastmoney_datacenter(
        "RPT_LIFT_STAGE",
        filter_str=f"(SECURITY_CODE=\"{code}\")(FREE_DATE>='{trade_date}')(FREE_DATE<='{end_str}')",
        page_size=20,
        sort_columns="FREE_DATE", sort_types="1",
    )
    upcoming = []
    for row in upcoming_data:
        upcoming.append({
            "date": str(row.get("FREE_DATE", ""))[:10],
            "type": row.get("LIMITED_STOCK_TYPE", ""),
            "shares": row.get("FREE_SHARES_NUM", 0),
            "ratio": row.get("FREE_RATIO", 0),
        })

    return {"history": history, "upcoming": upcoming}

def get_lockup_expiry(stock_code: str, months: int = 3) -> dict:
    """获取限售解禁信息"""
    code = normalize_code(stock_code)
    trade_date = datetime.now().strftime("%Y-%m-%d")
    forward_days = months * 30
    return lockup_expiry(code, trade_date, forward_days)

def industry_comparison(top_n: int = 20) -> dict:
    """全行业涨跌幅排名（东财）"""
    url = "https://push2.eastmoney.com/api/qt/clist/get"
    params = {
        "pn": "1", "pz": "100", "po": "1", "np": "1",
        "fltt": "2", "invt": "2",
        "fs": "m:90+t:2",
        "fields": "f2,f3,f4,f12,f13,f14,f104,f105,f128,f136,f140,f141,f207",
    }
    headers = {"User-Agent": UA}
    r = requests.get(url, params=params, headers=headers, timeout=15)
    d = r.json()
    items = d.get("data", {}).get("diff", [])
    if not items:
        return {"top": [], "bottom": [], "total": 0}

    rows = []
    for i, item in enumerate(items):
        rows.append({
            "rank": i + 1,
            "name": item.get("f14", ""),
            "change_pct": item.get("f3", 0),
            "code": item.get("f12", ""),
            "up_count": item.get("f104", 0),
            "down_count": item.get("f105", 0),
            "leader": item.get("f140", ""),
            "leader_change": item.get("f136", 0),
        })

    return {
        "top": rows[:top_n],
        "bottom": rows[-top_n:],
        "total": len(rows),
    }

# ==================== Layer 4: 资金面层 ====================

def margin_trading_detail(code: str, trade_date: str, days: int = 30) -> pd.DataFrame:
    """融资融券明细"""
    start = datetime.strptime(trade_date, "%Y-%m-%d") - timedelta(days=days)
    start_str = start.strftime("%Y-%m-%d")
    data = eastmoney_datacenter(
        "RPT_RZRQ_DETAIL",
        filter_str=f"(INTERVAL_TYPE='日期')(TRADE_DATE>='{start_str}')(TRADE_DATE<='{trade_date}')(SECURITY_CODE=\"{code}\")",
        page_size=days,
        sort_columns="TRADE_DATE", sort_types="-1",
    )
    if not data:
        return pd.DataFrame()
    df = pd.DataFrame(data)
    df["TRADE_DATE"] = pd.to_datetime(df["TRADE_DATE"]).dt.date
    return df

def block_trade(code: str, trade_date: str, days: int = 90) -> pd.DataFrame:
    """大宗交易"""
    start = datetime.strptime(trade_date, "%Y-%m-%d") - timedelta(days=days)
    start_str = start.strftime("%Y-%m-%d")
    data = eastmoney_datacenter(
        "RPT_BIGDEAL_DETAIL",
        filter_str=f"(TRADE_DATE>='{start_str}')(TRADE_DATE<='{trade_date}')(SECURITY_CODE=\"{code}\")",
        page_size=days,
        sort_columns="TRADE_DATE", sort_types="-1",
    )
    if not data:
        return pd.DataFrame()
    df = pd.DataFrame(data)
    df["TRADE_DATE"] = pd.to_datetime(df["TRADE_DATE"]).dt.date
    return df

def shareholder_count(code: str) -> pd.DataFrame:
    """股东户数变化"""
    data = eastmoney_datacenter(
        "RPT_SHAREHOLDERNUM_ALL",
        filter_str=f"(SECURITY_CODE=\"{code}\")",
        page_size=20,
        sort_columns="END_DATE", sort_types="-1",
    )
    if not data:
        return pd.DataFrame()
    df = pd.DataFrame(data)
    if "END_DATE" in df.columns:
        df["END_DATE"] = pd.to_datetime(df["END_DATE"]).dt.date
    return df

def dividend_history(code: str) -> pd.DataFrame:
    """分红送转历史"""
    data = eastmoney_datacenter(
        "RPT_DIVIDEND_DETAIL",
        filter_str=f"(SECURITY_CODE=\"{code}\")",
        page_size=20,
        sort_columns="REPORT_DATE", sort_types="-1",
    )
    if not data:
        return pd.DataFrame()
    df = pd.DataFrame(data)
    return df

def stock_fund_flow_120d(code: str) -> pd.DataFrame:
    """个股资金流120日（主力/大单/中单/小单）"""
    secid = f"1.{code}" if code.startswith("6") else f"0.{code}"
    url = EASTMONEY_PUSH2_URL
    params = {
        "secid": secid, "klt": 101, "fqt": 1,
        "fields1": "f1,f2,f3,f7",
        "fields2": "f51,f52,f53,f54,f55,f56,f57",
        "lmt": 120,
    }
    r = requests.get(url, params=params, timeout=15)
    d = r.json()

    rows = []
    for line in d.get("data", {}).get("klines", []):
        parts = line.split(",")
        if len(parts) >= 6:
            rows.append({
                "date": parts[0],
                "main_net": float(parts[1]),
                "small_net": float(parts[2]),
                "mid_net": float(parts[3]),
                "large_net": float(parts[4]),
                "super_net": float(parts[5]),
            })
    return pd.DataFrame(rows)

# ==================== Layer 5: 新闻层 ====================

def get_stock_news(code: str, days: int = 30) -> list:
    """获取个股新闻（东方财富）"""
    url = "https://search-api-web.eastmoney.com/search/jsonp"
    params = {
        "param": json.dumps({
            "uid": "",
            "keyword": code,
            "type": ["cmsArticle"],
            "pageindex": 0,
            "pagesize": 50,
            "time": str(days)
        })
    }
    
    max_retries = 3
    for attempt in range(max_retries):
        try:
            resp = session.get(url, params=params, timeout=15)
            d = resp.json()
            
            if d and d.get("result"):
                articles = d["result"].get("cmsArticles", []) or []
                return [
                    {
                        "title": a.get("title", ""),
                        "publish_time": a.get("publish_time", ""),
                        "source": a.get("source", ""),
                        "url": a.get("url", ""),
                    }
                    for a in articles
                ]
            else:
                if attempt < max_retries - 1:
                    time.sleep(0.5)
                    continue
                return []
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(0.5)
                continue
            print(f"[get_stock_news] 获取新闻失败: {e}")
            return []

def cls_flash_news() -> list:
    """财联社快讯"""
    headers = {
        "User-Agent": UA,
        "Referer": "https://www.cls.cn/",
    }
    r = requests.get(CLS_URL, headers=headers, timeout=10)
    d = r.json()
    return d.get("data", []) or []

# ==================== Layer 6: 基础数据层 ====================

def get_stock_basic_info(stock_code: str) -> dict:
    """获取股票基本信息"""
    code = normalize_code(stock_code)
    client = Quotes.factory(market='std')

    try:
        financial = client.financial(symbol=code)
        if financial is not None and not financial.empty:
            info = financial.iloc[0].to_dict() if len(financial) > 0 else {}
        else:
            info = {}
    except:
        info = {}

    try:
        quotes = get_stock_quote(code)
        if code in quotes:
            info.update(quotes[code])
    except:
        pass

    return info

def get_quarterly_report(stock_code: str, quarters: int = 4) -> pd.DataFrame:
    """获取季度报告数据"""
    code = normalize_code(stock_code)
    client = Quotes.factory(market='std')

    try:
        financial = client.financial(symbol=code)
        if financial is not None and not financial.empty:
            return financial.head(quarters)
    except:
        pass
    return pd.DataFrame()

def sina_financial_statements(code: str, statement: str = "balance") -> pd.DataFrame:
    """新浪财报三表"""
    url = f"{SINA_FINANCE_URL}/CN_Margin_StatementService.getFinancialStatement"
    type_map = {"balance": 1, "income": 2, "cashflow": 3}
    params = {
        "ctype": type_map.get(statement, 1),
        "symbol": f"sh{code}" if code.startswith(("6", "9")) else f"sz{code}",
    }
    headers = {"User-Agent": UA, "Referer": "https://finance.sina.com.cn/"}
    r = requests.get(url, params=params, headers=headers, timeout=15)
    d = r.json()
    rows = d.get("data", []) or []
    return pd.DataFrame(rows)

# ==================== Layer 7: 公告层 ====================

def cninfo_announcements(code: str, keyword: str = "", days: int = 30) -> list:
    """巨潮公告检索"""
    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")

    payload = {
        "stock": [code],
        "tabName": "full",
        "pageSize": 50,
        "pageNum": 1,
        "column": "szse",
        "category": "category_ndbg_szsh",
        "plate": "",
        "seDate": f"{start_date}~{end_date}",
        "searchkey": keyword,
        "secid": "",
        "sortName": "",
        "sortType": "",
        "isHLtitle": "true",
    }
    headers = {
        "User-Agent": UA,
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Referer": "https://www.cninfo.com.cn/",
    }
    r = requests.post(CNINFO_URL, json=payload, headers=headers, timeout=20)
    d = r.json()
    return d.get("announcements", []) or []

# ==================== 综合工具函数 ====================

def get_industry_comparison(stock_codes: list) -> dict:
    """对比多只股票的估值和财务指标"""
    result = {}
    for code in stock_codes:
        code = normalize_code(code)
        try:
            quotes = get_stock_quote(code)
            if code in quotes:
                result[code] = quotes[code]
            else:
                result[code] = {}
        except:
            result[code] = {}
    return result
