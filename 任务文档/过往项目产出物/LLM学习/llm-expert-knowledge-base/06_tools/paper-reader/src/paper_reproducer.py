#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
实验复现模块
对论文进行实验复现，包括环境配置、代码验证、关键实验复现等
"""

import json
import os
import subprocess
import sys
import shutil
import requests
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import tempfile


class PaperReproducer:
    """论文实验复现器"""

    def __init__(self, config_path: str):
        self.config = self._load_config(config_path)
        self.base_path = Path(__file__).parent.parent.parent / self.config["general"]["base_path"]
        self.repro_config = self.config["reproduction"]
        self.env_dir = self.repro_config["virtual_env_dir"]
        self.max_dataset_gb = self.repro_config["max_dataset_size_gb"]

    def _load_config(self, config_path: str) -> Dict:
        """加载配置"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"加载配置失败: {e}")
            return {}

    def setup_environment(self, repo_url: str, work_dir: Path) -> Dict:
        """设置复现环境"""
        print("\n🔧 设置复现环境...")

        env_info = {
            "repo_url": repo_url,
            "work_dir": str(work_dir),
            "python_version": "",
            "dependencies": [],
            "setup_status": "failed",
            "setup_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        try:
            env_info["python_version"] = sys.version.split()[0]

            if self._create_virtual_env(work_dir):
                print("   ✓ 虚拟环境创建成功")

                if self._install_dependencies(work_dir):
                    print("   ✓ 基础依赖安装成功")
                    env_info["setup_status"] = "success"
                else:
                    print("   ⚠️ 依赖安装失败")
            else:
                print("   ⚠️ 虚拟环境创建失败")

        except Exception as e:
            print(f"   ⚠️ 环境设置失败: {e}")
            env_info["setup_status"] = f"failed: {str(e)}"

        return env_info

    def _create_virtual_env(self, work_dir: Path) -> bool:
        """创建虚拟环境"""
        try:
            venv_path = work_dir / self.env_dir

            result = subprocess.run(
                [sys.executable, "-m", "venv", str(venv_path)],
                capture_output=True,
                text=True,
                timeout=300
            )

            if result.returncode == 0:
                self.venv_python = venv_path / "bin" / "python"
                return True

            return False

        except Exception as e:
            print(f"      创建虚拟环境失败: {e}")
            return False

    def _install_dependencies(self, work_dir: Path) -> bool:
        """安装基础依赖"""
        try:
            venv_python = work_dir / self.env_dir / "bin" / "python"

            base_packages = [
                "numpy", "torch", "transformers", "datasets",
                "accelerate", "scikit-learn", "pandas", "matplotlib"
            ]

            result = subprocess.run(
                [str(venv_python), "-m", "pip", "install", "--upgrade", "pip"],
                capture_output=True,
                text=True,
                timeout=300
            )

            if result.returncode != 0:
                print(f"      pip升级失败: {result.stderr}")

            for package in base_packages:
                result = subprocess.run(
                    [str(venv_python), "-m", "pip", "install", package],
                    capture_output=True,
                    text=True,
                    timeout=600
                )

                if result.returncode == 0:
                    print(f"      ✓ 安装 {package}")
                else:
                    print(f"      ⚠️ 安装 {package} 失败")

            return True

        except Exception as e:
            print(f"      安装依赖失败: {e}")
            return False

    def clone_repository(self, repo_url: str, target_dir: Path) -> bool:
        """克隆GitHub仓库"""
        print(f"\n📥 克隆仓库: {repo_url}")

        try:
            if target_dir.exists():
                print(f"   仓库已存在，跳过克隆")
                return True

            result = subprocess.run(
                ["git", "clone", repo_url, str(target_dir)],
                capture_output=True,
                text=True,
                timeout=600
            )

            if result.returncode == 0:
                print(f"   ✓ 克隆成功")
                return True
            else:
                print(f"   ⚠️ 克隆失败: {result.stderr}")
                return False

        except Exception as e:
            print(f"   ⚠️ 克隆失败: {e}")
            return False

    def read_readme(self, repo_dir: Path) -> str:
        """读取README文件"""
        readme_files = ["README.md", "README.txt", "readme.md"]

        for readme_file in readme_files:
            readme_path = repo_dir / readme_file
            if readme_path.exists():
                try:
                    content = readme_path.read_text(encoding='utf-8')
                    print(f"\n📄 读取 {readme_file} ({len(content)} 字符)")
                    return content
                except Exception as e:
                    print(f"   ⚠️ 读取失败: {e}")

        print(f"   ⚠️ 未找到README文件")
        return ""

    def verify_code(self, repo_dir: Path, env_info: Dict) -> Dict:
        """验证代码是否能正常运行"""
        print("\n🔍 验证代码...")

        verification = {
            "status": "pending",
            "test_passed": False,
            "errors": [],
            "output": ""
        }

        try:
            venv_python = Path(env_info["work_dir"]) / self.env_dir / "bin" / "python"

            if not venv_python.exists():
                verification["status"] = "failed"
                verification["errors"].append("虚拟环境不存在")
                return verification

            requirements_file = repo_dir / "requirements.txt"
            if requirements_file.exists():
                print(f"   📦 安装项目依赖...")

                result = subprocess.run(
                    [str(venv_python), "-m", "pip", "install", "-r", str(requirements_file)],
                    capture_output=True,
                    text=True,
                    timeout=1800
                )

                if result.returncode == 0:
                    print(f"   ✓ 依赖安装成功")
                else:
                    print(f"   ⚠️ 依赖安装失败")
                    verification["errors"].append(f"依赖安装失败: {result.stderr[:200]}")

            test_files = list(repo_dir.glob("test*.py")) + list(repo_dir.glob("*_test.py"))
            if test_files:
                print(f"   🧪 运行测试...")

                test_file = test_files[0]
                result = subprocess.run(
                    [str(venv_python), str(test_file)],
                    capture_output=True,
                    text=True,
                    timeout=600
                )

                verification["output"] = result.stdout + result.stderr

                if result.returncode == 0:
                    verification["status"] = "success"
                    verification["test_passed"] = True
                    print(f"   ✓ 测试通过")
                else:
                    verification["status"] = "failed"
                    verification["errors"].append(f"测试失败: {result.stderr[:200]}")
                    print(f"   ⚠️ 测试失败")
            else:
                print(f"   ℹ️ 未找到测试文件")
                verification["status"] = "skipped"
                verification["test_passed"] = None

        except subprocess.TimeoutExpired:
            verification["status"] = "timeout"
            verification["errors"].append("执行超时")
            print(f"   ⚠️ 执行超时")
        except Exception as e:
            verification["status"] = "error"
            verification["errors"].append(f"执行错误: {str(e)}")
            print(f"   ⚠️ 执行错误: {e}")

        return verification

    def reproduce_experiment(self, repo_dir: Path, experiment_name: str, env_info: Dict) -> Dict:
        """复现特定实验"""
        print(f"\n🔬 复现实验: {experiment_name}")

        repro_result = {
            "experiment_name": experiment_name,
            "status": "pending",
            "result": {},
            "expected": {},
            "comparison": {},
            "issues": [],
            "solutions": []
        }

        try:
            venv_python = Path(env_info["work_dir"]) / self.env_dir / "bin" / "python"

            example_files = list(repo_dir.glob("*example*.py")) + \
                          list(repo_dir.glob("*demo*.py")) + \
                          list(repo_dir.glob("run*.py"))

            if example_files:
                example_file = example_files[0]
                print(f"   📝 运行示例: {example_file.name}")

                result = subprocess.run(
                    [str(venv_python), str(example_file)],
                    capture_output=True,
                    text=True,
                    timeout=1800
                )

                repro_result["result"]["output"] = result.stdout
                repro_result["result"]["return_code"] = result.returncode

                if result.returncode == 0:
                    repro_result["status"] = "success"
                    print(f"   ✓ 实验复现成功")
                else:
                    repro_result["status"] = "failed"
                    repro_result["issues"].append(f"执行失败: {result.stderr[:200]}")
                    print(f"   ⚠️ 执行失败")
            else:
                repro_result["status"] = "skipped"
                repro_result["issues"].append("未找到示例文件")
                print(f"   ℹ️ 未找到示例文件")

        except Exception as e:
            repro_result["status"] = "error"
            repro_result["issues"].append(f"执行错误: {str(e)}")
            print(f"   ⚠️ 执行错误: {e}")

        return repro_result

    def generate_reproduction_report(self, env_info: Dict, verification: Dict,
                                    experiments: List[Dict]) -> str:
        """生成复现报告"""
        report = "\n## 实验复现信息\n\n"

        report += f"- **复现状态**：{self._get_status_text(verification['status'])}\n"
        report += f"- **复现日期**：{datetime.now().strftime('%Y-%m-%d')}\n"
        report += f"- **复现环境**：\n"
        report += f"  - Python版本：{env_info['python_version']}\n"
        report += f"  - 工作目录：{env_info['work_dir']}\n"
        report += f"  - 仓库地址：{env_info['repo_url']}\n\n"

        report += "### 环境设置\n\n"
        report += f"- 虚拟环境：{self.env_dir}\n"
        report += f"- 设置状态：{env_info['setup_status']}\n\n"

        report += "### 代码验证\n\n"
        report += f"- 验证状态：{verification['status']}\n"
        report += f"- 测试通过：{'是' if verification['test_passed'] else '否'}\n"

        if verification['errors']:
            report += "- 错误信息：\n"
            for error in verification['errors']:
                report += f"  - {error}\n"

        report += "\n### 实验复现\n\n"
        for exp in experiments:
            report += f"#### {exp['experiment_name']}\n\n"
            report += f"- 状态：{self._get_status_text(exp['status'])}\n"

            if exp['issues']:
                report += "- 遇到的问题：\n"
                for issue in exp['issues']:
                    report += f"  - {issue}\n"

            if exp['solutions']:
                report += "- 解决方案：\n"
                for solution in exp['solutions']:
                    report += f"  - {solution}\n"

        report += "\n### 复现结论\n\n"
        success_count = sum(1 for exp in experiments if exp['status'] == 'success')
        report += f"- 成功复现：{success_count}/{len(experiments)} 个实验\n"

        if success_count == len(experiments):
            report += "- 总体评价：✅ 论文方法可以成功复现\n"
        elif success_count > 0:
            report += "- 总体评价：⚠️ 部分实验可以复现\n"
        else:
            report += "- 总体评价：❌ 未能成功复现\n"

        return report

    def _get_status_text(self, status: str) -> str:
        """获取状态文本"""
        status_map = {
            "success": "✅ 成功",
            "failed": "❌ 失败",
            "pending": "⏳ 进行中",
            "skipped": "⏭️ 跳过",
            "error": "⚠️ 错误",
            "timeout": "⏱️ 超时"
        }
        return status_map.get(status, status)

    def reproduce(self, paper_info: Dict) -> Dict:
        """执行完整的复现流程"""
        print("=" * 60)
        print("🔬 实验复现模块")
        print("=" * 60)

        print(f"\n📄 论文: {paper_info.get('title', 'Unknown')}")

        github_url = paper_info.get("github_url", "")
        if not github_url:
            print("\n⚠️ 无官方代码，跳过复现")
            return {
                "has_code": False,
                "reproduction_report": "## 实验复现\n\n⚠️ 无官方代码，无法复现"
            }

        work_dir = self.base_path / "06_tools" / "paper-reader" / "reproductions"
        work_dir = work_dir / f"temp_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        work_dir.mkdir(parents=True, exist_ok=True)

        print(f"\n📂 工作目录: {work_dir}")

        if not self.clone_repository(github_url, work_dir):
            return {
                "has_code": True,
                "reproduction_report": f"## 实验复现\n\n❌ 仓库克隆失败"
            }

        readme_content = self.read_readme(work_dir)

        env_info = self.setup_environment(github_url, work_dir)

        verification = self.verify_code(work_dir, env_info)

        experiments = []
        max_experiments = self.repro_config["max_experiments_to_reproduce"]
        for i in range(max_experiments):
            exp = self.reproduce_experiment(
                work_dir,
                f"实验 {i+1}",
                env_info
            )
            experiments.append(exp)

            if exp['status'] != 'success':
                break

        reproduction_report = self.generate_reproduction_report(
            env_info, verification, experiments
        )

        print("\n" + "=" * 60)
        print("✅ 复现完成")
        print("=" * 60)

        return {
            "has_code": True,
            "env_info": env_info,
            "verification": verification,
            "experiments": experiments,
            "reproduction_report": reproduction_report
        }


def main():
    """主函数"""
    config_path = Path(__file__).parent.parent / "config/config.json"
    reproducer = PaperReproducer(str(config_path))

    print("🔬 论文实验复现工具")
    print("\n使用方法:")
    print("1. 准备论文信息（包含github_url）")
    print("2. 调用 reproducer.reproduce(paper_info)")
    print("3. 获取复现报告")


if __name__ == "__main__":
    main()
