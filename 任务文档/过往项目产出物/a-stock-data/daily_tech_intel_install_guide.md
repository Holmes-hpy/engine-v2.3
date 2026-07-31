# 🚀 科技前沿资讯自动化任务 - 安装与使用说明

## 📋 系统概述

这是一个每日上午9:30自动执行的科技前沿资讯分析系统，专注于十五五规划相关产业（人工智能、半导体、新能源、数字经济等），结合缠论进行知识沉淀，识别反向信号。

## 🎯 核心功能

1. **资讯爬取**: 使用WebSearch工具搜索科技前沿资讯
2. **智能分析**: 缠论视角分析、反向信号识别
3. **报告生成**: 结构化分析报告
4. **知识沉淀**: 长期知识库累积

## 📁 文件结构

```
a-stock-data/
├── daily_tech_intel_automation.py    # 主分析脚本（WebSearch增强版）
├── daily_tech_intel_executor.py      # 执行器（内置示例数据）
├── scripts/
│   ├── run_daily_tech_intel.sh       # Shell执行脚本
│   └── install_daily_tech_intel.sh   # 安装脚本
├── config/
│   └── com.user.dailytechintel.plist # MacOS launchd配置文件
├── daily_tech_intel/                 # 报告输出目录
│   ├── YYYY-MM-DD_tech_intel_report.md
│   └── YYYY-MM-DD_search_results.json
├── knowledge/                        # 知识库目录
│   └── tech_intel_knowledge_YYYYMM.md
└── logs/                             # 日志目录
    ├── daily_tech_intel_YYYY-MM-DD.log
    ├── launchd_stdout.log
    └── launchd_stderr.log
```

## 🔧 安装方式

### 方式一：使用MacOS launchd（推荐）

launchd是MacOS官方的定时任务管理系统，更加稳定可靠。

#### 步骤1：手动复制配置文件

```bash
# 创建LaunchAgents目录（如果不存在）
mkdir -p ~/Library/LaunchAgents

# 复制plist配置文件
cp /Users/houpengyuan/Documents/trae_projects/a-stock-data/config/com.user.dailytechintel.plist ~/Library/LaunchAgents/

# 给shell脚本添加执行权限
chmod +x /Users/houpengyuan/Documents/trae_projects/a-stock-data/scripts/run_daily_tech_intel.sh
```

#### 步骤2：加载定时任务

```bash
# 加载任务
launchctl load ~/Library/LaunchAgents/com.user.dailytechintel.plist

# 验证任务是否加载成功
launchctl list | grep dailytechintel
```

#### 步骤3：测试任务

```bash
# 手动执行一次测试
launchctl start com.user.dailytechintel

# 查看执行日志
tail -f /Users/houpengyuan/Documents/trae_projects/a-stock-data/logs/daily_tech_intel_*.log
```

### 方式二：使用cron（简单方案）

如果launchd配置遇到问题，可以使用cron作为替代方案。

#### 步骤1：编辑cron任务

```bash
# 打开cron编辑器
crontab -e
```

#### 步骤2：添加定时任务

在cron编辑器中添加以下内容：

```cron
# 每日上午9:30执行科技资讯分析
30 9 * * * /Users/houpengyuan/Documents/trae_projects/a-stock-data/scripts/run_daily_tech_intel.sh >> /Users/houpengyuan/Documents/trae_projects/a-stock-data/logs/cron.log 2>&1
```

#### 步骤3：保存并验证

```bash
# 保存后验证cron任务
crontab -l

# 查看cron日志
tail -f /Users/houpengyuan/Documents/trae_projects/a-stock-data/logs/cron.log
```

### 方式三：手动执行（测试用）

```bash
# 直接运行Python脚本
cd /Users/houpengyuan/Documents/trae_projects/a-stock-data
python3 daily_tech_intel_executor.py

# 或运行Shell脚本
./scripts/run_daily_tech_intel.sh
```

## 📊 今日报告已生成

今日（2026-06-24）的报告已成功生成：

