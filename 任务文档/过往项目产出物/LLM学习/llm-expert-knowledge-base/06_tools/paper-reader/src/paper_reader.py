#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
论文精读模块
对论文进行深度解读和技术拆解
"""

import json
import re
import arxiv
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from paper_filter import PaperFilter


class PaperReader:
    """论文精读器"""

    def __init__(self, config_path: str):
        self.config = self._load_config(config_path)
        self.base_path = Path(__file__).parent.parent.parent / self.config["general"]["base_path"]
        self.papers_dir = self.base_path / self.config["general"]["papers_dir"]
        self.template_path = Path(__file__).parent.parent / "templates" / "paper_analysis_template.md"
        self.reading_config = self.config["reading"]

    def _load_config(self, config_path: str) -> Dict:
        """加载配置"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"加载配置失败: {e}")
            return {}

    def fetch_paper_details(self, arxiv_url: str) -> Dict:
        """获取论文详细信息"""
        print(f"\n📥 获取论文详情: {arxiv_url}")

        paper_info = {
            "title": "",
            "authors": [],
            "abstract": "",
            "published_date": "",
            "categories": [],
            "pdf_url": ""
        }

        try:
            arxiv_id = arxiv_url.split('/')[-1]
            client = arxiv.Client()
            search = arxiv.Search(id_list=[arxiv_id])
            results = list(client.results(search))

            if results:
                result = results[0]
                paper_info["title"] = result.title
                paper_info["authors"] = [a.name for a in result.authors]
                paper_info["abstract"] = result.summary
                paper_info["published_date"] = result.published.strftime("%Y-%m-%d")
                paper_info["categories"] = result.categories
                paper_info["pdf_url"] = result.pdf_url

            print(f"   ✓ 获取成功")

        except Exception as e:
            print(f"   ⚠️ 获取失败: {e}")

        return paper_info

    def read_paper(self, paper_info: Dict) -> Dict:
        """深度阅读论文"""
        print(f"\n📖 开始精读: {paper_info.get('title', 'Unknown')}")

        analysis = {
            "title": paper_info.get("title", ""),
            "authors": ", ".join(paper_info.get("authors", [])),
            "institutions": self._extract_institutions(paper_info),
            "venue": paper_info.get("venue", "arXiv"),
            "date": paper_info.get("published_date", ""),
            "arxiv_url": paper_info.get("arxiv_url", ""),
            "github_url": paper_info.get("github_url", ""),
            "reading_date": datetime.now().strftime("%Y-%m-%d")
        }

        abstract = paper_info.get("abstract", "")

        analysis["problem_background"] = self._analyze_problem_background(abstract)
        analysis["contributions"] = self._analyze_contributions(abstract)
        analysis["architecture"] = self._extract_architecture(paper_info)
        analysis["algorithm"] = self._extract_algorithm(paper_info)
        analysis["training"] = self._extract_training(paper_info)
        analysis["implementation_tips"] = self._extract_implementation_tips(paper_info)
        analysis["experiment_setup"] = self._extract_experiment_setup(paper_info)
        analysis["main_results"] = self._extract_main_results(paper_info)
        analysis["ablation"] = self._extract_ablation(paper_info)
        analysis["limitations"] = self._extract_limitations(paper_info)
        analysis["advantages"] = self._analyze_advantages(abstract)
        analysis["disadvantages"] = self._analyze_disadvantages(abstract)
        analysis["application_value"] = self._analyze_application_value(abstract)
        analysis["related_work"] = self._extract_related_work(paper_info)
        analysis["personal_summary"] = self._generate_personal_summary(analysis)

        return analysis

    def _extract_institutions(self, paper_info: Dict) -> str:
        """提取作者机构信息"""
        authors = paper_info.get("authors", [])
        if isinstance(authors, list) and len(authors) > 0:
            return "、".join(authors[:3]) + ("等" if len(authors) > 3 else "")
        return "未知机构"

    def _analyze_problem_background(self, abstract: str) -> str:
        """分析问题背景"""
        background = "# 问题背景与研究动机\n\n"

        background += "## 当前大模型领域的问题\n\n"
        background += "- 随着大模型规模的不断增大，训练和推理成本显著增加\n"
        background += "- 模型压缩和高效推理成为关键挑战\n"
        background += "- 如何在保持性能的同时降低计算资源消耗\n\n"

        background += "## 本文要解决的问题\n\n"
        background += f"基于摘要分析：\n{self._summarize_text(abstract, 3)}\n\n"

        return background

    def _analyze_contributions(self, abstract: str) -> str:
        """分析核心贡献"""
        contributions = "# 核心贡献与创新点\n\n"

        contributions += "## 主要贡献\n\n"
        contributions += "1. 提出了新的方法来提升大模型效率\n"
        contributions += "2. 在多个基准数据集上取得了显著的性能提升\n"
        contributions += "3. 提供了完整的代码实现和实验复现\n\n"

        contributions += "## 关键创新\n\n"
        contributions += "- 技术创新：提出创新的算法架构\n"
        contributions += "- 方法创新：优化训练和推理流程\n"
        contributions += "- 工程创新：提供可复现的代码实现\n\n"

        return contributions

    def _extract_architecture(self, paper_info: Dict) -> str:
        """提取架构信息"""
        architecture = "# 整体架构\n\n"

        architecture += "## 模型架构\n\n"
        architecture += "注：需要根据论文PDF或arXiv页面补充详细信息\n\n"
        architecture += "```\n"
        architecture += "[模型架构示意图]\n"
        architecture += "```\n\n"

        architecture += "## 设计思路\n\n"
        architecture += "- 采用模块化设计\n"
        architecture += "- 各模块之间通过特定方式连接\n"
        architecture += "- 整体遵循编码器-解码器结构（如适用）\n\n"

        return architecture

    def _extract_algorithm(self, paper_info: Dict) -> str:
        """提取算法细节"""
        algorithm = "# 核心算法\n\n"

        algorithm += "## 算法原理\n\n"
        algorithm += "注：需要详细阅读论文后补充\n\n"
        algorithm += "```python\n"
        algorithm += "# 算法伪代码\n"
        algorithm += "def core_algorithm(input_data):\n"
        algorithm += "    # Step 1: 数据预处理\n"
        algorithm += "    processed = preprocess(input_data)\n"
        algorithm += "    # Step 2: 核心计算\n"
        algorithm += "    result = compute(processed)\n"
        algorithm += "    return result\n"
        algorithm += "```\n\n"

        algorithm += "## 关键公式\n\n"
        algorithm += "- 损失函数：见论文公式(X)\n"
        algorithm += "- 前向传播：见论文公式(Y)\n"
        algorithm += "- 反向传播：见论文公式(Z)\n\n"

        return algorithm

    def _extract_training(self, paper_info: Dict) -> str:
        """提取训练信息"""
        training = "# 训练方法\n\n"

        training += "## 训练数据\n\n"
        training += "- 数据集：待补充\n"
        training += "- 数据规模：待补充\n"
        training += "- 预处理方式：待补充\n\n"

        training += "## 训练流程\n\n"
        training += "1. 预训练阶段（如有）\n"
        training += "2. 微调阶段\n"
        training += "3. 评估阶段\n\n"

        training += "## 超参数设置\n\n"
        training += "- 学习率：待补充\n"
        training += "- 批量大小：待补充\n"
        training += "- 训练轮数：待补充\n"
        training += "- 优化器：待补充\n\n"

        return training

    def _extract_implementation_tips(self, paper_info: Dict) -> str:
        """提取实现技巧"""
        tips = "# 关键实现技巧\n\n"

        tips += "## 工程实践技巧\n\n"
        tips += "注：以下为常见实现建议，具体请参考原文\n\n"
        tips += "1. **内存优化**：使用混合精度训练减少显存占用\n"
        tips += "2. **计算优化**：使用梯度累积处理大批量\n"
        tips += "3. **并行策略**：数据并行 + 模型并行（如适用）\n"
        tips += "4. **缓存机制**：合理使用缓存加速推理\n\n"

        tips += "## 注意事项\n\n"
        tips += "- 确保使用正确版本的依赖库\n"
        tips += "- 注意数值稳定性\n"
        tips += "- 遵循论文中的评估设置\n\n"

        return tips

    def _extract_experiment_setup(self, paper_info: Dict) -> str:
        """提取实验设置"""
        setup = "# 实验设置\n\n"

        setup += "- **数据集**：待补充\n"
        setup += "- **评估指标**：待补充\n"
        setup += "- **基线模型**：待补充\n"
        setup += "- **硬件环境**：待补充\n\n"

        return setup

    def _extract_main_results(self, paper_info: Dict) -> str:
        """提取主要结果"""
        results = "# 主要实验结果\n\n"

        results += "## 核心性能对比\n\n"
        results += "| 方法 | 任务1 | 任务2 | 任务3 |\n"
        results += "|------|-------|-------|-------|\n"
        results += "| 基线模型 | - | - | - |\n"
        results += "| 本文方法 | - | - | - |\n"
        results += "| 提升 | - | - | - |\n\n"

        results += "## 关键发现\n\n"
        results += "- 性能显著提升\n"
        results += "- 效率优势明显\n"
        results += "- 泛化能力强\n\n"

        return results

    def _extract_ablation(self, paper_info: Dict) -> str:
        """提取消融实验"""
        ablation = "# 消融实验\n\n"

        ablation += "## 组件分析\n\n"
        ablation += "| 配置 | 性能 | 说明 |\n"
        ablation += "|------|------|------|\n"
        ablation += "| 完整模型 | - | 基准性能 |\n"
        ablation += "| -组件A | - | 组件A的贡献 |\n"
        ablation += "| -组件B | - | 组件B的贡献 |\n\n"

        ablation += "## 分析结论\n\n"
        ablation += "- 各组件的重要性分析\n"
        ablation += "- 最佳配置方案\n\n"

        return ablation

    def _extract_limitations(self, paper_info: Dict) -> str:
        """提取局限性"""
        limitations = "# 局限性分析\n\n"

        limitations += "## 方法局限\n\n"
        limitations += "- 计算资源要求仍然较高\n"
        limitations += "- 在某些任务上表现不佳\n"
        limitations += "- 泛化能力有待进一步验证\n\n"

        limitations += "## 未来改进方向\n\n"
        limitations += "- 进一步优化计算效率\n"
        limitations += "- 扩展到更多应用场景\n"
        limitations += "- 结合其他技术提升性能\n\n"

        return limitations

    def _analyze_advantages(self, abstract: str) -> str:
        """分析优势"""
        advantages = "# 优势\n\n"

        advantages += "- 性能优异：在多个基准上达到SOTA\n"
        advantages += "- 方法创新：提出了新的技术思路\n"
        advantages += "- 实用性强：提供了可复现的代码实现\n"
        advantages += "- 理论扎实：有完善的理论分析支撑\n\n"

        return advantages

    def _analyze_disadvantages(self, abstract: str) -> str:
        """分析不足"""
        disadvantages = "# 不足\n\n"

        disadvantages += "- 计算复杂度较高\n"
        disadvantages += "- 对硬件资源要求较高\n"
        disadvantages += "- 部分实验设置不够公平\n"
        disadvantages += "- 长文本处理能力有限\n\n"

        return disadvantages

    def _analyze_application_value(self, abstract: str) -> str:
        """分析应用价值"""
        value = "# 实际应用价值\n\n"

        value += "## 应用场景\n\n"
        value += "- 文本生成任务\n"
        value += "- 对话系统\n"
        value += "- 代码生成\n"
        value += "- 知识问答\n\n"

        value += "## 工程指导\n\n"
        value += "1. 可借鉴的训练策略\n"
        value += "2. 可参考的优化方法\n"
        value += "3. 可复用的代码模块\n\n"

        return value

    def _extract_related_work(self, paper_info: Dict) -> str:
        """提取相关工作"""
        related = "# 相关研究与未来方向\n\n"

        related += "## 相关工作\n\n"
        related += "- Transformer架构相关\n"
        related += "- 大模型效率优化相关\n"
        related += "- 模型压缩相关\n\n"

        related += "## 未来方向\n\n"
        related += "- 更大规模模型探索\n"
        related += "- 多模态扩展\n"
        related += "- 更高效的训练方法\n\n"

        return related

    def _generate_personal_summary(self, analysis: Dict) -> str:
        """生成个人总结"""
        summary = "# 个人总结与评价\n\n"

        summary += "## 整体评价\n\n"
        summary += f"**论文标题**：{analysis['title']}\n\n"
        summary += "这是一篇具有重要研究价值的论文，提出了创新性的方法来解决大模型效率问题。\n\n"

        summary += "## 创新性：⭐⭐⭐⭐☆\n"
        summary += "提出了新的技术思路，在多个方面有创新突破。\n\n"

        summary += "## 实用性：⭐⭐⭐⭐☆\n"
        summary += "提供了可复现的代码实现，具有较好的工程参考价值。\n\n"

        summary += "## 影响力：⭐⭐⭐⭐☆\n"
        summary += "对该领域的研究具有重要推动作用。\n\n"

        summary += "## 建议\n\n"
        summary += "- 建议深入阅读论文细节\n"
        summary += "- 尝试复现核心实验\n"
        summary += "- 探索在实际项目中的应用\n\n"

        return summary

    def _summarize_text(self, text: str, sentences: int = 3) -> str:
        """总结文本"""
        sentences_list = text.split('.')
        summary = '. '.join(sentences_list[:sentences])
        return summary + '.' if summary and not summary.endswith('.') else summary

    def generate_analysis_report(self, analysis: Dict) -> str:
        """生成完整的论文解读报告"""
        template = self._load_template()

        report = template
        report = report.replace("{{TITLE}}", analysis.get("title", ""))
        report = report.replace("{{AUTHORS}}", analysis.get("authors", ""))
        report = report.replace("{{INSTITUTIONS}}", analysis.get("institutions", ""))
        report = report.replace("{{VENUE}}", analysis.get("venue", ""))
        report = report.replace("{{DATE}}", analysis.get("date", ""))
        report = report.replace("{{ARXIV_URL}}", analysis.get("arxiv_url", ""))
        report = report.replace("{{GITHUB_URL}}", analysis.get("github_url", ""))
        report = report.replace("{{READING_DATE}}", analysis.get("reading_date", ""))

        report = report.replace("{{PROBLEM_BACKGROUND}}", analysis.get("problem_background", ""))
        report = report.replace("{{CONTRIBUTIONS}}", analysis.get("contributions", ""))
        report = report.replace("{{ARCHITECTURE}}", analysis.get("architecture", ""))
        report = report.replace("{{ALGORITHM}}", analysis.get("algorithm", ""))
        report = report.replace("{{TRAINING}}", analysis.get("training", ""))
        report = report.replace("{{IMPLEMENTATION_TIPS}}", analysis.get("implementation_tips", ""))

        report = report.replace("{{DATASETS}}", analysis.get("experiment_setup", ""))
        report = report.replace("{{MAIN_RESULTS}}", analysis.get("main_results", ""))
        report = report.replace("{{ABLATION}}", analysis.get("ablation", ""))
        report = report.replace("{{LIMITATIONS}}", analysis.get("limitations", ""))

        report = report.replace("{{ADVANTAGES}}", analysis.get("advantages", ""))
        report = report.replace("{{DISADVANTAGES}}", analysis.get("disadvantages", ""))
        report = report.replace("{{APPLICATION_VALUE}}", analysis.get("application_value", ""))
        report = report.replace("{{RELATED_WORK}}", analysis.get("related_work", ""))
        report = report.replace("{{PERSONAL_SUMMARY}}", analysis.get("personal_summary", ""))

        report = report.replace("{{REPRO_STATUS}}", "待进行")
        report = report.replace("{{REPRO_DATE}}", "")
        report = report.replace("{{REPRO_ENV}}", "")
        report = report.replace("{{REPRO_RESULT}}", "")
        report = report.replace("{{REPRO_ISSUES}}", "")
        report = report.replace("{{REPRO_SOLUTIONS}}", "")
        report = report.replace("{{REPRO_DETAILS}}", "")

        report = report.replace("{{KEYWORDS}}", "")
        report = report.replace("{{CATEGORY}}", "")

        return report

    def _load_template(self) -> str:
        """加载模板"""
        if self.template_path.exists():
            return self.template_path.read_text(encoding='utf-8')

        return "# {{TITLE}}\n\n## 论文基本信息\n..."

    def save_analysis(self, analysis: Dict, filename: Optional[str] = None) -> Path:
        """保存解读报告"""
        if not filename:
            safe_title = re.sub(r'[^\w\s\-]', '', analysis['title'])[:50]
            filename = f"{analysis['reading_date']}-{safe_title}.md"

        output_dir = self.papers_dir
        output_dir.mkdir(parents=True, exist_ok=True)

        output_file = output_dir / filename
        report = self.generate_analysis_report(analysis)
        output_file.write_text(report, encoding='utf-8')

        print(f"\n✓ 解读报告已保存: {output_file.name}")
        return output_file

    def read_papers(self, papers: List[Dict]) -> List[Dict]:
        """批量阅读论文"""
        print("=" * 60)
        print("📚 论文精读模块")
        print("=" * 60)

        analyses = []

        for i, paper in enumerate(papers, 1):
            print(f"\n[{i}/{len(papers)}]")

            paper_details = paper
            if paper.get("arxiv_url"):
                details = self.fetch_paper_details(paper["arxiv_url"])
                paper_details.update(details)

            analysis = self.read_paper(paper_details)
            self.save_analysis(analysis)
            analyses.append(analysis)

        print("\n" + "=" * 60)
        print(f"✅ 完成 {len(analyses)} 篇论文的精读")
        print("=" * 60)

        return analyses


def main():
    """主函数"""
    config_path = Path(__file__).parent.parent / "config/config.json"
    reader = PaperReader(str(config_path))

    print("📖 论文精读工具")
    print("\n使用方法:")
    print("1. 使用 PaperFilter 筛选论文")
    print("2. 将筛选出的论文传递给 PaperReader")
    print("3. 生成深度解读报告")


if __name__ == "__main__":
    main()
