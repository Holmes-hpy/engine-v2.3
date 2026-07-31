#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
周度报告生成模块
生成周度论文精读总结报告，推送给用户
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List


class WeeklyReporter:
    """周度报告生成器"""

    def __init__(self, config_path: str):
        self.config = self._load_config(config_path)
        self.base_path = Path(__file__).parent.parent.parent / self.config["general"]["base_path"]
        self.papers_dir = self.base_path / self.config["general"]["papers_dir"]
        self.report_config = self.config["report"]

    def _load_config(self, config_path: str) -> Dict:
        """加载配置"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"加载配置失败: {e}")
            return {}

    def find_this_week_papers(self) -> List[Path]:
        """查找本周精读的论文"""
        print("\n🔍 扫描本周论文...")

        week_ago = datetime.now() - timedelta(days=7)
        week_papers = []

        if not self.papers_dir.exists():
            print(f"   ⚠️ 论文目录不存在")
            return []

        for paper_file in self.papers_dir.glob("*.md"):
            if "周度报告" in paper_file.name or "筛选报告" in paper_file.name:
                continue

            try:
                mtime = datetime.fromtimestamp(paper_file.stat().st_mtime)
                if mtime >= week_ago:
                    week_papers.append(paper_file)
            except Exception as e:
                print(f"   ⚠️ 处理文件失败 {paper_file.name}: {e}")

        print(f"   发现 {len(week_papers)} 篇本周论文")
        return week_papers

    def extract_paper_summary(self, paper_file: Path) -> Dict:
        """提取论文摘要信息"""
        try:
            content = paper_file.read_text(encoding='utf-8')

            summary = {
                "file": paper_file.name,
                "title": self._extract_title(content),
                "authors": self._extract_field(content, "作者"),
                "venue": self._extract_field(content, "会议/期刊"),
                "date": self._extract_field(content, "发表时间"),
                "arxiv_url": self._extract_field(content, "arXiv链接"),
                "github_url": self._extract_field(content, "官方代码"),
                "contributions": self._extract_contributions(content),
                "key_findings": self._extract_key_findings(content),
                "reproduction_status": self._extract_reproduction_status(content)
            }

            return summary

        except Exception as e:
            print(f"   ⚠️ 提取失败 {paper_file.name}: {e}")
            return {}

    def _extract_title(self, content: str) -> str:
        """提取标题"""
        lines = content.split('\n')
        for line in lines:
            if line.startswith('# ') and len(line) > 2:
                return line[2:].strip()
        return "未知标题"

    def _extract_field(self, content: str, field_name: str) -> str:
        """提取字段"""
        import re
        pattern = rf'\*\*{field_name}\*\*[：:]\s*(.+)'
        match = re.search(pattern, content)
        return match.group(1).strip() if match else "未知"

    def _extract_contributions(self, content: str) -> str:
        """提取贡献"""
        contributions = []

        if "核心贡献" in content:
            section_start = content.find("核心贡献")
            section_end = content.find("##", section_start + 10)
            section = content[section_start:section_end] if section_end > 0 else content[section_start:]

            lines = section.split('\n')
            for line in lines[:5]:
                line = line.strip()
                if line and not line.startswith('#') and not line.startswith('**'):
                    contributions.append(line)
                    if len(contributions) >= 3:
                        break

        return '\n'.join(contributions) if contributions else "详见论文全文"

    def _extract_key_findings(self, content: str) -> str:
        """提取关键发现"""
        findings = []

        if "主要实验结果" in content:
            section_start = content.find("主要实验结果")
            section_end = content.find("##", section_start + 10)
            section = content[section_start:section_end] if section_end > 0 else content[section_start:]

            lines = section.split('\n')
            for line in lines[:3]:
                line = line.strip()
                if line and not line.startswith('#') and not line.startswith('-'):
                    findings.append(line)

        return '\n'.join(findings) if findings else "详见论文全文"

    def _extract_reproduction_status(self, content: str) -> str:
        """提取复现状态"""
        if "复现状态" in content:
            return self._extract_field(content, "复现状态")
        return "未复现"

    def generate_weekly_report(self, paper_summaries: List[Dict]) -> str:
        """生成周度报告"""
        print("\n📝 生成周度报告...")

        report = "# 本周论文精读周度报告\n\n"
        report += f"**生成时间**：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        report += f"**本周精读论文数**：{len(paper_summaries)}\n\n"

        report += "---\n\n"

        report += "## 本周精读论文列表\n\n"

        for i, summary in enumerate(paper_summaries, 1):
            report += f"### {i}. {summary.get('title', '未知标题')}\n\n"

            report += f"- **作者**：{summary.get('authors', '未知')}\n"
            report += f"- **机构/会议**：{summary.get('venue', '未知')}\n"
            report += f"- **发表时间**：{summary.get('date', '未知')}\n"
            report += f"- **arXiv链接**：{summary.get('arxiv_url', '无')}\n"
            report += f"- **官方代码**：{summary.get('github_url', '无')}\n"
            report += f"- **复现状态**：{summary.get('reproduction_status', '未复现')}\n\n"

            report += f"**核心贡献**：\n{summary.get('contributions', '')}\n\n"

            report += f"**关键发现**：\n{summary.get('key_findings', '')}\n\n"

            report += f"**解读文件**：{summary.get('file', '')}\n\n"

            report += "---\n\n"

        report += "## 本周重要技术进展\n\n"

        if paper_summaries:
            report += "### 主要发现\n\n"

            llm_related = [s for s in paper_summaries
                         if 'LLM' in s.get('title', '').upper() or
                            'Language Model' in s.get('title', '')]

            if llm_related:
                report += f"- 本周重点关注了大模型相关研究，共精读了 {len(llm_related)} 篇相关论文\n"

            code_available = [s for s in paper_summaries
                            if s.get('github_url', '无') != '无']

            if code_available:
                report += f"- 其中 {len(code_available)} 篇提供了官方代码实现\n"

            reproduced = [s for s in paper_summaries
                        if '成功' in s.get('reproduction_status', '')]

            if reproduced:
                report += f"- 成功复现了 {len(reproduced)} 篇论文的实验\n"

            report += "\n### 技术趋势\n\n"
            report += "- 大模型效率优化持续是研究热点\n"
            report += "- 多模态学习取得显著进展\n"
            report += "- 代码生成和推理能力不断提升\n"

        else:
            report += "本周未精读论文\n"

        report += "\n## 对大模型领域发展的影响分析\n\n"

        if paper_summaries:
            report += "### 研究方向影响\n\n"

            report += "1. **技术创新**：本周论文推动了以下技术方向的发展\n"
            report += "   - 模型架构创新\n"
            report += "   - 训练效率提升\n"
            report += "   - 推理优化\n\n"

            report += "2. **工程实践**：提供了可复现的代码实现\n"
            report += "   - 促进技术落地\n"
            report += "   - 加速研究进展\n\n"

            report += "3. **未来趋势**：这些工作预示着以下发展方向\n"
            report += "   - 更高效的模型\n"
            report += "   - 更广泛的应用\n"
            report += "   - 更好的用户体验\n"

        else:
            report += "本周暂无相关分析\n"

        report += "\n\n---\n\n"
        report += f"*本报告由论文精读与复现Skill自动生成*\n"
        report += f"*报告时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n"

        return report

    def save_report(self, report_content: str) -> Path:
        """保存报告"""
        print("\n💾 保存报告...")

        report_filename = datetime.now().strftime("%Y-%m-%d-周度研究报告.md")
        report_file = self.papers_dir / report_filename

        report_file.parent.mkdir(parents=True, exist_ok=True)
        report_file.write_text(report_content, encoding='utf-8')

        print(f"   ✓ 报告已保存: {report_filename}")
        return report_file

    def generate_summary_for_push(self, paper_summaries: List[Dict]) -> str:
        """生成推送摘要"""
        summary = "📚 本周论文精读报告\n\n"

        summary += f"本周共精读 {len(paper_summaries)} 篇论文：\n\n"

        for i, summary in enumerate(paper_summaries[:3], 1):
            summary += f"{i}. {summary.get('title', '未知')[:50]}\n"
            summary += f"   - {summary.get('venue', 'arXiv')} | {summary.get('date', '')}\n"
            summary += f"   - 复现状态：{summary.get('reproduction_status', '未复现')}\n\n"

        if len(paper_summaries) > 3:
            summary += f"...等共 {len(paper_summaries)} 篇论文\n\n"

        summary += "💡 主要发现：\n"
        summary += "- 大模型效率优化持续是研究热点\n"
        summary += "- 多篇论文提供了可复现的代码\n\n"

        summary += "📖 完整报告已生成，需要查看详情吗？\n"

        return summary

    def generate_weekly_report_all(self) -> Dict:
        """执行完整的周度报告生成"""
        print("=" * 60)
        print("📊 周度报告生成模块")
        print("=" * 60)

        week_papers = self.find_this_week_papers()

        paper_summaries = []
        for paper_file in week_papers:
            summary = self.extract_paper_summary(paper_file)
            if summary:
                paper_summaries.append(summary)

        report_content = self.generate_weekly_report(paper_summaries)
        report_file = self.save_report(report_content)

        push_summary = self.generate_summary_for_push(paper_summaries)

        print("\n" + "=" * 60)
        print("✅ 周度报告生成完成")
        print("=" * 60)

        return {
            "report_file": report_file,
            "report_content": report_content,
            "push_summary": push_summary,
            "paper_count": len(paper_summaries),
            "paper_summaries": paper_summaries
        }


def main():
    """主函数"""
    config_path = Path(__file__).parent.parent / "config/config.json"
    reporter = WeeklyReporter(str(config_path))

    result = reporter.generate_weekly_report_all()

    print("\n📋 推送摘要：")
    print(result["push_summary"])


if __name__ == "__main__":
    main()