- **报告位置**: [2026-06-24_tech_intel_report.md](file:///Users/houpengyuan/Documents/trae_projects/a-stock-data/daily_tech_intel/2026-06-24_tech_intel_report.md)
- **资讯总数**: 25条
- **高影响力资讯**: 16条
- **反向信号**: 1条
- **缠论买点信号**: 17个

### 今日核心判断

🟢半导体 + 🟡十五五规划 + 🟡新能源 → **结构性机会持续，需分区段判断介入时机**

### 重点资讯

1. **豆包大模型2.1 Pro发布，性能直逼GPT-5** - ⭐⭐⭐⭐⭐
   - 第一类买点信号，置信度60/100
   - 6月23日火山引擎Force大会发布

2. **中国半导体设备国产化率加速提升，2026年预计达45%** - ⭐⭐⭐⭐⭐
   - 三类买点全部触发，置信度100/100
   - 十五五规划+大基金三期落地驱动

3. **618光伏新政落地，分布式光伏彻底松绑** - ⭐⭐⭐⭐
   - 储能正式成为并网通行证
   - 万亿储能市场爆发

## 🔍 任务管理命令

### launchd管理命令

```bash
# 查看任务状态
launchctl list | grep dailytechintel

# 手动执行任务
launchctl start com.user.dailytechintel

# 停止任务
launchctl stop com.user.dailytechintel

# 卸载任务
launchctl unload ~/Library/LaunchAgents/com.user.dailytechintel.plist

# 重新加载任务
launchctl load ~/Library/LaunchAgents/com.user.dailytechintel.plist
```

### cron管理命令

```bash
# 查看cron任务列表
crontab -l

# 编辑cron任务
crontab -e

# 删除所有cron任务
crontab -r
```

## 📝 日志查看

```bash
# 查看今日执行日志
tail -f /Users/houpengyuan/Documents/trae_projects/a-stock-data/logs/daily_tech_intel_2026-06-24.log

# 查看launchd标准输出
tail -f /Users/houpengyuan/Documents/trae_projects/a-stock-data/logs/launchd_stdout.log

# 查看launchd错误日志
tail -f /Users/houpengyuan/Documents/trae_projects/a-stock-data/logs/launchd_stderr.log

# 查看cron日志
tail -f /Users/houpengyuan/Documents/trae_projects/a-stock-data/logs/cron.log
```

## ⚠️ 注意事项

1. **首次安装**: 需要手动复制plist文件到LaunchAgents目录
2. **权限问题**: 如果遇到权限问题，请检查shell脚本是否有执行权限
3. **日志监控**: 建议定期查看日志，确保任务正常执行
4. **报告验证**: 每日检查生成的报告，确保内容完整
5. **知识沉淀**: 定期回顾知识库，形成长期积累

## 🎯 质量检查清单

每日任务执行后，请检查以下内容：

- ✅ 报告文件是否生成（daily_tech_intel/YYYY-MM-DD_tech_intel_report.md）
- ✅ 资讯数量是否≥10条
- ✅ 产业覆盖是否≥3个领域
- ✅ 缠论分析是否有具体触发逻辑
- ✅ 反向信号识别是否完整
- ✅ 知识沉淀是否追加到知识库

## 🔄 后续优化方向

1. **增加官方来源**: 政府官网、官方媒体、上市公司公告原文
2. **补充行业报告**: SEMI、行业协会发布的正式报告/统计数据
3. **优化搜索关键词**: 根据市场热点动态调整搜索词
4. **增强反向信号**: 增加账号历史言论追踪功能
5. **自动化推送**: 集成消息推送，每日自动发送报告摘要

## 💡 使用建议

1. **工作日持续运行**: 保持定时任务在每个工作日运行
2. **定期检查报告**: 每天上午查看生成的分析报告
3. **反向信号警惕**: 遇到高风险资讯时反向思考
4. **结合技术分析**: 将资讯分析与缠论等技术分析结合使用
5. **知识积累**: 定期回顾知识库中的历史数据

## 📞 问题排查

### 问题1：任务未执行

**检查步骤**:
1. 确认launchd任务是否加载: `launchctl list | grep dailytechintel`
2. 查看launchd错误日志: `tail -f logs/launchd_stderr.log`
3. 检查shell脚本权限: `ls -l scripts/run_daily_tech_intel.sh`

### 问题2：报告内容为空

**检查步骤**:
1. 查看执行日志: `tail -f logs/daily_tech_intel_*.log`
2. 检查Python环境: `python3 --version`
3. 验证脚本路径: 确保在项目目录下执行

### 问题3：权限错误

**解决方案**:
1. 给shell脚本添加执行权限: `chmod +x scripts/*.sh`
2. 检查目录权限: `ls -la daily_tech_intel/ logs/ knowledge/`

---

**系统版本**: v3.0 (WebSearch增强版)
**创建时间**: 2026-06-24
**执行频率**: 每日上午9:30