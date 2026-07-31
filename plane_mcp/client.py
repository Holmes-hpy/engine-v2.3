#!/usr/bin/env python3
"""
Plane MCP HTTP 客户端
通过 HTTP SSE 协议调用 Plane MCP Server 的所有工具
"""
import json
import os
import sys
import urllib.request
import urllib.error
from pathlib import Path
from typing import Any, Optional


def _load_dotenv():
    """加载 .env 文件到环境变量（不覆盖已有值）"""
    env_path = Path(__file__).parent / ".env"
    if not env_path.exists():
        return
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                k, v = line.split("=", 1)
                k, v = k.strip(), v.strip()
                if k not in os.environ:
                    os.environ[k] = v


_load_dotenv()


class PlaneMCPClient:
    """Plane MCP HTTP 客户端"""

    def __init__(self, api_key: str = None, workspace: str = None, endpoint: str = None):
        self.api_key = api_key or os.environ.get("PLANE_API_KEY", "")
        self.workspace = workspace or os.environ.get("PLANE_WORKSPACE", "mas")
        self.endpoint = endpoint or os.environ.get(
            "PLANE_MCP_ENDPOINT",
            "https://mcp-plane.mas.aicookbook.site/http/api-key/mcp"
        )
        self._request_id = 0

    def _next_id(self) -> int:
        self._request_id += 1
        return self._request_id

    def _call(self, method: str, params: dict = None) -> dict:
        """底层 MCP 协议调用"""
        payload = {
            "jsonrpc": "2.0",
            "id": self._next_id(),
            "method": method,
            "params": params or {}
        }
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            self.endpoint,
            data=data,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "x-workspace-slug": self.workspace,
                "Content-Type": "application/json",
                "Accept": "application/json, text/event-stream",
            },
            method="POST"
        )
        try:
            with urllib.request.urlopen(req) as resp:
                body = resp.read().decode("utf-8")
        except urllib.error.HTTPError as e:
            return {"error": f"HTTP {e.code}: {e.reason}"}
        except urllib.error.URLError as e:
            return {"error": f"URL Error: {e.reason}"}

        # 解析 SSE 响应
        for line in body.split("\n"):
            if line.startswith("data:"):
                try:
                    return json.loads(line[5:].strip())
                except json.JSONDecodeError:
                    continue
        return {"error": "No valid SSE response", "raw": body[:500]}

    def call_tool(self, tool_name: str, arguments: dict = None) -> dict:
        """调用 Plane MCP 工具"""
        return self._call("tools/call", {
            "name": tool_name,
            "arguments": arguments or {}
        })

    def list_tools(self) -> list:
        """列出所有可用工具"""
        result = self._call("tools/list")
        if "result" in result and "tools" in result["result"]:
            return result["result"]["tools"]
        return []

    def get_result(self, response: dict) -> Any:
        """从 MCP 响应中提取结构化结果"""
        if "error" in response:
            return {"error": response["error"]}
        if "result" in response:
            result = response["result"]
            if "structuredContent" in result:
                return result["structuredContent"]
            if "content" in result and result["content"]:
                for item in result["content"]:
                    if item.get("type") == "text":
                        try:
                            return json.loads(item["text"])
                        except json.JSONDecodeError:
                            return item["text"]
        return response

    # ========== 便捷方法 ==========

    def list_projects(self):
        """列出所有项目"""
        return self.get_result(self.call_tool("list_projects"))

    def list_work_items(self, project_id: str, **kwargs):
        """列出工作项"""
        args = {"project_id": project_id, **kwargs}
        return self.get_result(self.call_tool("list_work_items", args))

    def create_work_item(self, project_id: str, name: str, **kwargs):
        """创建工作项"""
        args = {"project_id": project_id, "name": name, **kwargs}
        return self.get_result(self.call_tool("create_work_item", args))

    def update_work_item(self, project_id: str, work_item_id: str, **kwargs):
        """更新工作项"""
        args = {"project_id": project_id, "work_item_id": work_item_id, **kwargs}
        return self.get_result(self.call_tool("update_work_item", args))

    def search_work_items(self, query: str):
        """搜索工作项"""
        return self.get_result(self.call_tool("search_work_items", {"query": query}))

    def get_me(self):
        """获取当前用户信息"""
        return self.get_result(self.call_tool("get_me"))

    def list_cycles(self, project_id: str, **kwargs):
        """列出周期"""
        return self.get_result(self.call_tool("list_cycles", {"project_id": project_id, **kwargs}))

    def list_modules(self, project_id: str, **kwargs):
        """列出模块"""
        return self.get_result(self.call_tool("list_modules", {"project_id": project_id, **kwargs}))

    def list_labels(self, project_id: str, **kwargs):
        """列出标签"""
        return self.get_result(self.call_tool("list_labels", {"project_id": project_id, **kwargs}))

    def list_states(self, project_id: str, **kwargs):
        """列出状态"""
        return self.get_result(self.call_tool("list_states", {"project_id": project_id, **kwargs}))

    def get_workspace_members(self, **kwargs):
        """获取工作区成员"""
        return self.get_result(self.call_tool("get_workspace_members", kwargs))

    def list_pages(self, project_id: str = None, **kwargs):
        """列出页面"""
        args = {}
        if project_id:
            args["project_id"] = project_id
        args.update(kwargs)
        return self.get_result(self.call_tool("list_pages", args))


# ========== 命令行入口 ==========
if __name__ == "__main__":
    client = PlaneMCPClient()

    if len(sys.argv) < 2:
        print("用法: python client.py <tool_name> [key=value ...]")
        print("示例: python client.py list_projects")
        print("      python client.py list_work_items project_id=xxx")
        sys.exit(1)

    tool_name = sys.argv[1]
    args = {}
    for arg in sys.argv[2:]:
        if "=" in arg:
            k, v = arg.split("=", 1)
            args[k] = v

    result = client.call_tool(tool_name, args)
    parsed = client.get_result(result)
    print(json.dumps(parsed, indent=2, ensure_ascii=False))