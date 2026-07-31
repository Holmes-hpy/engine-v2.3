#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import io
import json
import os
import sys
import time
import traceback
from datetime import datetime
from pathlib import Path


class TeeOutput:
    """将 stdout/stderr 同时输出到终端和日志文件"""

    def __init__(self, original_stream, log_file):
        self.original = original_stream
        self.log_file = log_file
        self.encoding = 'utf-8'

    def write(self, data):
        try:
            self.original.write(data)
            self.original.flush()
        except Exception:
            pass
        try:
            if isinstance(data, bytes):
                data = data.decode('utf-8', errors='replace')
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(data)
                f.flush()
        except Exception:
            pass
        return len(data)

    def flush(self):
        try:
            self.original.flush()
        except Exception:
            pass


class KnowledgePipeline:
    """大模型知识库完整流程管理"""

    def __init__(self, config_path=None):
        if config_path is None:
            self.base_path = Path(__file__).parent.parent
            config_path = self.base_path / "config" / "pipeline_config.json"
        else:
            self.base_path = Path(__file__).parent.parent

        self.config = self.load_config(config_path)
        self.state_file = self.base_path / "state" / "pipeline_state.json"
        self.logs_dir = self.base_path / "logs"
        self.state = self.load_state()

        # 确保目录存在
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        (self.base_path / "state").mkdir(parents=True, exist_ok=True)
        (self.base_path / "02_raw").mkdir(parents=True, exist_ok=True)

        # 设置输出目录
        self.inbox_dir = self.base_path / self.config['output']['inbox_dir']
        self.wiki_dir = self.base_path / self.config['output']['wiki_dir']
        self.error_log_path = self.base_path / self.config['output']['error_log']
        self.inbox_dir.mkdir(parents=True, exist_ok=True)
        self.wiki_dir.mkdir(parents=True, exist_ok=True)
        self.error_log_path.parent.mkdir(parents=True, exist_ok=True)

        # 设置今天的日志文件
        today = datetime.now().strftime('%Y-%m-%d')
        self.log_file = self.logs_dir / f"pipeline-{today}.log"

        # 备份原来的 stdout/stderr
        self._original_stdout = sys.stdout
        self._original_stderr = sys.stderr
        self._tee_stdout = None
        self._tee_stderr = None

    def setup_logging(self):
        """设置 stdout/stderr 双重输出（终端 + 日志文件）"""
        # 初始化日志文件（清空旧内容）
        with open(self.log_file, 'w', encoding='utf-8') as f:
            f.write(f"# Pipeline Log - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"# 工作目录: {self.base_path}\n\n")

        self._tee_stdout = TeeOutput(self._original_stdout, self.log_file)
        self._tee_stderr = TeeOutput(self._original_stderr, self.log_file)
        sys.stdout = self._tee_stdout
        sys.stderr = self._tee_stderr
        print(f"[INFO] 日志已配置: {self.log_file}")

    def restore_logging(self):
        sys.stdout = self._original_stdout
        sys.stderr = self._original_stderr

    def load_config(self, config_path):
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            self.write_error(f"加载配置失败: {e}")
            raise

    def load_state(self):
        if self.state_file.exists():
            try:
                with open(self.state_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {"last_run": None, "last_full_audit": None, "runs": []}

    def save_state(self):
        with open(self.state_file, "w", encoding="utf-8") as f:
            json.dump(self.state, f, ensure_ascii=False, indent=2)

    def write_error(self, error_message):
        """将错误信息追加到 01_inbox/error.log"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_line = f"[{timestamp}] {error_message}\n"
        try:
            with open(self.error_log_path, "a", encoding="utf-8") as f:
                f.write(log_line)
        except Exception as e:
            # 尝试直接打印到 stderr
            print(f"[FATAL] 写入错误日志失败: {e}", file=self._original_stderr)

    def run_radar(self):
        """调用信息雷达采集模块"""
        print("=" * 60)
        print("[STAGE 1] 信息雷达 - 从 arXiv 等数据源采集")
        print("=" * 60)
        sys.path.insert(0, str(self.base_path / "src"))
        from radar_collector import ArxivCollector
        collector = ArxivCollector(self.base_path / "config" / "pipeline_config.json")
        items = collector.run()
        return items

    def run_distillation(self, items=None):
        """调用知识蒸馏模块"""
        print("=" * 60)
        print("[STAGE 2] 知识蒸馏 - 生成 AI Wiki 知识点")
        print("=" * 60)
        sys.path.insert(0, str(self.base_path / "src"))
        from knowledge_distiller import KnowledgeDistiller
        distiller = KnowledgeDistiller(self.base_path / "config" / "pipeline_config.json")
        distilled = distiller.run(items)
        return distilled

    def run_audit(self, items=None, distilled=None):
        """调用知识审计与简报生成模块"""
        print("=" * 60)
        print("[STAGE 3] 知识审计 - 生成每日信息简报")
        print("=" * 60)
        sys.path.insert(0, str(self.base_path / "src"))
        from knowledge_auditor import KnowledgeAuditor
        auditor = KnowledgeAuditor(self.base_path / "config" / "pipeline_config.json")
        briefing = auditor.run(items, distilled)
        return briefing

    def run_full_pipeline(self, skip_wait=False):
        """运行完整流程：信息雷达 -> 知识蒸馏 -> 知识审计"""
        success = False
        try:
            print("#" * 60)
            print(f"# 开始运行完整知识流水线 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print("#" * 60)

            self.state["last_run"] = datetime.now().isoformat()

            # Stage 1: 信息雷达
            items = []
            radar_config = self.config["tasks"].get("radar", {})
            if radar_config.get("enabled", True):
                try:
                    items = self.run_radar()
                    if not items:
                        msg = "信息雷达未采集到任何数据，可能网络受限或API限流"
                        print(f"[WARN] {msg}")
                        self.write_error(msg)
                        # 继续使用已有数据
                except Exception as e:
                    msg = f"信息雷达执行异常: {e}"
                    print(f"[ERROR] {msg}")
                    self.write_error(f"{msg}\n{traceback.format_exc()}")
                    items = []
            else:
                # 从 02_raw 目录加载已有数据
                raw_dir = self.base_path / "02_raw"
                if raw_dir.exists():
                    files = sorted(raw_dir.glob("raw-*.json"), reverse=True)
                    if files:
                        with open(files[0], 'r', encoding='utf-8') as f:
                            items = json.load(f)
                        print(f"[INFO] 使用已有数据: {files[0]} ({len(items)} 条)")

            if not items:
                msg = "没有任何数据可用（采集失败且无历史数据），流程终止"
                print(f"[ERROR] {msg}")
                self.write_error(msg)
                return False

            if not skip_wait:
                wait = radar_config.get("wait_after_radar", 2)
                print(f"[INFO] 等待 {wait} 秒后继续...")
                time.sleep(wait)

            # Stage 2: 知识蒸馏
            distilled = []
            distill_config = self.config["tasks"].get("distillation", {})
            if distill_config.get("enabled", True):
                try:
                    distilled = self.run_distillation(items)
                    if not distilled:
                        msg = "知识蒸馏返回空结果"
                        print(f"[WARN] {msg}")
                        self.write_error(msg)
                except Exception as e:
                    msg = f"知识蒸馏执行异常: {e}"
                    print(f"[ERROR] {msg}")
                    self.write_error(f"{msg}\n{traceback.format_exc()}")

            if not skip_wait:
                wait = distill_config.get("wait_after_distillation", 2)
                print(f"[INFO] 等待 {wait} 秒后继续...")
                time.sleep(wait)

            # Stage 3: 知识审计 & 简报
            audit_config = self.config["tasks"].get("audit", {})
            if audit_config.get("enabled", True):
                try:
                    briefing = self.run_audit(items, distilled)
                    if briefing:
                        print(f"[OK] 每日信息简报已生成: {briefing}")
                    else:
                        msg = "未能生成每日信息简报"
                        print(f"[WARN] {msg}")
                        self.write_error(msg)
                except Exception as e:
                    msg = f"知识审计执行异常: {e}"
                    print(f"[ERROR] {msg}")
                    self.write_error(f"{msg}\n{traceback.format_exc()}")

            self.state["last_run"] = datetime.now().isoformat()
            self.save_state()

            print("#" * 60)
            print(f"# 完整流程执行结束 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print("#" * 60)
            print(f"[SUMMARY] 原始采集: {len(items)} 条, 蒸馏: {len(distilled)} 条")
            success = True
        except Exception as e:
            msg = f"完整流程执行异常: {e}"
            print(f"[FATAL] {msg}\n{traceback.format_exc()}")
            self.write_error(f"{msg}\n{traceback.format_exc()}")
            success = False

        return success


def main():
    import argparse

    parser = argparse.ArgumentParser(description="大模型知识库任务调度器")
    parser.add_argument("--full-pipeline", action="store_true", help="运行完整流水线（默认行为）")
    parser.add_argument("--skip-wait", action="store_true", help="跳过等待时间")

    args = parser.parse_args()

    pipeline = KnowledgePipeline()

    # 配置 stdout/stderr 双重输出
    pipeline.setup_logging()

    success = False
    try:
        success = pipeline.run_full_pipeline(skip_wait=args.skip_wait)
    finally:
        pipeline.restore_logging()

    if not success:
        print("[FINAL] 流程执行失败，详细错误见日志文件", file=sys.stderr)
        sys.exit(1)
    else:
        print(f"[FINAL] 流程执行成功！日志: {pipeline.log_file}")


if __name__ == "__main__":
    main()
