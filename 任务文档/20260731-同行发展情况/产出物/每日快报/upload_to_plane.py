#!/usr/bin/env python3
"""
每日快报 → Plane 自动上传工具
============================

功能：将本地生成的每日快报 Markdown 文件上传到 Plane 项目的"科技快报"模块。

用法：
    python3 upload_daily_briefing.py                    # 上传今天的快报
    python3 upload_daily_briefing.py --date 2026-08-04   # 上传指定日期的快报
    python3 upload_daily_briefing.py --dry-run          # 预览，不上传

依赖：
    - plane_mcp 客户端（项目根目录 plane_mcp/）
    - markdown 库（pip install markdown）

配置：
    所有配置通过环境变量或 .env 文件读取，凭证不硬编码。
    PLANE_API_KEY: Plane API Key
    PLANE_WORKSPACE: 工作区 slug（默认 mas）
    PLANE_PROJECT_ID: 项目 ID（产品交付）
    PLANE_MODULE_ID: 模块 ID（科技快报）

作者：发动机V2.3项目
日期：2026-08-04
"""

import sys
import os
import json
import argparse
import markdown
from pathlib import Path
from datetime import datetime, date

# ========== 路径配置 ==========
# 向上查找项目根目录（包含 plane_mcp/ 的目录）
def _find_project_root() -> Path:
    current = Path(__file__).resolve().parent
    for _ in range(10):  # 最多向上找10层
        if (current / "plane_mcp").exists() and (current / "rules").exists():
            return current
        current = current.parent
    raise RuntimeError("找不到项目根目录（未找到 plane_mcp/ 和 rules/ 目录）")

PROJECT_ROOT = _find_project_root()
PLANE_MCP_DIR = PROJECT_ROOT / "plane_mcp"
DAILY_BRIEFING_DIR = Path(__file__).resolve().parent

# 将 plane_mcp 加入路径
sys.path.insert(0, str(PLANE_MCP_DIR))

from client import PlaneMCPClient  # noqa: E402


# ========== 默认配置 ==========
DEFAULT_PROJECT_ID = "458341b9-94b6-4419-97b9-5d5f8073d6d1"   # 产品交付
DEFAULT_MODULE_ID = "1cd55d8a-8c64-4450-bd54-9446ed3f577c"    # 科技快报


def load_env():
    """加载 .env 文件"""
    env_path = PLANE_MCP_DIR / ".env"
    if not env_path.exists():
        return
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            k, v = k.strip(), v.strip()
            if k not in os.environ:
                os.environ[k] = v


def get_briefing_path(target_date: str) -> Path:
    """获取指定日期的快报文件路径"""
    filename = f"每日快报_{target_date}.md"
    filepath = DAILY_BRIEFING_DIR / filename
    if not filepath.exists():
        raise FileNotFoundError(f"未找到快报文件: {filepath}")
    return filepath


def md_to_html(md_content: str) -> str:
    """Markdown 转 HTML"""
    return markdown.markdown(
        md_content,
        extensions=["tables", "fenced_code", "toc", "nl2br", "sane_lists"]
    )


def upload_to_plane(client, project_id: str, module_id: str,
                   title: str, md_content: str, dry_run: bool = False) -> dict:
    """
    上传快报到 Plane 科技快报模块

    Args:
        client: PlaneMCPClient 实例
        project_id: 项目 ID
        module_id: 模块 ID
        title: 工作项标题
        md_content: Markdown 内容
        dry_run: 预览模式，不上传

    Returns:
        dict: {success, work_item_id, title, message}
    """
    html_content = md_to_html(md_content)

    # 内容长度限制保护（Plane description_html 可能有上限）
    if len(html_content) > 100000:
        html_content = html_content[:100000] + (
            '<p style="color:#999;">...内容过长已截断，完整内容请参考本地文件</p>'
        )

    if dry_run:
        return {
            "success": True,
            "work_item_id": "dry-run",
            "title": title,
            "message": f"预览模式：将创建工作项 '{title}'，HTML 长度 {len(html_content)} 字符",
            "html_length": len(html_content),
        }

    # 1. 创建工作项
    result = client.create_work_item(
        project_id=project_id,
        name=title,
        description_html=html_content,
        priority="medium",
    )

    if not isinstance(result, dict) or "id" not in result:
        return {
            "success": False,
            "work_item_id": None,
            "title": title,
            "message": f"创建工作项失败: {str(result)[:200]}",
        }

    work_item_id = result["id"]

    # 2. 关联到模块
    module_result = client.call_tool("manage_module_work_items", {
        "project_id": project_id,
        "module_id": module_id,
        "add_ids": [work_item_id],
    })
    module_parsed = client.get_result(module_result)
    module_ok = not isinstance(module_parsed, str) or "Error" not in module_parsed

    return {
        "success": True,
        "work_item_id": work_item_id,
        "title": title,
        "message": f"上传成功，工作项 ID: {work_item_id}" + ("" if module_ok else "（模块关联可能失败）"),
        "module_attached": module_ok,
        "html_length": len(html_content),
    }


