#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import re
import sys
from datetime import datetime
from pathlib import Path


class KnowledgeDistiller:

    KEYWORDS_CATEGORY = {
        'agent': ['agent', 'agents', 'multi-agent', 'autonomous agent', 'tool use', 'tool calling'],
        'model_architecture': ['transformer', 'attention', 'llm', 'large language model', 'gpt', 'claude', 'gemini', 'mo', 'mixture', 'finetune', 'fine-tune', 'pretrain', 'pre-train', 'peft', 'lora'],
        'reasoning': ['reasoning', 'chain of thought', 'cot', 'self-consistency', 'logic', 'inference'],
        'alignment': ['alignment', 'safety', 'rlhf', 'dpo', 'ppo', 'red team', 'jailbreak', 'harm', 'bias'],
        'retrieval_rag': ['rag', 'retrieval', 'retriever', 'vector', 'embedding', 'knowledge base', 'document'],
        'evaluation': ['evaluation', 'benchmark', 'mmlu', 'hellaswag', 'humaneval', 'mbpp', 'gsm8k', 'metric'],
        'multimodal': ['multimodal', 'vision', 'image', 'video', 'audio', 'vlm', 'diffusion', 'stable diffusion'],
        'efficiency': ['quantization', 'pruning', 'distillation', 'compression', 'inference speed', 'throughput', 'memory', 'efficiency', 'optimization'],
        'training': ['training', 'optimizer', 'learning rate', 'adam', 'gradient', 'backpropagation', 'batch size'],
        'data': ['dataset', 'data', 'synthetic data', 'curriculum', 'annotation', 'data augmentation'],
        'security': ['security', 'privacy', 'differential privacy', 'federated', 'poisoning', 'attack', 'defense'],
        'application': ['application', 'use case', 'industry', 'enterprise', 'product', 'chatbot', 'assistant', 'coding agent']
    }

    def __init__(self, config_path=None):
        self.base_path = Path(__file__).parent.parent
        if config_path is None:
            config_path = self.base_path / 'config' / 'pipeline_config.json'
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = json.load(f)
        self.wiki_dir = self.base_path / self.config['output']['wiki_dir']
        self.wiki_dir.mkdir(parents=True, exist_ok=True)
        self.inbox_dir = self.base_path / self.config['output']['inbox_dir']
        self.inbox_dir.mkdir(parents=True, exist_ok=True)

    def categorize(self, item):
        title = item.get('title', '').lower()
        summary = item.get('summary', '').lower()
        text = f"{title} {summary}"
        matched = []
        for cat, kws in self.KEYWORDS_CATEGORY.items():
            for kw in kws:
                if re.search(r'\b' + re.escape(kw) + r'\b', text):
                    matched.append(cat)
                    break
        if not matched:
            matched = ['general_ai']
        return matched

    def generate_one_line_summary(self, item):
        title = item.get('title', '')
        summary = item.get('summary', '').strip()
        # 取摘要第一句或生成简短描述
        first_sentence = ''
        if summary:
            m = re.match(r'(.+?[。.!?！？\n])', summary)
            if m:
                first_sentence = m.group(1).strip()
            else:
                first_sentence = summary[:150]
        categories = item.get('_categories', ['AI'])
        cat_str = '/'.join(categories)
        if first_sentence:
            return f"[{cat_str}] {first_sentence}"
        return f"[{cat_str}] {title[:80]}"

    def generate_key_points(self, item):
        summary = item.get('summary', '').strip()
        if not summary:
            return ['暂无详细信息']
        # 按句号分割取前几句
        sentences = re.split(r'[。.!?！？\n]', summary)
        sentences = [s.strip() for s in sentences if s.strip()]
        return sentences[:5]

    def distill(self, items):
        print(f"[INFO] 开始知识蒸馏: {len(items)} 条原始数据")
        distilled = []
        for idx, item in enumerate(items):
            categories = self.categorize(item)
            item['_categories'] = categories
            d = {
                'id': f"KNOW-{datetime.now().strftime('%Y%m%d')}-{idx+1:04d}",
                'title': item.get('title', ''),
                'summary': self.generate_one_line_summary(item),
                'key_points': self.generate_key_points(item),
                'categories': categories,
                'authors': item.get('authors', []),
                'published': item.get('published', ''),
                'source': item.get('source', ''),
                'link': item.get('link', ''),
                'distilled_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'importance': item.get('importance', '★★★')
            }
            distilled.append(d)
        print(f"[OK] 知识蒸馏完成: {len(distilled)} 条")
        return distilled

    def save_wiki_entries(self, distilled):
        today = datetime.now().strftime('%Y-%m-%d')
        wiki_file = self.wiki_dir / f'{today}-知识蒸馏.md'
        lines = []
        lines.append(f"# AI Wiki 知识蒸馏 - {today}")
        lines.append("")
        lines.append(f"- **蒸馏时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"- **蒸馏条目数**: {len(distilled)}")
        lines.append("")

        # 按分类分组
        grouped = {}
        for d in distilled:
            for cat in d['categories']:
                if cat not in grouped:
                    grouped[cat] = []
                grouped[cat].append(d)

        for cat, items in sorted(grouped.items(), key=lambda x: -len(x[1])):
            lines.append(f"## {cat} ({len(items)})")
            lines.append("")
            for d in items:
                lines.append(f"### {d['id']}: {d['title']}")
                lines.append(f"- **来源**: {d['source']}")
                lines.append(f"- **链接**: {d['link']}")
                lines.append(f"- **发布时间**: {d['published']}")
                lines.append(f"- **一句话摘要**: {d['summary']}")
                if d['key_points']:
                    lines.append("- **关键要点**:")
                    for kp in d['key_points']:
                        lines.append(f"  - {kp}")
                lines.append("")

        with open(wiki_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
        print(f"[INFO] Wiki 已保存: {wiki_file}")

        # 保存 JSON
        json_file = self.wiki_dir / f'{today}-知识蒸馏.json'
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(distilled, f, ensure_ascii=False, indent=2)
        print(f"[INFO] 蒸馏 JSON 已保存: {json_file}")
        return wiki_file

    def load_raw(self):
        today = datetime.now().strftime('%Y-%m-%d')
        raw_file = self.base_path / '02_raw' / f'raw-{today}.json'
        if raw_file.exists():
            with open(raw_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        # 查找最近的 raw 文件
        raw_dir = self.base_path / '02_raw'
        if raw_dir.exists():
            files = sorted(raw_dir.glob('raw-*.json'), reverse=True)
            if files:
                with open(files[0], 'r', encoding='utf-8') as f:
                    return json.load(f)
        return []

    def run(self, items=None):
        print("=" * 60)
        print("开始执行知识蒸馏任务")
        print(f"执行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)

        if items is None:
            items = self.load_raw()

        if not items:
            print("[ERROR] 没有可蒸馏的数据")
            return []

        distilled = self.distill(items)
        self.save_wiki_entries(distilled)
        print(f"[DONE] 知识蒸馏完成: {len(distilled)} 条")
        return distilled


def main():
    distiller = KnowledgeDistiller()
    result = distiller.run()
    if not result:
        sys.exit(1)


if __name__ == '__main__':
    main()
