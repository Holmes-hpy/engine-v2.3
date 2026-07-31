#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
知识质量审计工具 - 增强版
核心使命：作为大模型知识库的"质量守门人"，严格审核所有AI生成的知识内容
"""

import os
import sys
import json
import time
import re
import shutil
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from collections import Counter, defaultdict

try:
    from tqdm import tqdm
    HAS_TQDM = True
except ImportError:
    HAS_TQDM = False


# ==================== 领域关键词库 ====================
TECH_KEYWORDS = {
    "模型架构": ["Transformer", "GPT", "BERT", "LLaMA", "RWKV", "Attention", "注意力机制",
                "Encoder", "Decoder", "MLP", "RNN", "LSTM", "Seq2Seq", "MoE", "Mixtral"],
    "训练技术": ["预训练", "微调", "Fine-tune", "LoRA", "QLoRA", "RLHF", "PPO", "DPO",
                "梯度下降", "反向传播", "Adam", "AdamW", "学习率", "Batch Normalization",
                "Dropout", "Prompt Engineering", "Instruction Tuning"],
    "推理优化": ["量化", "Quantization", "GPTQ", "AWQ", "蒸馏", "剪枝", "KV Cache",
                "推理加速", "Flash Attention", "vLLM", "TensorRT", "ONNX", "FP8", "FP16"],
    "应用开发": ["RAG", "Agent", "LangChain", "LlamaIndex", "应用", "开发", "工具",
                "API", "Plugin", "Tool", "Embedding", "向量检索", "语义搜索"],
    "部署工程": ["部署", "容器", "Docker", "Kubernetes", "K8s", "云", "服务", "生产",
                "GPU", "CUDA", "推理服务", "模型服务化"],
    "数据处理": ["数据清洗", "Tokenization", "分词", "数据集", "预处理", "后处理",
                "数据增强", "数据混合"],
    "评估理论": ["评估", "Benchmark", "MMLU", "HumanEval", "准确率", "困惑度", "BLEU",
                "ROUGE", "Perplexity", "Alignment"],
    "行业动态": ["趋势", "市场", "产业", "动态", "报告", "发布", "发布了", "宣布", "融资"]
}

LLM_RELATED_KEYWORDS = [
    "大模型", "LLM", "GPT", "Transformer", "BERT", "LLaMA", "预训练", "微调",
    "量化", "推理", "Agent", "RAG", "Claude", "Gemini", "GPT-4", "GPT-3",
    "ChatGPT", "语言模型", "神经网络", "深度学习", "机器学习", "AI", "人工智能",
    "LoRA", "RLHF", "Prompt", "Embedding", "Token", "Attention", "注意力"
]

TECHNICAL_ACCURACY_PATTERNS = [
    r"\d+\s*%",  # 百分比数据
    r"\d+\.\d+",  # 小数
    r"\d{4}[-年]\d{1,2}[-月]\d{1,2}",  # 日期格式
    r"[A-Z][a-z]+[A-Z]?[A-Za-z]*",  # 专有名词（如Transformer）
    r"https?://\S+",  # 参考链接
]

RED_FLAG_PATTERNS = [
    r"可能(是|有|存在)?",
    r"也许",
    r"大概",
    r"或许",
    r"我觉得",
    r"我认为",
    r"不确定",
    r"有待验证",
    r"需要确认",
    r"未验证",
    r"TODO",
    r"待补充",
    r"待完善"
]


class KnowledgeAuditor:
    """知识质量审计器 - 增强版"""

    def __init__(self, config_path: str, full_audit: bool = False):
        """初始化审计器"""
        self.full_audit_mode = full_audit
        self.config = self._load_config(config_path)
        self.base_path = Path(__file__).parent.parent / self.config["general"]["base_path"]
        self.base_path = self.base_path.resolve()

        # 确定扫描范围
        self.audit_dirs = self._get_audit_dirs()

        # 审计输出目录
        self.output_audit_dir = self.base_path / "08_audit"
        self.rejected_dir = self.base_path / "99_archive" / "rejected"
        self.pipeline_log_dir = self.base_path / "06_tools" / "knowledge-auditor" / "logs"

        self._ensure_directories()

        # 状态文件
        self.state_file = Path(__file__).parent.parent / "state" / "audit_state.json"
        self.audit_state = self._load_audit_state()

        # 统计数据
        self.stats = {
            "total_scanned": 0,
            "total_processed": 0,
            "errors": 0,
            "start_time": datetime.now(),
            "category_counts": {"优秀": 0, "合格": 0, "待修正": 0, "不合格": 0},
            "dir_stats": defaultdict(lambda: {"count": 0, "avg_score": 0.0, "scores": []}),
            "dimension_avg": defaultdict(list),
        }

        # 错误日志
        self.error_log = []

        print("=" * 70)
        print("📚 知识质量审计工具 - 增强版")
        print(f"⏰ 启动时间: {self.stats['start_time'].strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"📁 项目根目录: {self.base_path}")
        print(f"📁 扫描目录: {', '.join(d['name'] for d in self.audit_dirs)}")
        print("=" * 70)

    def _get_audit_dirs(self) -> List[Dict]:
        """获取审计目录列表"""
        dirs = []

        # 03_ai_wiki
        wiki_path = self.base_path / "03_ai_wiki"
        if wiki_path.exists():
            dirs.append({"name": "03_ai_wiki", "path": wiki_path, "type": "wiki"})

        # 04_permanent
        perm_path = self.base_path / "04_permanent"
        if perm_path.exists():
            dirs.append({"name": "04_permanent", "path": perm_path, "type": "permanent"})

        # 增强模式：扫描其他相关目录
        if self.full_audit_mode:
            inbox_path = self.base_path / "01_inbox"
            if inbox_path.exists():
                dirs.append({"name": "01_inbox", "path": inbox_path, "type": "inbox"})

            raw_path = self.base_path / "02_raw"
            if raw_path.exists():
                dirs.append({"name": "02_raw", "path": raw_path, "type": "raw"})

            papers_path = self.base_path / "05_papers"
            if papers_path.exists():
                dirs.append({"name": "05_papers", "path": papers_path, "type": "papers"})

            tools_wiki = self.base_path / "06_tools" / "03_ai_wiki"
            if tools_wiki.exists():
                dirs.append({"name": "06_tools/03_ai_wiki", "path": tools_wiki, "type": "wiki"})

            case_path = self.base_path / "07_case_studies"
            if case_path.exists():
                dirs.append({"name": "07_case_studies", "path": case_path, "type": "cases"})

        if not dirs:
            fallback = Path(__file__).parent.parent.parent
            for sub in ["01_inbox", "02_raw", "03_ai_wiki", "04_permanent", "05_papers", "07_case_studies"]:
                p = fallback / sub
                if p.exists():
                    dirs.append({"name": sub, "path": p, "type": sub})
            self.base_path = fallback
            self.output_audit_dir = self.base_path / "08_audit"
            self.rejected_dir = self.base_path / "99_archive" / "rejected"

        return dirs

    def _load_config(self, config_path: str) -> Dict:
        """加载配置文件"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠️  加载配置失败，使用默认配置: {e}")
            return self._get_default_config()

    def _get_default_config(self) -> Dict:
        """获取默认配置"""
        return {
            "general": {"base_path": "../../", "ai_wiki_dir": "03_ai_wiki",
                        "permanent_dir": "04_permanent", "audit_dir": "08_audit",
                        "rejected_dir": "99_archive/rejected"},
            "validation": {"audit_threshold": 70, "excellent_threshold": 85,
                          "need_correction_threshold": 50, "exclude_audited_in_hours": 24},
            "scoring": {
                "weights": {"accuracy": 0.25, "completeness": 0.15, "consistency": 0.20,
                           "timeliness": 0.15, "relevance": 0.10, "comprehensibility": 0.15},
                "dimensions": {
                    "accuracy": {"name": "准确性", "description": "事实是否准确，数据是否可靠"},
                    "completeness": {"name": "完整性", "description": "是否涵盖核心要点"},
                    "consistency": {"name": "一致性", "description": "格式与表述是否一致"},
                    "timeliness": {"name": "时效性", "description": "信息是否最新"},
                    "relevance": {"name": "相关性", "description": "与大模型领域的相关程度"},
                    "comprehensibility": {"name": "可理解性", "description": "表述是否清晰易懂"}
                }
            }
        }

    def _load_audit_state(self) -> Dict:
        """加载审计状态"""
        try:
            if self.state_file.exists():
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception:
            pass
        return {"last_audit": None, "audited_files": {}}

    def _save_audit_state(self):
        """保存审计状态"""
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.state_file, 'w', encoding='utf-8') as f:
            json.dump(self.audit_state, f, ensure_ascii=False, indent=2)

    def _ensure_directories(self):
        """确保必要目录存在"""
        self.rejected_dir.mkdir(parents=True, exist_ok=True)
        self.output_audit_dir.mkdir(parents=True, exist_ok=True)
        self.pipeline_log_dir.mkdir(parents=True, exist_ok=True)

    def find_all_documents(self) -> List[Tuple[str, Path]]:
        """扫描所有知识文档"""
        print("\n🔍 全面审计模式：扫描所有知识文档...")
        all_docs = []
        for dir_info in self.audit_dirs:
            dir_path = dir_info["path"]
            dir_name = dir_info["name"]
            count = 0
            for md_file in sorted(dir_path.rglob("*.md")):
                filename = str(md_file)
                if ".context.md" in filename:
                    continue
                if "审计报告" in filename:
                    continue
                if "99_archive" in str(md_file):
                    continue
                all_docs.append((dir_name, md_file))
                count += 1
            print(f"   📂 {dir_name}: {count} 篇")

        print(f"   {'─' * 50}")
        print(f"   📊 总计: {len(all_docs)} 篇知识文档")
        self.stats["total_scanned"] = len(all_docs)
        return all_docs

    def analyze_document(self, dir_name: str, file_path: Path) -> Optional[Dict]:
        """分析文档并生成评分"""
        try:
            content = file_path.read_text(encoding='utf-8', errors='replace')
            file_size = file_path.stat().st_size
            file_mtime = datetime.fromtimestamp(file_path.stat().st_mtime)

            scores = self._calculate_scores_enhanced(content, file_path, file_size, file_mtime)
            weights = self.config["scoring"]["weights"]
            total_score = sum(scores[key] * weights[key] for key in weights)
            category = self._classify_document(total_score)
            domains = self._identify_domains(content)

            return {
                "dir_name": dir_name,
                "file_path": file_path,
                "file_name": file_path.name,
                "relative_path": str(file_path.relative_to(self.base_path)),
                "file_size": file_size,
                "file_mtime": file_mtime,
                "scores": scores,
                "total_score": round(total_score, 2),
                "category": category,
                "domains": domains,
                "word_count": len(content),
                "line_count": len(content.splitlines()),
                "section_count": self._count_sections(content),
                "has_code_block": "```" in content,
                "has_link": bool(re.search(r"https?://", content)),
                "has_table": bool(re.search(r"^\s*\|.*\|", content, re.MULTILINE)),
                "has_list": bool(re.search(r"^\s*[-*]\s", content, re.MULTILINE)),
                "has_image": "![" in content,
                "issues": self._detect_issues(content),
                "red_flags": self._detect_red_flags(content),
            }
        except Exception as e:
            error_msg = f"{datetime.now().strftime('%H:%M:%S')} - 分析失败 {file_path}: {e}"
            self.error_log.append(error_msg)
            self.stats["errors"] += 1
            return None

    def _calculate_scores_enhanced(self, content: str, file_path: Path,
                                    file_size: int, file_mtime: datetime) -> Dict[str, float]:
        """增强版六维评分计算"""
        return {
            "accuracy": self._check_accuracy(content, file_path),
            "completeness": self._check_completeness(content),
            "consistency": self._check_consistency(content),
            "timeliness": self._check_timeliness(content, file_mtime),
            "relevance": self._check_relevance(content),
            "comprehensibility": self._check_comprehensibility(content),
        }

    def _check_accuracy(self, content: str, file_path: Path) -> float:
        """检查准确性 - 增强版"""
        score = 40.0

        data_pattern_hits = 0
        for pattern in TECHNICAL_ACCURACY_PATTERNS:
            hits = len(re.findall(pattern, content))
            if hits > 0:
                data_pattern_hits += min(hits, 5)
        if data_pattern_hits > 0:
            score += min(data_pattern_hits * 4, 20)

        tech_terms_found = set()
        for category, keywords in TECH_KEYWORDS.items():
            for kw in keywords:
                if kw.lower() in content.lower():
                    tech_terms_found.add(kw)
        score += min(len(tech_terms_found) * 1.2, 20)

        link_count = len(re.findall(r"https?://[^\s)]+", content))
        if link_count > 0:
            score += min(link_count * 2, 10)

        if "参考" in content or "引用" in content or "来源" in content or "参考文献" in content:
            score += 5

        for flag in ["需要人工验证", "需要验证", "待验证", "未验证"]:
            if flag in content:
                score -= 8

        uncertain_count = 0
        for pattern in RED_FLAG_PATTERNS:
            if re.search(pattern, content, re.IGNORECASE):
                uncertain_count += 1
        if uncertain_count > 0:
            score -= min(uncertain_count * 3, 15)

        if "```" in content or re.search(r"\$\$.*?\$\$", content, re.DOTALL):
            score += 5

        if re.search(r"\d{4}[-年]\d{1,2}[-月]\d{1,2}", content) or re.search(r"v?\d+\.\d+", content):
            score += 3

        return min(max(score, 10), 100)

    def _check_completeness(self, content: str) -> float:
        """检查完整性 - 增强版"""
        score = 30.0
        word_count = len(content)
        line_count = len(content.splitlines())

        if word_count < 200:
            score += 2
        elif word_count < 500:
            score += 8
        elif word_count < 1000:
            score += 14
        elif word_count < 2000:
            score += 18
        else:
            score += 20

        headers = re.findall(r"^#{1,6}\s", content, re.MULTILINE)
        if len(headers) >= 5:
            score += 20
        elif len(headers) >= 3:
            score += 15
        elif len(headers) >= 2:
            score += 10
        elif len(headers) >= 1:
            score += 5

        diversity_score = 0
        if "```" in content:
            diversity_score += 5
        if re.search(r"^\s*\|.*\|", content, re.MULTILINE):
            diversity_score += 5
        if re.search(r"^\s*[-*]\s", content, re.MULTILINE):
            diversity_score += 5
        if re.search(r"^\d+\.\s", content, re.MULTILINE):
            diversity_score += 5
        if re.search(r"> ", content):
            diversity_score += 3
        if re.search(r"!\[.*?\]", content):
            diversity_score += 2

        if any(kw in content for kw in ["案例", "示例", "例子", "举例"]):
            diversity_score += 3
        if any(kw in content for kw in ["总结", "小结", "结论", "要点"]):
            diversity_score += 3
        if any(kw in content for kw in ["背景", "介绍", "简介", "概述"]):
            diversity_score += 3

        score += min(diversity_score, 25)

        if line_count > 0:
            avg_line_length = word_count / line_count
            if avg_line_length > 30:
                score += 10
            elif avg_line_length > 20:
                score += 7
            elif avg_line_length > 10:
                score += 4
            else:
                score += 1

        section_keywords = ["背景", "介绍", "原理", "方法", "实现", "应用",
                           "优势", "缺点", "限制", "问题", "总结", "结论",
                           "参考", "链接", "文献"]
        found_sections = 0
        for kw in section_keywords:
            if re.search(r"^#{1,6}\s.*" + kw, content, re.MULTILINE):
                found_sections += 1
        score += min(found_sections * 2, 10)

        return min(max(score, 10), 100)

    def _check_consistency(self, content: str) -> float:
        """检查一致性 - 增强版"""
        score = 55.0

        md_score = 0
        if re.search(r"^#{1,6}\s+\S", content, re.MULTILINE):
            md_score += 5
        if re.search(r"^\s*[-*]\s+\S", content, re.MULTILINE):
            md_score += 3
        if re.search(r"\[.*?\]\(.*?\)", content):
            md_score += 3
        if re.search(r"\*\*.*?\*\*", content):
            md_score += 2
        if re.search(r"`[^`]+`", content):
            md_score += 2
        score += min(md_score, 15)

        term_pairs = [
            ("大模型", "LLM"), ("大模型", "语言模型"),
            ("微调", "Fine-tune"), ("量化", "Quantization"), ("注意力", "Attention"),
        ]
        consistency_issues = 0
        for term_a, term_b in term_pairs:
            a_found = term_a in content
            b_found = term_b in content
            if a_found and b_found:
                paragraphs = re.split(r"\n\s*\n", content)
                for para in paragraphs:
                    if term_a in para and term_b in para:
                        consistency_issues += 1
                        break
        score -= min(consistency_issues * 3, 8)

        contradiction_patterns = [
            (r"支持", r"不支持"), (r"能够", r"不能"), (r"可以", r"不可以"),
        ]
        contradiction_count = 0
        for pat_pos, pat_neg in contradiction_patterns:
            pos_count = len(re.findall(pat_pos, content))
            neg_count = len(re.findall(pat_neg, content))
            if pos_count > 0 and neg_count > 0:
                contradiction_count += 1
        if contradiction_count == 0:
            score += 8
        else:
            score -= contradiction_count * 3

        dates_found = re.findall(r"(\d{4})[-年](\d{1,2})", content)
        if len(dates_found) > 1:
            years = set(int(d[0]) for d in dates_found)
            if len(years) <= 2:
                score += 5
            else:
                score += 2
        elif len(dates_found) == 1:
            score += 3

        lines = content.splitlines()
        header_levels = []
        for line in lines:
            m = re.match(r"^(#{1,6})\s", line)
            if m:
                header_levels.append(len(m.group(1)))
        if len(header_levels) > 1:
            jumps = sum(1 for i in range(1, len(header_levels))
                       if abs(header_levels[i] - header_levels[i - 1]) > 2)
            if jumps == 0:
                score += 10
            else:
                score += 5
        elif len(header_levels) == 1:
            score += 5

        list_lines = [l.strip() for l in lines if re.match(r"^\s*[-*]\s", l)]
        if len(list_lines) > 0:
            dash_count = sum(1 for l in list_lines if l.startswith("-"))
            star_count = sum(1 for l in list_lines if l.startswith("*"))
            if dash_count == 0 or star_count == 0:
                score += 5
            else:
                score += 2

        return min(max(score, 10), 100)

    def _check_timeliness(self, content: str, file_mtime: datetime) -> float:
        """检查时效性 - 增强版"""
        score = 40.0
        now = datetime.now()

        time_diff = now - file_mtime
        if time_diff.days <= 7:
            score += 25
        elif time_diff.days <= 30:
            score += 20
        elif time_diff.days <= 90:
            score += 15
        elif time_diff.days <= 180:
            score += 10
        elif time_diff.days <= 365:
            score += 5

        current_year = now.year
        recent_dates = re.findall(r"(20\d{2})[-年月日/](\d{1,2})", content)
        if recent_dates:
            year_scores = 0
            for year_str, _ in recent_dates:
                year = int(year_str)
                year_diff = current_year - year
                if year_diff == 0:
                    year_scores += 10
                elif year_diff == 1:
                    year_scores += 7
                elif year_diff <= 3:
                    year_scores += 4
                elif year_diff <= 5:
                    year_scores += 1
            score += min(year_scores, 25)

        current_hot_topics = [
            "GPT-4", "GPT-5", "Claude", "Claude 3", "Claude 4",
            "Gemini", "Grok", "Qwen", "DeepSeek", "LLaMA 3", "LLaMA 4",
            "多模态", "具身智能", "Agent", "智能体",
            "RAG", "Sora", "视频生成", "图像生成",
            "推理加速", "vLLM", "量化", "FP8",
            "MoE", "混合专家", str(current_year), f"{current_year}年",
            "最新", "近期", "最近", "当前",
        ]
        hot_count = sum(1 for topic in current_hot_topics if topic in content)
        score += min(hot_count * 3, 15)

        outdated_terms = ["GPT-2", "BERT-base", "ELMo", "Word2Vec", "2018", "2019", "2020"]
        outdated_count = sum(1 for term in outdated_terms if term in content)
        if outdated_count > 0:
            score -= min(outdated_count * 1, 5)

        version_patterns = re.findall(r"v?(\d+)\.(\d+)(?:\.(\d+))?", content)
        if version_patterns:
            recent_versions = sum(1 for v in version_patterns if int(v[0]) >= 2)
            if recent_versions > 0:
                score += min(recent_versions * 2, 5)

        return min(max(score, 10), 100)

    def _check_relevance(self, content: str) -> float:
        """检查相关性 - 增强版"""
        score = 20.0

        llm_hits = 0
        found_keywords = set()
        content_lower = content.lower()
        for keyword in LLM_RELATED_KEYWORDS:
            kw_lower = keyword.lower()
            if kw_lower in content_lower:
                llm_hits += content_lower.count(kw_lower)
                found_keywords.add(keyword)

        score += min(len(found_keywords) * 3, 40)

        word_count = max(len(content), 100)
        density = llm_hits / word_count * 1000
        if density >= 10:
            score += 20
        elif density >= 5:
            score += 15
        elif density >= 2:
            score += 10
        elif density >= 1:
            score += 5

        domain_hits = 0
        for category, keywords in TECH_KEYWORDS.items():
            for kw in keywords:
                if kw.lower() in content_lower:
                    domain_hits += 1
                    break
        score += min(domain_hits * 4, 20)

        deep_terms = ["梯度", "损失函数", "反向传播", "优化器", "学习率调度",
                     "注意力机制", "位置编码", "残差连接", "层归一化",
                     "Dropout", "正则化", "泛化", "过拟合", "欠拟合",
                     "蒸馏", "剪枝", "量化", "知识蒸馏"]
        deep_count = sum(1 for term in deep_terms if term in content)
        score += min(deep_count * 2, 10)

        return min(max(score, 10), 100)

    def _check_comprehensibility(self, content: str) -> float:
        """检查可理解性 - 增强版"""
        score = 40.0

        paragraphs = [p for p in re.split(r"\n\s*\n", content) if p.strip()]
        if len(paragraphs) >= 10:
            score += 15
        elif len(paragraphs) >= 5:
            score += 12
        elif len(paragraphs) >= 3:
            score += 8
        elif len(paragraphs) >= 2:
            score += 4

        explanation_markers = [
            "是指", "指的是", "即", "是", "指", "就是",
            "简单来说", "简单地说", "换句话说",
            "例如", "比如", "举例来说",
            "具体来说", "具体地说", "详细来说",
            "这意味着", "也就是说",
            "定义", "概念", "含义", "说明", "解释", "表示",
        ]
        explanation_count = sum(1 for marker in explanation_markers if marker in content)
        score += min(explanation_count * 2, 20)

        definition_patterns = [
            r"[A-Z][A-Za-z]+\s*是", r"[A-Z][A-Za-z]+\s*指",
            r"[一二三四五六七八九十]+、\s*\S+\s*(是|指|即)",
            r"所谓\s*\S+", r"什么是\s*\S+",
        ]
        def_count = sum(1 for pat in definition_patterns if re.search(pat, content))
        score += min(def_count * 2, 10)

        sentences = re.split(r"[。！？.!?]", content)
        sentences = [s for s in sentences if len(s.strip()) > 5]
        if sentences:
            avg_sentence_len = sum(len(s) for s in sentences) / len(sentences)
            if 15 <= avg_sentence_len <= 60:
                score += 10
            elif 10 <= avg_sentence_len <= 80:
                score += 6
            else:
                score += 2

        if "**" in content or "__" in content:
            score += 2
        if "*" in content or "_" in content:
            score += 1
        if "`" in content:
            score += 2

        structure_words = ["首先", "其次", "然后", "接着", "最后", "总结",
                           "第一", "第二", "第三", "第四", "第五",
                           "一方面", "另一方面", "此外", "另外", "同时"]
        struct_count = sum(1 for word in structure_words if word in content)
        score += min(struct_count * 1, 5)

        return min(max(score, 10), 100)

    def _count_sections(self, content: str) -> int:
        """统计章节数"""
        return len(re.findall(r"^#{1,6}\s", content, re.MULTILINE))

    def _identify_domains(self, content: str) -> List[str]:
        """识别文档的主要技术领域"""
        domains = []
        content_lower = content.lower()
        for category, keywords in TECH_KEYWORDS.items():
            hits = sum(1 for kw in keywords if kw.lower() in content_lower)
            if hits >= 2:
                domains.append(category)
        if not domains:
            domains.append("其他/通用")
        return domains

    def _detect_issues(self, content: str) -> List[str]:
        """检测文档存在的问题"""
        issues = []
        word_count = len(content)

        if word_count < 200:
            issues.append("内容过短，信息量不足")

        if not re.search(r"^#{1,6}\s", content, re.MULTILINE):
            issues.append("缺少标题结构")

        if "```" not in content and word_count > 500:
            if any(kw in content for kw in ["代码", "实现", "示例"]):
                issues.append("提到代码但无代码块示例")

        if not re.search(r"https?://", content) and word_count > 500:
            issues.append("缺少参考链接和引用来源")

        uncertain_terms = ["可能", "也许", "大概", "或许", "不确定"]
        if sum(content.count(term) for term in uncertain_terms) > 5:
            issues.append("存在较多不确定表述，建议补充验证")

        if "需要人工验证" in content or "待验证" in content:
            issues.append("标注有需要人工验证的内容")

        return issues

    def _detect_red_flags(self, content: str) -> List[str]:
        """检测红色警示标记"""
        red_flags = []
        for pattern in RED_FLAG_PATTERNS:
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                red_flags.append(f"{matches[0].strip()} (x{len(matches)})")
        return red_flags[:5]

    def _classify_document(self, total_score: float) -> str:
        """根据得分分类文档"""
        th = self.config["validation"]
        if total_score >= th["excellent_threshold"]:
            return "优秀"
        elif total_score >= th["audit_threshold"]:
            return "合格"
        elif total_score >= th["need_correction_threshold"]:
            return "待修正"
        else:
            return "不合格"

    def run(self, max_docs: Optional[int] = None):
        """运行完整审计流程"""
        print(f"\n🚀 开始知识质量审计")
        print(f"   模式: {'全面审计' if self.full_audit_mode else '增量审计'}")

        all_docs = self.find_all_documents()
        if not all_docs:
            print("\n✨ 没有需要处理的文档，审计完成！")
            return

        if max_docs and max_docs < len(all_docs):
            print(f"\n🧪 测试模式：只处理前 {max_docs} 个文档")
            all_docs = all_docs[:max_docs]

        all_analyses = []
        print(f"\n📖 开始分析文档...")

        iterator = tqdm(all_docs, desc="分析进度", unit="篇") if HAS_TQDM else all_docs

        for dir_name, file_path in iterator:
            analysis = self.analyze_document(dir_name, file_path)
            if analysis is not None:
                all_analyses.append(analysis)
                self.stats["total_processed"] += 1
                self.stats["category_counts"][analysis["category"]] += 1

                dir_stat = self.stats["dir_stats"][dir_name]
                dir_stat["count"] += 1
                dir_stat["scores"].append(analysis["total_score"])

                for dim, score in analysis["scores"].items():
                    self.stats["dimension_avg"][dim].append(score)

                file_str = str(file_path.relative_to(self.base_path))
                self.audit_state["audited_files"][file_str] = {
                    "time": datetime.now().isoformat(),
                    "score": analysis["total_score"],
                    "category": analysis["category"]
                }

        for dir_name, dir_stat in self.stats["dir_stats"].items():
            if dir_stat["scores"]:
                dir_stat["avg_score"] = round(sum(dir_stat["scores"]) / len(dir_stat["scores"]), 2)

        if all_analyses:
            self.generate_audit_report(all_analyses)

        self.audit_state["last_audit"] = datetime.now().isoformat()
        self._save_audit_state()

        self._print_summary(all_analyses)
        self._save_logs(all_analyses)

    def generate_audit_report(self, all_analyses: List[Dict]):
        """生成详细的审计报告"""
        print("\n📝 生成审计报告...")

        timestamp = datetime.now()
        date_str = timestamp.strftime("%Y-%m-%d")
        datetime_str = timestamp.strftime("%Y-%m-%d %H:%M:%S")

        report_file = self.output_audit_dir / f"{date_str}-全面审计报告.md"
        short_report_file = self.output_audit_dir / f"{date_str}-审计摘要.md"

        total = len(all_analyses)
        categories = self.stats["category_counts"]
        all_scores_list = [a["total_score"] for a in all_analyses]
        avg_total = sum(all_scores_list) / total if total > 0 else 0

        score_distribution = {
            "90-100": sum(1 for s in all_scores_list if s >= 90),
            "85-89": sum(1 for s in all_scores_list if 85 <= s < 90),
            "80-84": sum(1 for s in all_scores_list if 80 <= s < 85),
            "70-79": sum(1 for s in all_scores_list if 70 <= s < 80),
            "60-69": sum(1 for s in all_scores_list if 60 <= s < 70),
            "50-59": sum(1 for s in all_scores_list if 50 <= s < 60),
            "< 50": sum(1 for s in all_scores_list if s < 50),
        }

        dimensions = self.config["scoring"]["dimensions"]
        dimension_names = {k: v["name"] for k, v in dimensions.items()}
        dim_avg = {}
        for dim, scores in self.stats["dimension_avg"].items():
            if scores:
                dim_avg[dim] = round(sum(scores) / len(scores), 2)

        sorted_by_score = sorted(all_analyses, key=lambda x: x["total_score"], reverse=True)
        top_docs = sorted_by_score[:10]
        bottom_docs = sorted_by_score[-10:] if len(sorted_by_score) >= 10 else sorted_by_score

        dir_summaries = []
        for dir_name, dir_stat in sorted(self.stats["dir_stats"].items()):
            if dir_stat["count"] > 0:
                dir_summaries.append({
                    "name": dir_name, "count": dir_stat["count"],
                    "avg_score": dir_stat["avg_score"]
                })
        dir_summaries.sort(key=lambda x: x["avg_score"], reverse=True)

        all_domains = []
        for a in all_analyses:
            all_domains.extend(a["domains"])
        domain_counter = Counter(all_domains)
        top_domains = domain_counter.most_common(10)

        all_issues = []
        for a in all_analyses:
            all_issues.extend(a["issues"])
        issue_counter = Counter(all_issues)
        common_issues = issue_counter.most_common(10)

        report_content = self._generate_full_report(
            timestamp=datetime_str, total=total, categories=categories,
            avg_total=avg_total, score_distribution=score_distribution,
            dim_avg=dim_avg, dimension_names=dimension_names,
            top_docs=top_docs, bottom_docs=bottom_docs,
            dir_summaries=dir_summaries, top_domains=top_domains,
            common_issues=common_issues, all_analyses=all_analyses,
        )

        report_file.write_text(report_content, encoding='utf-8')
        print(f"   📄 完整报告: {report_file}")

        short_content = self._generate_short_report(
            timestamp=datetime_str, total=total, categories=categories,
            avg_total=avg_total, score_distribution=score_distribution,
            dim_avg=dim_avg, dimension_names=dimension_names,
            top_docs=top_docs, bottom_docs=bottom_docs,
            dir_summaries=dir_summaries, common_issues=common_issues,
        )

        short_report_file.write_text(short_content, encoding='utf-8')
        print(f"   📋 摘要报告: {short_report_file}")

        json_file = self.output_audit_dir / f"{date_str}-审计数据.json"
        json_data = {
            "audit_time": datetime_str,
            "mode": "full" if self.full_audit_mode else "incremental",
            "total_documents": total, "categories": categories,
            "average_score": round(avg_total, 2),
            "score_distribution": score_distribution,
            "dimension_averages": {dimension_names.get(k, k): v for k, v in dim_avg.items()},
            "directory_summary": dir_summaries,
            "top_documents": [
                {"file": a["relative_path"], "score": a["total_score"], "category": a["category"]}
                for a in top_docs
            ],
            "bottom_documents": [
                {"file": a["relative_path"], "score": a["total_score"], "category": a["category"]}
                for a in bottom_docs
            ],
        }
        json_file.write_text(json.dumps(json_data, ensure_ascii=False, indent=2), encoding='utf-8')
        print(f"   💾 数据文件: {json_file}")

    def _generate_full_report(self, **kwargs) -> str:
        """生成完整报告内容"""
        total = kwargs["total"]
        categories = kwargs["categories"]
        avg_total = kwargs["avg_total"]
        score_dist = kwargs["score_distribution"]
        dim_avg = kwargs["dim_avg"]
        dim_names = kwargs["dimension_names"]
        top_docs = kwargs["top_docs"]
        bottom_docs = kwargs["bottom_docs"]
        dir_summaries = kwargs["dir_summaries"]
        top_domains = kwargs["top_domains"]
        common_issues = kwargs["common_issues"]
        all_analyses = kwargs["all_analyses"]
        timestamp = kwargs["timestamp"]

        report = f"""# 📚 知识库质量全面审计报告

**审计时间**: {timestamp}
**审计模式**: {'全面审计' if self.full_audit_mode else '增量审计'}
**审计文档数**: {total} 篇
**综合平均得分**: {avg_total:.2f} / 100
**执行耗时**: {(datetime.now() - self.stats['start_time']).total_seconds():.1f} 秒

---

## 📊 一、整体质量概览

### 1.1 质量分类统计

| 等级 | 文档数 | 占比 | 说明 |
|------|--------|------|------|
| ⭐ **优秀** | {categories['优秀']} | {(categories['优秀'] / total * 100):.1f}% | 综合得分 ≥ 85 |
| ✅ **合格** | {categories['合格']} | {(categories['合格'] / total * 100):.1f}% | 综合得分 70-84 |
| ⚠️  **待修正** | {categories['待修正']} | {(categories['待修正'] / total * 100):.1f}% | 综合得分 50-69 |
| ❌ **不合格** | {categories['不合格']} | {(categories['不合格'] / total * 100):.1f}% | 综合得分 < 50 |

### 1.2 分数段分布

| 分数段 | 文档数 | 占比 |
|--------|--------|------|
"""
        for range_key, count in score_dist.items():
            report += f"| {range_key} | {count} | {(count / total * 100):.1f}% |\n"

        report += f"""
### 1.3 各维度平均得分

| 维度 | 平均分 | 权重 | 说明 |
|------|--------|------|------|
"""
        dim_order = ["accuracy", "completeness", "consistency", "timeliness", "relevance", "comprehensibility"]
        weights = self.config["scoring"]["weights"]
        for dim in dim_order:
            if dim in dim_avg:
                desc = self.config["scoring"]["dimensions"].get(dim, {}).get("description", "")
                report += f"| {dim_names.get(dim, dim)} | {dim_avg[dim]:.2f} | {int(weights[dim] * 100)}% | {desc} |\n"

        report += """
---

## 📁 二、目录质量分析

### 2.1 各目录平均得分

| 目录 | 文档数 | 平均得分 |
|------|--------|----------|
"""
        for ds in dir_summaries:
            emoji = "⭐" if ds["avg_score"] >= 85 else ("✅" if ds["avg_score"] >= 70 else ("⚠️" if ds["avg_score"] >= 50 else "❌"))
            report += f"| {emoji} `{ds['name']}` | {ds['count']} | {ds['avg_score']:.2f} |\n"

        report += """
---

## 🏆 三、优质知识 TOP 10

| 排名 | 文档 | 目录 | 得分 | 分类 |
|------|------|------|------|------|
"""
        for i, a in enumerate(top_docs, 1):
            report += f"| {i} | `{a['file_name']}` | {a['dir_name']} | **{a['total_score']:.1f}** | {a['category']} |\n"

        report += """
---

## 🚨 四、需重点关注文档 TOP 10

| 排名 | 文档 | 目录 | 得分 | 分类 | 主要问题 |
|------|------|------|------|------|----------|
"""
        for i, a in enumerate(reversed(bottom_docs), 1):
            issue_str = "、".join(a["issues"][:2]) if a["issues"] else "无"
            report += f"| {i} | `{a['file_name']}` | {a['dir_name']} | {a['total_score']:.1f} | {a['category']} | {issue_str} |\n"

        report += f"""
---

## 🏷️ 五、技术领域分布

| 领域 | 文档数 |
|------|--------|
"""
        for domain, count in top_domains:
            report += f"| {domain} | {count} |\n"

        report += """
---

## 🔍 六、常见问题分析

### 6.1 高频出现的问题

| 问题 | 出现次数 | 占比 |
|------|----------|------|
"""
        for issue, count in common_issues:
            report += f"| {issue} | {count} | {(count / total * 100):.1f}% |\n"

        report += """
### 6.2 质量改进建议

1. **准确性方面**：
   - 增加具体数据、百分比和可验证的数字
   - 补充技术来源链接和参考资料
   - 减少"可能""也许"等不确定表述

2. **完整性方面**：
   - 确保文档有清晰的标题结构（#、##、###）
   - 增加代码块、表格、列表等多种内容形式
   - 建议包含：背景介绍 → 核心原理 → 实现方法 → 应用场景 → 总结的完整结构

3. **一致性方面**：
   - 统一术语表述（避免同一概念中英混用）
   - 保持Markdown格式的一致性
   - 避免内部矛盾的表述

4. **时效性方面**：
   - 关注最新技术动态和版本更新
   - 及时更新过时的技术描述
   - 标注内容的更新时间

5. **相关性方面**：
   - 聚焦大模型/AI相关的技术主题
   - 覆盖多个技术领域以增加知识广度
   - 补充技术深度关键词（如梯度下降、注意力机制等）

6. **可理解性方面**：
   - 增加术语定义和解释性文字
   - 使用粗体/列表等格式帮助阅读
   - 保持适中的句子长度（15-60字）

---

## 📋 七、逐文档详细评分

"""

        for dir_info in self.audit_dirs:
            dir_name = dir_info["name"]
            dir_docs = [a for a in all_analyses if a["dir_name"] == dir_name]
            if not dir_docs:
                continue

            dir_docs.sort(key=lambda x: x["total_score"], reverse=True)
            dir_names_list = [d["name"] for d in self.audit_dirs]
            report += f"\n### 7.{dir_names_list.index(dir_name) + 1} {dir_name} ({len(dir_docs)} 篇)\n\n"
            report += "| # | 文档 | 综合 | 准确 | 完整 | 一致 | 时效 | 相关 | 可理解 | 分类 |\n"
            report += "|---|------|------|------|------|------|------|------|--------|------|\n"

            for i, a in enumerate(dir_docs, 1):
                s = a["scores"]
                emoji = "⭐" if a["category"] == "优秀" else ("✅" if a["category"] == "合格" else ("⚠️" if a["category"] == "待修正" else "❌"))
                fname = a['file_name'][:40] + ("..." if len(a['file_name']) > 40 else "")
                report += f"| {i} | `{fname}` | **{a['total_score']:.1f}** | {s['accuracy']:.1f} | {s['completeness']:.1f} | {s['consistency']:.1f} | {s['timeliness']:.1f} | {s['relevance']:.1f} | {s['comprehensibility']:.1f} | {emoji}{a['category']} |\n"

        report += "\n---\n\n## 🔎 八、重点文档详细分析\n\n"

        detailed_count = 0
        for a in top_docs + list(reversed(bottom_docs)):
            if detailed_count >= 30:
                break
            detailed_count += 1

            report += f"### {detailed_count}. `{a['file_name']}`\n\n"
            report += f"- **目录**: {a['dir_name']}\n"
            report += f"- **综合得分**: **{a['total_score']:.1f}** ({a['category']})\n"
            report += f"- **文件大小**: {a['file_size']} 字节 | 字数: {a['word_count']} | 章节: {a['section_count']}\n"
            report += f"- **修改时间**: {a['file_mtime'].strftime('%Y-%m-%d %H:%M:%S')}\n"
            report += f"- **主要领域**: {', '.join(a['domains'])}\n\n"

            report += "**六维评分**:\n\n"
            report += "| 维度 | 得分 | 维度 | 得分 |\n"
            report += "|------|------|------|------|\n"
            s = a["scores"]
            report += f"| 准确性 | {s['accuracy']:.1f} | 完整性 | {s['completeness']:.1f} |\n"
            report += f"| 一致性 | {s['consistency']:.1f} | 时效性 | {s['timeliness']:.1f} |\n"
            report += f"| 相关性 | {s['relevance']:.1f} | 可理解性 | {s['comprehensibility']:.1f} |\n\n"

            features = []
            if a["has_code_block"]: features.append("含代码块")
            if a["has_table"]: features.append("含表格")
            if a["has_list"]: features.append("含列表")
            if a["has_link"]: features.append("含链接")
            if a["has_image"]: features.append("含图片")
            if features:
                report += f"**内容特性**: {', '.join(features)}\n\n"

            if a["issues"]:
                report += "**检测到的问题**:\n\n"
                for issue in a["issues"]:
                    report += f"- ⚠️ {issue}\n"
                report += "\n"

            if a["red_flags"]:
                report += "**警示标记**:\n\n"
                for flag in a["red_flags"]:
                    report += f"- 🔴 {flag}\n"
                report += "\n"

            report += "---\n\n"

        report += f"""
## 📌 九、审计总结

- 本次共审计 {total} 篇知识文档
- 平均得分 {avg_total:.2f}/100
- 优质文档 (≥85分): {categories['优秀']} 篇 ({(categories['优秀'] / total * 100):.1f}%)
- 合格文档 (70-84分): {categories['合格']} 篇 ({(categories['合格'] / total * 100):.1f}%)
- 待修正文档 (50-69分): {categories['待修正']} 篇 ({(categories['待修正'] / total * 100):.1f}%)
- 不合格文档 (<50分): {categories['不合格']} 篇 ({(categories['不合格'] / total * 100):.1f}%)
- 分析过程中出现 {self.stats['errors']} 个错误

**总体评价**: 
"""
        if avg_total >= 85:
            report += "🌟 知识库整体质量优秀，保持良好的维护和更新机制。"
        elif avg_total >= 70:
            report += "👍 知识库整体质量合格，存在一定改进空间，建议关注待修正文档。"
        elif avg_total >= 50:
            report += "⚠️ 知识库质量有待提升，建议重点关注内容完善和结构优化。"
        else:
            report += "🚨 知识库整体质量偏低，需要进行系统性改进和内容补充。"

        report += f"""

---

*本报告由知识质量审计工具自动生成 - {timestamp}*
"""
        return report

    def _generate_short_report(self, **kwargs) -> str:
        """生成简短的摘要报告"""
        total = kwargs["total"]
        categories = kwargs["categories"]
        avg_total = kwargs["avg_total"]
        dim_avg = kwargs["dim_avg"]
        dim_names = kwargs["dimension_names"]
        top_docs = kwargs["top_docs"]
        bottom_docs = kwargs["bottom_docs"]
        dir_summaries = kwargs["dir_summaries"]
        common_issues = kwargs["common_issues"]
        timestamp = kwargs["timestamp"]

        report = f"""# 📋 知识质量审计摘要

**审计时间**: {timestamp}
**审计文档**: {total} 篇
**平均得分**: {avg_total:.2f}/100

## 质量分布

| 等级 | 数量 | 占比 |
|------|------|------|
| ⭐ 优秀 | {categories['优秀']} | {(categories['优秀'] / total * 100):.1f}% |
| ✅ 合格 | {categories['合格']} | {(categories['合格'] / total * 100):.1f}% |
| ⚠️ 待修正 | {categories['待修正']} | {(categories['待修正'] / total * 100):.1f}% |
| ❌ 不合格 | {categories['不合格']} | {(categories['不合格'] / total * 100):.1f}% |

## 六维评分

| 维度 | 平均分 |
|------|--------|
"""
        for dim in ["accuracy", "completeness", "consistency", "timeliness", "relevance", "comprehensibility"]:
            if dim in dim_avg:
                report += f"| {dim_names.get(dim, dim)} | {dim_avg[dim]:.2f} |\n"

        report += """
## 优质知识 TOP 5

| 文档 | 得分 | 分类 |
|------|------|------|
"""
        for a in top_docs[:5]:
            fname = a['file_name'][:30] + ("..." if len(a['file_name']) > 30 else "")
            report += f"| `{fname}` | **{a['total_score']:.1f}** | {a['category']} |\n"

        report += """
## 需关注知识 TOP 5

| 文档 | 得分 | 分类 |
|------|------|------|
"""
        for a in list(reversed(bottom_docs))[:5]:
            fname = a['file_name'][:30] + ("..." if len(a['file_name']) > 30 else "")
            report += f"| `{fname}` | {a['total_score']:.1f} | {a['category']} |\n"

        report += f"""
## 各目录平均得分

| 目录 | 文档数 | 平均分 |
|------|--------|--------|
"""
        for ds in dir_summaries:
            report += f"| `{ds['name']}` | {ds['count']} | {ds['avg_score']:.2f} |\n"

        report += f"""
## 常见问题

| 问题 | 出现次数 |
|------|----------|
"""
        for issue, count in common_issues[:5]:
            report += f"| {issue} | {count} |\n"

        report += f"""
---

*审计摘要 - {timestamp}*
"""
        return report

    def _print_summary(self, all_analyses: List[Dict]):
        """打印运行总结"""
        print("\n" + "=" * 70)
        print("📊 审计完成总结")
        print("=" * 70)

        elapsed = (datetime.now() - self.stats["start_time"]).total_seconds()
        total = len(all_analyses)

        print(f"\n⏱️  执行耗时: {elapsed:.1f} 秒")
        print(f"📄 扫描文档: {self.stats['total_scanned']} 篇")
        print(f"✅ 成功分析: {self.stats['total_processed']} 篇")
        if self.stats["errors"] > 0:
            print(f"❌ 处理失败: {self.stats['errors']} 篇")

        all_scores_list = [a["total_score"] for a in all_analyses]
        if all_scores_list:
            avg_score = sum(all_scores_list) / len(all_scores_list)
            print(f"\n📈 综合平均得分: {avg_score:.2f} / 100")
            print(f"   最高分: {max(all_scores_list):.2f}")
            print(f"   最低分: {min(all_scores_list):.2f}")

        print("\n📊 分类统计:")
        for cat, count in self.stats["category_counts"].items():
            if count > 0:
                bar_length = int(count / total * 40) if total > 0 else 0
                bar = "█" * bar_length
                print(f"   {cat}: {count:4d} 篇 ({count/total*100:5.1f}%) {bar}")

        print("\n📁 目录分布:")
        for dir_name, dir_stat in sorted(self.stats["dir_stats"].items()):
            if dir_stat["count"] > 0:
                print(f"   {dir_name}: {dir_stat['count']:4d} 篇 | 平均分 {dir_stat['avg_score']:.2f}")

        if self.stats["errors"] >= 3:
            print("\n💡 提示：有多个文档分析失败，请查看错误日志。")

        print("\n" + "=" * 70)
        print("✅ 知识质量审计完成！")
        print(f"📄 详细报告已保存到: {self.output_audit_dir}")
        print("=" * 70)

    def _save_logs(self, all_analyses: List[Dict]):
        """保存执行日志和错误日志"""
        timestamp = datetime.now()

        pipeline_log = self.pipeline_log_dir / f"pipeline_{timestamp.strftime('%Y%m%d_%H%M%S')}.log"
        log_content = f"""知识质量审计执行日志
时间: {timestamp.strftime('%Y-%m-%d %H:%M:%S')}
模式: {'全面审计' if self.full_audit_mode else '增量审计'}

[统计信息]
- 扫描文档数: {self.stats['total_scanned']}
- 分析成功: {self.stats['total_processed']}
- 处理错误: {self.stats['errors']}
- 执行耗时: {(datetime.now() - self.stats['start_time']).total_seconds():.1f}秒

[分类统计]
"""
        for cat, count in self.stats["category_counts"].items():
            log_content += f"- {cat}: {count} 篇\n"

        log_content += "\n[文档处理记录]\n"
        for a in all_analyses:
            log_content += f"[{a['category']}] {a['total_score']:6.2f} - {a['relative_path']}\n"

        pipeline_log.write_text(log_content, encoding='utf-8')

        latest_log = self.base_path / "01_inbox" / "pipeline.log"
        if latest_log.parent.exists():
            latest_log.write_text(log_content, encoding='utf-8')

        if self.error_log:
            error_file = self.output_audit_dir / f"error_{timestamp.strftime('%Y%m%d_%H%M%S')}.log"
            error_file.write_text("\n".join(self.error_log), encoding='utf-8')
            print(f"❌ 错误日志: {error_file}")


def main():
    """主函数"""
    try:
        config_path = Path(__file__).parent.parent / "config" / "config.json"
        auditor = KnowledgeAuditor(str(config_path), full_audit=True)
        auditor.run()
    except Exception as e:
        import traceback
        error_msg = f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - 严重错误: {str(e)}\n{traceback.format_exc()}\n"
        try:
            error_log_path = Path(__file__).parent.parent / "08_audit" / "error.log"
            if not error_log_path.exists():
                error_log_path = Path(__file__).parent.parent.parent / "08_audit" / "error.log"
            error_log_path.parent.mkdir(parents=True, exist_ok=True)
            with open(error_log_path, "a", encoding='utf-8') as f:
                f.write(error_msg)
        except Exception:
            pass
        print(f"\n❌ 审计失败！")
        print(f"错误信息: {str(e)}")
        print(f"详细堆栈:\n{traceback.format_exc()}")
        sys.exit(1)


if __name__ == "__main__":
    main()