def main():
    parser = argparse.ArgumentParser(description="每日快报上传到 Plane 科技快报模块")
    parser.add_argument("--date", default=None,
                        help="目标日期 (YYYY-MM-DD)，默认今天")
    parser.add_argument("--title", default=None,
                        help="自定义工作项标题，默认使用日期")
    parser.add_argument("--project-id", default=None,
                        help=f"Plane 项目 ID，默认 {DEFAULT_PROJECT_ID}")
    parser.add_argument("--module-id", default=None,
                        help=f"Plane 模块 ID，默认 {DEFAULT_MODULE_ID}")
    parser.add_argument("--dry-run", action="store_true",
                        help="预览模式，不上传")
    parser.add_argument("--verify", action="store_true",
                        help="上传后验证模块下的工作项列表")
    args = parser.parse_args()

    # 加载环境变量
    load_env()

    # 确定日期
    if args.date:
        target_date = args.date
    else:
        target_date = date.today().strftime("%Y-%m-%d")

    # 获取配置
    project_id = args.project_id or os.environ.get("PLANE_PROJECT_ID", DEFAULT_PROJECT_ID)
    module_id = args.module_id or os.environ.get("PLANE_MODULE_ID", DEFAULT_MODULE_ID)

    # 读取快报文件
    try:
        filepath = get_briefing_path(target_date)
        md_content = filepath.read_text(encoding="utf-8")
    except FileNotFoundError as e:
        print(f"❌ {e}")
        sys.exit(1)

    # 标题
    if args.title:
        title = args.title
    else:
        title = f"【{target_date}】同行每日快报"

    print(f"📰 每日快报上传工具")
    print(f"   日期: {target_date}")
    print(f"   文件: {filepath.name}")
    print(f"   标题: {title}")
    print(f"   项目 ID: {project_id}")
    print(f"   模块 ID: {module_id}")
    print(f"   模式: {'预览 (dry-run)' if args.dry_run else '正式上传'}")
    print()

    # 初始化客户端
    client = PlaneMCPClient()

    # 上传
    print("🚀 开始上传...")
    result = upload_to_plane(
        client=client,
        project_id=project_id,
        module_id=module_id,
        title=title,
        md_content=md_content,
        dry_run=args.dry_run,
    )

    if result["success"]:
        print(f"✅ {result['message']}")
        print(f"   工作项 ID: {result['work_item_id']}")
        print(f"   HTML 长度: {result.get('html_length', '?')} 字符")
    else:
        print(f"❌ {result['message']}")
        sys.exit(1)

    # 验证
    if args.verify and not args.dry_run:
        print()
        print("🔍 验证模块下的工作项...")
        verify_result = client.call_tool("list_module_work_items", {
            "project_id": project_id,
            "module_id": module_id,
            "per_page": 5,
        })
        verified = client.get_result(verify_result)
        if isinstance(verified, dict) and "results" in verified:
            items = verified["results"]
            total = verified.get("total_count", "?")
            print(f"   模块下共 {total} 个工作项（最新5条）:")
            for item in items:
                state_name = ""
                state = item.get("state")
                if isinstance(state, dict):
                    state_name = state.get("name", "")
                print(f"     - {item['name']} [{state_name}]")
        else:
            print(f"   验证结果: {str(verified)[:100]}")

    print()
    print("🎉 完成！")


if __name__ == "__main__":
    main()
