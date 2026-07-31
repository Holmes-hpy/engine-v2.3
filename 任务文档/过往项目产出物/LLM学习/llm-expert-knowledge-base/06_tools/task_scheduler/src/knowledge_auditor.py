#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path


class KnowledgeAuditor:

    def __init__(self, config_path=None):
        self.base_path = Path(__file__).parent.parent
        if config_path is None:
            config_path = self.base_path / 'config' / 'pipeline_config.json'
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = json.load(f)
        self.inbox_dir = self.base_path / self.config['output']['inbox_dir']
        self.inbox_dir.mkdir(parents=True, exist_ok=True)

    def load_distilled(self):
        today = datetime.now().strftime('%Y-%m-%d')
        wiki_dir = self.base_path / self.config['output']['wiki_dir']
        json_file = wiki_dir / f'{today}-知识蒸馏.json'
        if json_file.exists():
            with open(json_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        if wiki_dir.exists():
            files = sorted(wiki_dir.glob('*-知识蒸馏.json'), reverse=True)
            if files:
                with open(files[0], 'r', encoding='utf-8') as f:
                    return json.load(f)
        return []

    def load_raw_items(self):
        today = datetime.now().strftime('%Y-%m-%d')
        raw_file = self.base_path / '02_raw' / f'raw-{today}.json'
        if raw_file.exists():
            with open(raw_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        raw_dir = self.base_path / '02_raw'
        if raw_dir.exists():
            files = sorted(raw_dir.glob('raw-*.json'), reverse=True)
            if files:
                with open(files[0], 'r', encoding='utf-8') as f:
                    return json.load(f)
        return []

    def generate_briefing(self, items, distilled):
        today = datetime.now().strftime('%Y-%m-%d')
        source_names = list(set([it.get('source', '') for it in items]))

        lines = []
        lines.append(f"# 大模型领域每日信息简报 - {today}")
        lines.append("")
        lines.append(f"- **采集时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"- **采集来源数量**: {len(source_names)}")
        lines.append(f"- **筛选后内容数量**: {len(items)}")
        lines.append("")

        # 分类统计
        all_cats = []
        for d in distilled:
            for c in d.get('categories', []):
                all_cats.append(c)
        cat_counter = Counter(all_cats)
        if cat_counter:
            lines.append("## 内容分类统计")
            lines.append("")
            for cat, cnt in cat_counter.most_common():
                lines.append(f"- **{cat}**: {cnt} 篇")
            lines.append("")

        lines.append("## 内容列表")
        lines.append("")

        for idx, it in enumerate(items, start=1):
            title = it.get('title', '').replace('\n', ' ').strip()
            src = it.get('source', 'Unknown')
            link = it.get('link', '')
            importance = it.get('importance', '★★★')

            # 查找对应的蒸馏摘要
            short_summary = '...'
            for d in distilled:
                if d['title'] == title:
                    s = d.get('summary', '')
                    if len(s) > 120:
                        short_summary = s[:117] + '...'
                    elif s:
                        short_summary = s
                    break

            lines.append(f"### {idx}. {title}")
            lines.append(f"- **来源**: {src}")
            lines.append(f"- **链接**: {link}")
            lines.append(f"- **重要性**: {importance}")
            lines.append(f"- **一句话摘要**: {short_summary}")
            lines.append("")

        briefing_file = self.inbox_dir / f"{today}-每日信息简报.md"
        with open(briefing_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
        print(f"[INFO] 每日信息简报已保存: {briefing_file}")
        return briefing_file

    def run(self, items=None, distilled=None):
        print("=" * 60)
        print("开始执行知识审计与简报生成")
        print(f"执行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)

        if items is None:
            items = self.load_raw_items()
        if distilled is None:
            distilled = self.load_distilled()

        if not items:
            print("[ERROR] 没有可生成简报的数据")
            return None

        briefing = self.generate_briefing(items, distilled)
        print(f"[DONE] 简报生成完成: {len(items)} 条内容")
        return briefing


def main():
    auditor = KnowledgeAuditor()
    result = auditor.run()
    if result is None:
        sys.exit(1)


if __name__ == '__main__':
    main()
