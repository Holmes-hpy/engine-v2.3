"""
Plane MCP 集成模块
通过 HTTP SSE 协议调用 Plane MCP Server，实现项目管理自动化
"""

from .client import PlaneMCPClient

__all__ = ["PlaneMCPClient"]