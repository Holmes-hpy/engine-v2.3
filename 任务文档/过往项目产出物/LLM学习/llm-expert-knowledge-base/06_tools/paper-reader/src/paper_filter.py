#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
论文筛选模块
从采集的论文中按照标准筛选出最具价值的论文
"""

import json
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple
import arxiv


class PaperFilter:
    """论文筛选器"""

    def __init__(self, config_path: str):
        self.config = self._load_config(config_path)
        self.base_path = Path(__file__).parent.parent.parent / self.config["general"]["base_path"]
        self.inbox_dir = self.base_path / self.config["general"]["inbox_dir"]
        self.papers_dir = self.base_path / self.config["general"]["papers_dir"]
        self.filtering_config = self.config["filtering"]

    def _load_config(self, config_path: str) -> Dict:
        """加载配置"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"加载配置失败: {e}")
            return {}

    def find_recent_papers(self, days: int = 7) -> List[Dict]:
        """查找过去N天内的论文"""
        print(f"\n🔍 扫描过去 {days} 天的论文...")

        recent_papers = []
        cutoff_date = datetime.now() - timedelta(days=days)

        if not self.inbox_dir.exists():
            print(f"⚠️ inbox目录不存在: {self.inbox_dir}")
            return []

        for md_file in self.inbox_dir.rglob("*.md"):
            try:
                content = md_file.read_text(encoding='utf-8')
                mtime = datetime.fromtimestamp(md_file.stat().st_mtime)

                if mtime >= cutoff_date:
                    paper_info = self._extract_paper_info(content, md_file)
                    if paper_info:
                        recent_papers.append(paper_info)
            except Exception as e:
                print(f"⚠️ 处理文件失败 {md_file.name}: {e}")

        print(f"   发现 {len(recent_papers)} 篇近期论文")
        return recent_papers

    def _extract_paper_info(self, content: str, file_path: Path) -> Dict:
        """从文件内容中提取论文信息"""
        paper_info = {
            "title": "",
            "authors": "",
            "institutions": "",
            "venue": "",
            "date": "",
            "arxiv_url": "",
            "github_url": "",
            "abstract": "",
            "source_file": str(file_path),
            "score": 0
        }

        title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        if title_match:
            paper_info["title"] = title_match.group(1).strip()

        arxiv_match = re.search(r'https?://arxiv\.org/(?:abs|pdf)/(\d+\.\d+)', content)
        if arxiv_match:
            paper_info["arxiv_url"] = f"https://arxiv.org/abs/{arxiv_match.group(1)}"

        github_match = re.search(r'https?://github\.com/[\w\-]+/[\w\-]+', content)
        if github_match:
            paper_info["github_url"] = github_match.group(0)

        author_match = re.search(r'\*\*作者\*\*[：:]\s*(.+)', content)
        if author_match:
            paper_info["authors"] = author_match.group(1).strip()

        inst_match = re.search(r'\*\*机构\*\*[：:]\s*(.+)', content)
        if inst_match:
            paper_info["institutions"] = inst_match.group(1).strip()

        date_match = re.search(r'(\d{4}-\d{2}-\d{2})', content)
        if date_match:
            paper_info["date"] = date_match.group(1)

        return paper_info if paper_info["title"] else None

    def score_papers(self, papers: List[Dict]) -> List[Dict]:
        """对论文进行评分"""
        print("\n📊 对论文进行评分...")

        top_conferences = self.filtering_config["top_conferences"]
        top_institutions = self.filtering_config["top_institutions"]

        for paper in papers:
            score = 0

            venue = paper.get("venue", "").upper()
            for conf in top_conferences:
                if conf.upper() in venue:
                    score += 30
                    break

            institutions = paper.get("institutions", "").upper()
            for inst in top_institutions:
                if inst.upper() in institutions:
                    score += 25
                    break

            if paper.get("github_url"):
                score += 20

            if paper.get("arxiv_url"):
                score += 10

            title = paper.get("title", "").upper()
            llm_keywords = ["LLM", "GPT", "TRANSFORMER", "LARGE LANGUAGE MODEL",
                         "NEURAL NETWORK", "DEEP LEARNING", "ATTENTION"]
            for keyword in llm_keywords:
                if keyword in title:
                    score += 5

            paper["score"] = score

        papers.sort(key=lambda x: x["score"], reverse=True)

        return papers

    def filter_papers(self, papers: List[Dict]) -> List[Dict]:
        """过滤论文"""
        print("\n🔎 应用筛选标准...")

        filtered = []
        target_count = self.filtering_config["weekly_paper_count"]

        for paper in papers:
            if self._is_already_read(paper):
                continue

            if paper["score"] < 5:
                continue

            if not self._is_relevant_to_llm(paper):
                continue

            filtered.append(paper)

            if len(filtered) >= target_count:
                break

        print(f"   筛选出 {len(filtered)} 篇高质量论文")
        return filtered

    def _is_already_read(self, paper: Dict) -> bool:
        """检查论文是否已读过"""
        source_file = paper.get("source_file", "")
        
        if not source_file:
            return False

        source_path = Path(source_file)
        
        if source_path.stem.startswith("已读-"):
            return True

        if self.papers_dir.exists():
            for read_file in self.papers_dir.glob("*.md"):
                if source_path.stem in read_file.name:
                    return True

        return False

    def _is_relevant_to_llm(self, paper: Dict) -> bool:
        """检查论文是否与大模型相关"""
        title = paper.get("title", "").lower()
        abstract = paper.get("abstract", "").lower()

        llm_keywords = [
            "large language model", "llm", "gpt", "transformer",
            "language model", "text generation", "natural language",
            "deep learning", "neural network", "attention mechanism",
            "bert", "pre-training", "fine-tuning", "instruction tuning"
        ]

        content = title + " " + abstract
        for keyword in llm_keywords:
            if keyword in content:
                return True

        return False

    def generate_selection_report(self, papers: List[Dict]) -> str:
        """生成论文筛选报告"""
        report = "# 本周论文精读筛选报告\n\n"
        report += f"筛选时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        report += f"筛选标准：{self._get_filtering_criteria()}\n\n"
        report += "---\n\n"
        report += "## 入选论文列表\n\n"

        for i, paper in enumerate(papers, 1):
            report += f"### {i}. {paper['title']}\n\n"
            report += f"- **作者**：{paper.get('authors', '未知')}\n"
            report += f"- **机构**：{paper.get('institutions', '未知')}\n"
            report += f"- **会议/期刊**：{paper.get('venue', 'arXiv')}\n"
            report += f"- **发表时间**：{paper.get('date', '未知')}\n"
            report += f"- **arXiv链接**：{paper.get('arxiv_url', '无')}\n"
            report += f"- **官方代码**：{paper.get('github_url', '无')}\n"
            report += f"- **筛选得分**：{paper['score']}\n"
            report += f"- **筛选理由**：{self._get_selection_reason(paper)}\n\n"
            report += "---\n\n"

        return report

    def _get_filtering_criteria(self) -> str:
        """获取筛选标准说明"""
        return (
            "1. 优先顶级会议论文（ICML、NeurIPS、ICLR、ACL等）+30分\n"
            "2. 优先顶级机构论文（OpenAI、Google DeepMind等）+25分\n"
            "3. 有官方代码实现 +20分\n"
            "4. 有arXiv链接 +10分\n"
            "5. 与大模型领域相关 +5分"
        )

    def _get_selection_reason(self, paper: Dict) -> str:
        """生成论文的筛选理由"""
        reasons = []

        if paper.get("github_url"):
            reasons.append("有官方代码实现")

        venue = paper.get("venue", "").upper()
        if any(conf.upper() in venue for conf in self.filtering_config["top_conferences"][:5]):
            reasons.append("来自顶级会议")

        institutions = paper.get("institutions", "").upper()
        if any(inst.upper() in institutions for inst in self.filtering_config["top_institutions"][:5]):
            reasons.append("来自顶级研究机构")

        if not reasons:
            reasons.append("综合评分较高")

        return "；".join(reasons)

    def run_weekly_selection(self) -> List[Dict]:
        """运行每周论文筛选流程"""
        print("=" * 60)
        print("📚 论文筛选模块")
        print("=" * 60)

        recent_papers = self.find_recent_papers(days=7)

        if not recent_papers:
            print("\n⚠️ 未找到近期论文，尝试从arXiv获取...")
            recent_papers = self.fetch_arxiv_papers()

        scored_papers = self.score_papers(recent_papers)
        selected_papers = self.filter_papers(scored_papers)

        if selected_papers:
            report = self.generate_selection_report(selected_papers)
            report_file = self.papers_dir / f"{datetime.now().strftime('%Y-%m-%d')}-论文筛选报告.md"
            report_file.parent.mkdir(parents=True, exist_ok=True)
            report_file.write_text(report, encoding='utf-8')
            print(f"\n✓ 筛选报告已保存: {report_file.name}")

        print("\n✅ 论文筛选完成！")
        return selected_papers

    def fetch_arxiv_papers(self, max_results: int = 20) -> List[Dict]:
        """从arXiv获取最新论文"""
        print(f"\n🔍 从arXiv获取最新论文...")

        papers = []

        try:
            search_query = "cat:cs.CL OR cat:cs.LG OR cat:cs.AI"
            client = arxiv.Client()
            search = arxiv.Search(
                query=search_query,
                max_results=max_results,
                sort_by=arxiv.SortCriterion.SubmittedDate
            )

            for result in client.results(search):
                paper = {
                    "title": result.title,
                    "authors": ", ".join([a.name for a in result.authors]),
                    "arxiv_url": result.entry_id,
                    "github_url": "",
                    "abstract": result.summary,
                    "date": result.published.strftime("%Y-%m-%d"),
                    "venue": "arXiv",
                    "score": 0
                }
                papers.append(paper)

            print(f"   从arXiv获取了 {len(papers)} 篇论文")

        except Exception as e:
            print(f"⚠️ 从arXiv获取论文失败: {e}")

        return papers


def main():
    """主函数"""
    import sys

    config_path = Path(__file__).parent.parent / "config/config.json"
    filter_module = PaperFilter(str(config_path))
    selected_papers = filter_module.run_weekly_selection()

    if selected_papers:
        print(f"\n📋 已筛选出 {len(selected_papers)} 篇论文进行精读")
        for i, paper in enumerate(selected_papers, 1):
            print(f"{i}. {paper['title']}")
    else:
        print("\n⚠️ 未筛选出论文")


if __name__ == "__main__":
    main()
