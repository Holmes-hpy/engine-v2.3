#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
知识整合模块
从论文解读中提取核心技术点，建立知识链接，更新知识库索引
"""

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List


class KnowledgeIntegrator:
    """知识整合器"""

    def __init__(self, config_path: str):
        self.config = self._load_config(config_path)
        self.base_path = Path(__file__).parent.parent.parent / self.config["general"]["base_path"]
        self.papers_dir = self.base_path / self.config["general"]["papers_dir"]
        self.permanent_dir = self.base_path / self.config["general"]["permanent_dir"]
        self.integration_config = self.config["knowledge_integration"]

    def _load_config(self, config_path: str) -> Dict:
        """加载配置"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"加载配置失败: {e}")
            return {}

    def extract_technical_points(self, analysis: Dict) -> List[Dict]:
        """从论文解读中提取技术要点"""
        print("\n🔍 提取技术要点...")

        technical_points = []

        point = {
            "title": f"来自论文：{analysis.get('title', '')[:50]}",
            "category": self._categorize_technique(analysis),
            "content": self._extract_core_technique(analysis),
            "source": analysis.get("arxiv_url", ""),
            "paper_title": analysis.get("title", ""),
            "extraction_date": datetime.now().strftime("%Y-%m-%d")
        }
        technical_points.append(point)

        print(f"   ✓ 提取了 {len(technical_points)} 个技术要点")
        return technical_points

    def _categorize_technique(self, analysis: Dict) -> str:
        """对技术进行分类"""
        title = analysis.get("title", "").lower()
        abstract = analysis.get("abstract", "")

        categories = {
            "模型架构": ["architecture", "model", "network", "transformer", "encoder", "decoder"],
            "训练技术": ["training", "fine-tuning", "pre-training", "optimization", "learning"],
            "推理优化": ["inference", "speed", "efficient", "quantization", "pruning"],
            "应用开发": ["application", "task", "benchmark", "downstream"],
            "评估指标": ["metric", "evaluation", "performance", "accuracy", "score"]
        }

        for category, keywords in categories.items():
            for keyword in keywords:
                if keyword in title:
                    return category

        return "基础理论"

    def _extract_core_technique(self, analysis: Dict) -> str:
        """提取核心技术"""
        technique = "# 核心技术\n\n"

        technique += f"## 来源\n\n"
        technique += f"- 论文标题：{analysis.get('title', '')}\n"
        technique += f"- 作者：{analysis.get('authors', '')}\n"
        technique += f"- 发表时间：{analysis.get('date', '')}\n"
        technique += f"- 论文链接：{analysis.get('arxiv_url', '')}\n\n"

        technique += "## 核心贡献\n\n"
        technique += analysis.get("contributions", "") + "\n\n"

        technique += "## 技术细节\n\n"
        technique += analysis.get("architecture", "") + "\n"
        technique += analysis.get("algorithm", "") + "\n\n"

        technique += "## 实际应用\n\n"
        technique += analysis.get("application_value", "") + "\n\n"

        return technique

    def create_knowledge_document(self, point: Dict) -> str:
        """创建知识文档"""
        doc = f"# {point['title']}\n\n"

        doc += f"**分类**：{point['category']}\n\n"
        doc += f"**来源**：{point['paper_title']}\n\n"
        doc += f"**链接**：{point['source']}\n\n"
        doc += f"**提取时间**：{point['extraction_date']}\n\n"
        doc += "---\n\n"

        doc += point["content"]

        doc += "\n\n---\n\n"
        doc += f"本知识条目从论文《{point['paper_title']}》中提取\n"

        return doc

    def save_knowledge_docs(self, technical_points: List[Dict]) -> List[Path]:
        """保存技术文档到知识库"""
        print("\n💾 保存知识文档...")

        saved_files = []

        for point in technical_points:
            category_dir = self.permanent_dir / point["category"]
            category_dir.mkdir(parents=True, exist_ok=True)

            safe_title = re.sub(r'[^\w\s\-]', '', point["title"])[:50]
            filename = f"{point['extraction_date']}-{safe_title}.md"
            file_path = category_dir / filename

            doc_content = self.create_knowledge_document(point)
            file_path.write_text(doc_content, encoding='utf-8')

            print(f"   ✓ 保存: {point['category']}/{filename}")
            saved_files.append(file_path)

        return saved_files

    def update_knowledge_index(self, technical_points: List[Dict],
                               paper_file: Path) -> None:
        """更新知识库索引"""
        print("\n📑 更新知识库索引...")

        index_file = self.base_path / "knowledge_index.json"

        index_data = {}
        if index_file.exists():
            try:
                index_data = json.loads(index_file.read_text(encoding='utf-8'))
            except Exception as e:
                print(f"   ⚠️ 读取索引失败: {e}")

        if "entries" not in index_data:
            index_data["entries"] = []

        for point in technical_points:
            entry = {
                "title": point["title"],
                "category": point["category"],
                "source_paper": point["paper_title"],
                "source_link": point["source"],
                "extraction_date": point["extraction_date"],
                "linked_paper": str(paper_file.relative_to(self.base_path))
            }
            index_data["entries"].append(entry)

        index_file.write_text(
            json.dumps(index_data, ensure_ascii=False, indent=2),
            encoding='utf-8'
        )

        print(f"   ✓ 索引已更新，共 {len(index_data['entries'])} 条知识")

    def create_bidirectional_links(self, paper_file: Path,
                                  knowledge_files: List[Path]) -> None:
        """创建双向链接"""
        print("\n🔗 创建双向链接...")

        paper_content = paper_file.read_text(encoding='utf-8')

        links_section = "\n\n---\n\n## 相关知识条目\n\n"
        for kf in knowledge_files:
            rel_path = str(kf.relative_to(self.base_path))
            link_text = f"- [[{kf.stem}]]({rel_path})"
            links_section += link_text + "\n"

        paper_content += links_section
        paper_file.write_text(paper_content, encoding='utf-8')

        for kf in knowledge_files:
            kf_content = kf.read_text(encoding='utf-8')

            links_section = "\n\n---\n\n## 相关论文解读\n\n"
            paper_rel_path = str(paper_file.relative_to(self.base_path))
            links_section += f"- [[{paper_file.stem}]]({paper_rel_path})\n"

            kf_content += links_section
            kf.write_text(kf_content, encoding='utf-8')

        print(f"   ✓ 已创建 {len(knowledge_files)} 个双向链接")

    def integrate_knowledge(self, analysis: Dict, paper_file: Path) -> List[Path]:
        """执行完整的知识整合流程"""
        print("=" * 60)
        print("🧠 知识整合模块")
        print("=" * 60)

        technical_points = self.extract_technical_points(analysis)

        knowledge_files = []
        if self.integration_config["create_knowledge_docs"]:
            knowledge_files = self.save_knowledge_docs(technical_points)

        if self.integration_config["update_index"]:
            self.update_knowledge_index(technical_points, paper_file)

        if self.integration_config["establish_links"] and knowledge_files:
            self.create_bidirectional_links(paper_file, knowledge_files)

        print("\n" + "=" * 60)
        print(f"✅ 知识整合完成，创建了 {len(knowledge_files)} 个知识文档")
        print("=" * 60)

        return knowledge_files

    def batch_integrate(self, analyses: List[Dict], paper_files: List[Path]) -> List[Path]:
        """批量整合多篇论文的知识"""
        print("=" * 60)
        print("🧠 批量知识整合")
        print("=" * 60)

        all_knowledge_files = []

        for analysis, paper_file in zip(analyses, paper_files):
            print(f"\n处理: {analysis.get('title', '')[:50]}...")

            knowledge_files = self.integrate_knowledge(analysis, paper_file)
            all_knowledge_files.extend(knowledge_files)

        print("\n" + "=" * 60)
        print(f"✅ 批量整合完成，共创建 {len(all_knowledge_files)} 个知识文档")
        print("=" * 60)

        return all_knowledge_files


def main():
    """主函数"""
    config_path = Path(__file__).parent.parent / "config/config.json"
    integrator = KnowledgeIntegrator(str(config_path))

    print("🧠 知识整合工具")
    print("\n使用方法:")
    print("1. 准备论文解读分析结果")
    print("2. 调用 integrator.integrate_knowledge(analysis, paper_file)")
    print("3. 自动提取、整合、更新索引")


if __name__ == "__main__":
    main()
