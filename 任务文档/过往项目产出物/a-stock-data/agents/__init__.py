from pathlib import Path

AGENTS_DIR = Path(__file__).parent

AGENT_LIST = [
    'Serenity瓶颈投资分析专家',
    '知识图谱打标专家',
    '公告深度解读专家',
    '红队风险评估专家',
    '市场实时监控专家',
    '数据采集专家',
]

def get_agent_prompt(agent_name: str) -> str:
    """获取指定Agent的提示词"""
    prompt_file = AGENTS_DIR / f"{agent_name}_agent.md"
    if prompt_file.exists():
        return prompt_file.read_text(encoding='utf-8')
    return ""

def list_agents() -> list:
    """列出所有可用的Agent"""
    return AGENT_LIST

__all__ = [
    'AGENTS_DIR',
    'AGENT_LIST',
    'get_agent_prompt',
    'list_agents',
]