
# 大模型信息雷达

自动采集大模型领域最新信息，为知识库提供高质量原始素材。

## 功能

- 多源采集：从 arXiv、Hugging Face、GitHub、技术博客等权威来源采集内容
- 智能筛选：自动筛选与大模型技术相关的高质量内容
- 去重处理：避免重复采集相同内容
- 重要性评分：对采集内容进行1-5星重要性评分
- 每日简报：生成每日信息汇总报告

## 安装

```bash
cd llm-info-radar
pip install -r requirements.txt
```

## 使用方法

### 单次运行

```bash
python src/main.py
```

### 配置定时任务（macOS/Linux）

使用 crontab 设置每日定时运行：

```bash
crontab -e
```

添加以下内容（例如每天早上9点运行）：

```
0 9 * * * cd /path/to/llm-info-radar &amp;&amp; python src/main.py &gt;&gt; logs/cron.log 2&gt;&amp;1
```

## 配置说明

编辑 `config/config.json` 可以自定义：

- 采集来源
- 请求超时时间
- 用户代理
- 摘要长度限制

## 采集来源

1. arXiv (cs.CL, cs.LG)
2. Hugging Face Blog
3. Hugging Face Papers
4. OpenAI Blog
5. Anthropic Research
6. DeepMind Blog
7. GitHub Trending (Python, Machine Learning)
8. 机器之心
9. 量子位
10. InfoQ AI

## 输出

采集的内容会保存到：
- 单条内容：`../../01_inbox/YYYY-MM-DD-XXX-Title.md`
- 每日简报：`../../01_inbox/YYYY-MM-DD-每日信息简报.md`
- 运行日志：`logs/llm-info-radar-YYYYMMDD.log`

## 注意事项

- 请遵守各网站的 robots.txt 协议和访问频率限制
- 本工具仅用于学习和研究目的
- 请勿用于商业用途或频繁爬取

