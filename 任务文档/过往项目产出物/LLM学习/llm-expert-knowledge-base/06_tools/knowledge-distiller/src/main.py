#!/usr/bin/env python3
"""
知识蒸馏工具 - 将原始信息转化为结构化知识文档
"""

import os
import sys
import json
import logging
from datetime import datetime
from pathlib import Path
import shutil
import re


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(str(Path(__file__).parent.parent / 'logs' / f'knowledge-distiller-{datetime.now().strftime("%Y%m%d")}.log')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class KnowledgeDistiller:
    def __init__(self, config_path=None):
        self.project_root = Path(__file__).parent.parent.parent.parent
        
        self.inbox_dir = self.project_root / '01_inbox'
        self.raw_dir = self.project_root / '02_raw'
        self.ai_wiki_dir = self.project_root / '03_ai_wiki'
        
        # 确保目录存在
        self.ai_wiki_dir.mkdir(exist_ok=True)
        
        self.config = self._load_config(config_path)
        
        self.categories = {
            '基础理论': ['数学', '理论', '框架', '原理', '基础', '算法', '数学基础', '理论基础'],
            '模型架构': ['Transformer', 'GPT', 'BERT', 'LLaMA', '模型', '架构', 'Decoder', 'Encoder'],
            '训练技术': ['预训练', '微调', 'RLHF', 'LoRA', '训练', 'SFT', '对齐', '指令微调'],
            '推理优化': ['量化', '蒸馏', '剪枝', '推理', '优化', '加速', '部署优化'],
            '应用开发': ['RAG', 'Agent', '多模态', '应用', '开发', '工具', '插件'],
            '部署工程': ['部署', '容器', '云服务', '工程', '运维', 'API', '服务'],
            '行业动态': ['趋势', '市场', '厂商', '动态', '新闻', '报告', '分析']
        }
        
        self.processed_count = 0
        self.generated_count = 0
        self.processed_files = []
        self.generated_docs = []
        self.failed_files = []
    
    def _load_config(self, config_path=None):
        if config_path is None:
            config_path = Path(__file__).parent.parent / 'config' / 'config.json'
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.warning(f"配置文件 {config_path} 未找到，使用默认配置")
            return self._get_default_config()
    
    def _get_default_config(self):
        return {
            "max_content_length": 10000,
            "min_content_length": 100,
            "skip_keywords": ["每日信息简报", "已处理", "知识蒸馏报告"]
        }
    
    def _scan_unprocessed_files(self):
        """扫描inbox目录，找出未处理的文件"""
        unprocessed = []
        
        if not self.inbox_dir.exists():
            logger.warning(f"目录 {self.inbox_dir} 不存在")
            return []
        
        for file_path in self.inbox_dir.glob('*.md'):
            filename = file_path.name
            
            skip = False
            for keyword in self.config.get('skip_keywords', []):
                if keyword in filename:
                    skip = True
                    break
            
            if not skip:
                unprocessed.append(file_path)
        
        logger.info(f"发现 {len(unprocessed)} 个未处理文件")
        return unprocessed
    
    def _read_file(self, file_path):
        """读取文件内容"""
        try:
            content = file_path.read_text(encoding='utf-8')
            if len(content) < self.config.get('min_content_length', 100):
                logger.warning(f"文件内容过短，跳过: {file_path.name}")
                return None
            return content[:self.config.get('max_content_length', 10000)]
        except Exception as e:
            logger.error(f"读取文件失败 {file_path}: {e}")
            return None
    
    def _extract_metadata(self, content):
        """从内容中提取元数据"""
        metadata = {
            'title': '',
            'source': '',
            'publish_time': '',
            'author': ''
        }
        
        lines = content.split('\n')
        in_header = True
        
        for line in lines[:20]:
            if line.startswith('# '):
                metadata['title'] = line[2:].strip()
            
            if line.startswith('- **来源**:'):
                metadata['source'] = line.replace('- **来源**:', '').strip()
            
            if line.startswith('- **链接**:'):
                metadata['source'] = line.replace('- **链接**:', '').strip()
            
            if line.startswith('- **发布时间**:'):
                metadata['publish_time'] = line.replace('- **发布时间**:', '').strip()
            
            if line.startswith('- **作者**:'):
                metadata['author'] = line.replace('- **作者**:', '').strip()
            
            if line.startswith('## '):
                in_header = False
        
        return metadata
    
    def _classify_topic(self, title, content):
        """根据标题和内容分类"""
        text = (title + content).lower()
        
        for category, keywords in self.categories.items():
            for keyword in keywords:
                if keyword.lower() in text:
                    return category
        
        return '行业动态'
    
    def _determine_knowledge_level(self, content):
        """判断知识等级"""
        advanced_terms = ['证明', '定理', '推导', '复杂性', '收敛', '理论分析', '数学模型']
        intermediate_terms = ['实现', '代码', '方法', '技术', '实验', '评估', '性能']
        
        text = content.lower()
        
        advanced_count = sum(1 for term in advanced_terms if term.lower() in text)
        intermediate_count = sum(1 for term in intermediate_terms if term.lower() in text)
        
        if advanced_count >= 2:
            return '高级'
        elif intermediate_count >= 2:
            return '中级'
        else:
            return '入门'
    
    def _generate_structured_doc(self, metadata, content):
        """生成结构化知识文档"""
        today = datetime.now().strftime('%Y-%m-%d')
        
        knowledge_level = self._determine_knowledge_level(content)
        
        doc = f"# {metadata.get('title', '未知标题')}\n\n"
        
        doc += "## 基本信息\n"
        doc += f"- **来源**: {metadata.get('source', '')}\n"
        doc += f"- **发布时间**: {metadata.get('publish_time', '')}\n"
        doc += f"- **作者/机构**: {metadata.get('author', '')}\n"
        doc += f"- **知识等级**: {knowledge_level}\n"
        doc += f"- **处理时间**: {today}\n\n"
        
        doc += "## 核心问题\n"
        doc += self._extract_core_question(content) + "\n\n"
        
        doc += "## 核心解决方案\n"
        doc += self._extract_solution(content) + "\n\n"
        
        doc += "## 关键技术点\n"
        tech_points = self._extract_tech_points(content)
        for i, point in enumerate(tech_points, 1):
            doc += f"{i}. {point}\n"
        doc += "\n"
        
        doc += "## 实验结果与结论\n"
        doc += "- **主要实验结果**: \n"
        doc += "- **核心结论**: \n\n"
        
        doc += "## 优势与局限性\n"
        doc += "### 优势\n"
        doc += "- \n"
        doc += "- \n\n"
        doc += "### 局限性\n"
        doc += "- \n"
        doc += "- \n\n"
        
        doc += "## 适用场景\n"
        doc += "- \n"
        doc += "- \n\n"
        
        doc += "## 相关知识\n"
        related = self._find_related_knowledge(content)
        for rel in related:
            doc += f"- [[{rel}]]\n"
        doc += "\n"
        
        doc += "## 验证状态\n"
        doc += "- **验证人**: AI自动提取\n"
        doc += f"- **验证时间**: {today}\n"
        doc += "- **验证状态**: 待人工验证\n"
        
        return doc
    
    def _extract_core_question(self, content):
        """提取核心问题"""
        patterns = [
            r'(解决|解决了|解决的|针对|面对).*?(问题|挑战|难题)',
            r'(旨在|目的是|致力于).*?(研究|解决|探索)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                return match.group(0)
        
        return "本文探讨了大模型相关的技术问题和解决方案。"
    
    def _extract_solution(self, content):
        """提取核心解决方案"""
        patterns = [
            r'(提出|提出了|开发了|设计了|采用).*?(方法|技术|模型|框架)',
            r'(基于|通过|利用).*?(实现|解决|改进)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                return match.group(0)
        
        return "作者提出了相应的技术解决方案来应对上述问题。"
    
    def _extract_tech_points(self, content):
        """提取关键技术点"""
        tech_keywords = [
            'Transformer', 'GPT', 'BERT', 'LLaMA', '预训练', '微调',
            'RLHF', 'LoRA', '量化', '蒸馏', '剪枝', 'RAG', 'Agent',
            '多模态', '注意力机制', '自监督学习', '对比学习', '强化学习'
        ]
        
        found_points = []
        for keyword in tech_keywords:
            if keyword in content:
                found_points.append(f"{keyword}：相关技术内容")
        
        if not found_points:
            found_points = ['核心技术点1：需要人工补充', '核心技术点2：需要人工补充']
        
        return found_points[:3]
    
    def _find_related_knowledge(self, content):
        """查找相关知识"""
        related_map = {
            'Transformer': 'transformer_architecture',
            'GPT': 'gpt_model_family',
            'BERT': 'bert_model',
            'LLaMA': 'llama_model',
            '预训练': 'pre_training',
            '微调': 'fine_tuning',
            'RLHF': 'rlhf_training',
            'LoRA': 'lora_adaptation',
            'RAG': 'retrieval_augmented_generation',
            '量化': 'model_quantization',
            '蒸馏': 'knowledge_distillation'
        }
        
        related = []
        for keyword, filename in related_map.items():
            if keyword in content:
                related.append(filename)
        
        return related[:3]
    
    def _save_to_wiki(self, doc, title, category):
        """保存到AI Wiki目录"""
        safe_title = re.sub(r'[\\/*?:"<>|]', '_', title)[:50]
        filename = f"{safe_title}.md"
        category_dir = self.ai_wiki_dir / category
        
        category_dir.mkdir(exist_ok=True)
        filepath = category_dir / filename
        
        filepath.write_text(doc, encoding='utf-8')
        logger.info(f"保存知识文档: {filepath}")
        
        return str(filepath)
    
    def _move_to_raw(self, source_path):
        """移动到raw目录并添加已处理标记"""
        new_name = f"已处理-{source_path.name}"
        dest_path = self.raw_dir / new_name
        
        shutil.move(str(source_path), str(dest_path))
        logger.info(f"移动文件: {source_path} -> {dest_path}")
    
    def _generate_report(self):
        """生成处理报告"""
        today = datetime.now().strftime('%Y-%m-%d')
        report_path = self.ai_wiki_dir / f"{today}-知识蒸馏报告.md"
        
        report = f"# 知识蒸馏处理报告 - {today}\n\n"
        report += f"- **处理时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        report += f"- **处理文件数**: {self.processed_count}\n"
        report += f"- **生成知识文档数**: {self.generated_count}\n"
        report += f"- **失败文件数**: {len(self.failed_files)}\n\n"
        
        if self.failed_files:
            report += "## 失败文件\n"
            for f in self.failed_files:
                report += f"- {f}\n"
            report += "\n"
        
        report += "## 生成的知识文档\n"
        report += "| 分类 | 标题 |\n"
        report += "|------|------|\n"
        for doc in self.generated_docs:
            report += f"| {doc['category']} | {doc['title']} |\n"
        
        report_path.write_text(report, encoding='utf-8')
        logger.info(f"生成处理报告: {report_path}")
        
        return str(report_path)
    
    def run(self):
        """运行知识蒸馏"""
        logger.info("=" * 50)
        logger.info("开始知识蒸馏")
        logger.info("=" * 50)
        
        unprocessed_files = self._scan_unprocessed_files()
        
        for file_path in unprocessed_files:
            logger.info(f"处理文件: {file_path.name}")
            
            try:
                content = self._read_file(file_path)
                if not content:
                    continue
                
                metadata = self._extract_metadata(content)
                category = self._classify_topic(metadata['title'], content)
                doc = self._generate_structured_doc(metadata, content)
                
                saved_path = self._save_to_wiki(doc, metadata['title'], category)
                self._move_to_raw(file_path)
                
                self.processed_count += 1
                self.generated_count += 1
                self.processed_files.append(file_path.name)
                self.generated_docs.append({
                    'title': metadata['title'],
                    'category': category,
                    'path': saved_path
                })
                
                logger.info(f"成功处理: {file_path.name} -> {category}")
                
            except Exception as e:
                logger.error(f"处理文件失败 {file_path.name}: {e}")
                self.failed_files.append(file_path.name)
        
        report_path = self._generate_report()
        
        logger.info("=" * 50)
        logger.info("知识蒸馏完成")
        logger.info("=" * 50)
        
        return report_path


def main():
    non_interactive = len(sys.argv) > 1 and sys.argv[1] == '--non-interactive'
    
    distiller = KnowledgeDistiller()
    report_path = distiller.run()
    
    print("\n" + "=" * 50)
    print("知识蒸馏完成！")
    print(f"处理文件数: {distiller.processed_count}")
    print(f"生成知识文档数: {distiller.generated_count}")
    print(f"失败文件数: {len(distiller.failed_files)}")
    print(f"处理报告已保存至: {report_path}")
    print("=" * 50)
    
    if not non_interactive:
        response = input("\n是否需要进行知识质量审计？(y/n): ").strip().lower()
        if response == 'y':
            print("\n知识质量审计功能开发中...")


if __name__ == '__main__':
    main()

