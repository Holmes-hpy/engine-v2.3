"""
LangGraph 可视化编排演示 — 智能文档处理系统
=============================================
这个 Demo 演示了 LangGraph 全部五种核心编排能力：
1. 串行执行：文档接收 → 预处理 → 分类
2. 条件分支：根据文档类型走不同处理流程
3. 并行执行：内容提取 + 风险分析 + 摘要生成
4. 循环：质量检查不通过 → 重试
5. 人机协同：关键审批节点暂停等人工确认

面向产品经理设计，每个节点都有清晰的中文说明。
"""

import operator
import random
from typing import Annotated, TypedDict, Literal

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import interrupt, Command


# ============================================================
# 一、状态定义（State）
# ============================================================
class DocState(TypedDict):
    """文档处理工作流共享状态 — 相当于流水线上的"随工单" """
    # 文档信息
    doc_title: str
    doc_content: str
    doc_type: str              # 合同 / 报告 / 邮件 / 未知
    # 处理结果
    preprocessed: bool
    extracted_info: Annotated[dict, operator.ior]  # 用 | 合并，保留所有键
    risk_level: str            # 低 / 中 / 高
    risk_detail: str
    summary: str
    # 流程控制
    quality_score: float       # 0-100，质量评分
    retry_count: int           # 重试次数
    # 审批
    human_approved: bool
    approval_comment: str
    # 日志
    logs: Annotated[list, operator.add]  # 用 + 累加


# ============================================================
# 二、节点函数（Nodes）— 每个函数代表一个"工位"
# ============================================================

def node_receive_doc(state: DocState) -> dict:
    """【串行·第1步】文档接收：接收原始文档，记录日志"""
    return {
        "logs": [f"[接收] 收到文档: 《{state['doc_title']}》"],
        "preprocessed": False,
        "retry_count": 0,
        "human_approved": False,
    }


def node_preprocess(state: DocState) -> dict:
    """【串行·第2步】预处理：清洗文档格式，去除乱码"""
    content = state["doc_content"]
    # 模拟预处理：去除首尾空白
    cleaned = content.strip()
    return {
        "doc_content": cleaned,
        "preprocessed": True,
        "logs": [f"[预处理] 文档清洗完成，原始长度 {len(content)} → 清洗后 {len(cleaned)}"],
    }


def node_classify(state: DocState) -> dict:
    """【串行·第3步】文档分类：根据关键词判断文档类型"""
    content = state["doc_content"]
    title = state["doc_title"]

    if "合同" in title or "协议" in title or "甲方" in content or "乙方" in content:
        doc_type = "合同"
    elif "报告" in title or "分析" in title or "数据" in title:
        doc_type = "报告"
    elif "邮件" in title or "通知" in title or "公告" in title:
        doc_type = "邮件"
    else:
        doc_type = "未知"

    return {
        "doc_type": doc_type,
        "logs": [f"[分类] 文档类型判定为: {doc_type}"],
    }


# ============================================================
# 三、条件路由（Conditional Edges）— 根据文档类型分流
# ============================================================

def route_by_doc_type(state: DocState) -> Literal["handle_contract", "handle_report", "handle_mail", "handle_unknown"]:
    """【条件分支】根据文档类型，路由到不同的处理节点"""
    doc_type = state["doc_type"]
    mapping = {
        "合同": "handle_contract",
        "报告": "handle_report",
        "邮件": "handle_mail",
    }
    return mapping.get(doc_type, "handle_unknown")


# ============================================================
# 四、分支处理节点
# ============================================================

def node_handle_contract(state: DocState) -> dict:
    """合同处理：提取甲乙方、金额、条款"""
    return {
        "extracted_info": {"合同类型": "采购合同"},
        "logs": [f"[合同处理] 进入合同专用处理流程，提取甲乙方信息、金额条款"],
    }


def node_handle_report(state: DocState) -> dict:
    """报告处理：提取数据指标、结论"""
    return {
        "extracted_info": {"报告类型": "数据分析报告"},
        "logs": [f"[报告处理] 进入报告专用处理流程，提取数据指标和结论"],
    }


def node_handle_mail(state: DocState) -> dict:
    """邮件处理：提取发件人、收件人、主题"""
    return {
        "extracted_info": {"邮件类型": "工作通知"},
        "logs": [f"[邮件处理] 进入邮件专用处理流程，提取收发人和主题"],
    }


def node_handle_unknown(state: DocState) -> dict:
    """未知文档处理：尝试通用提取"""
    return {
        "extracted_info": {"文档类型": "未知/通用"},
        "logs": [f"[未知处理] 文档类型无法识别，进入通用处理流程"],
    }


# ============================================================
# 五、并行处理节点（Parallel / Fan-out）
# ============================================================

def node_extract_content(state: DocState) -> dict:
    """【并行·第1路】内容提取：提取文档关键信息"""
    return {
        "extracted_info": {"关键字段": f"从《{state['doc_title']}》提取的核心内容"},
        "logs": [f"[并行-内容提取] 正在提取文档关键信息..."],
    }


def node_analyze_risk(state: DocState) -> dict:
    """【并行·第2路】风险分析：评估文档风险等级"""
    score = random.randint(0, 100)
    if score < 30:
        risk = "低"
        detail = "无明显风险点"
    elif score < 70:
        risk = "中"
        detail = "存在部分需关注条款"
    else:
        risk = "高"
        detail = "发现高风险条款，建议人工复核"

    return {
        "risk_level": risk,
        "risk_detail": detail,
        "logs": [f"[并行-风险分析] 风险评分 {score}，等级: {risk} — {detail}"],
    }


def node_generate_summary(state: DocState) -> dict:
    """【并行·第3路】摘要生成：生成文档摘要"""
    title = state["doc_title"]
    dtype = state["doc_type"]
    summary = f"《{title}》是一份{dtype}类文档，已完成自动处理。"
    return {
        "summary": summary,
        "logs": [f"[并行-摘要生成] 摘要: {summary}"],
    }


# ============================================================
# 六、质量检查 & 循环（Loop）
# ============================================================

def node_quality_check(state: DocState) -> dict:
    """质量检查：评估处理结果质量，决定是否需要重试"""
    # 模拟质量评分
    score = 75 + random.randint(0, 25)  # 75-100 分
    return {
        "quality_score": score,
        "logs": [f"[质量检查] 评分: {score}/100"],
    }


def route_quality(state: DocState) -> Literal["parallel_processing", "human_approval"]:
    """【循环条件】质量不达标且未超过重试上限 → 循环重试"""
    if state["quality_score"] < 85 and state["retry_count"] < 3:
        return "parallel_processing"
    return "human_approval"


def node_retry_count(state: DocState) -> dict:
    """重试计数器：记录重试次数"""
    new_count = state["retry_count"] + 1
    return {
        "retry_count": new_count,
        "logs": [f"[重试] 第 {new_count} 次重试..."],
    }


# ============================================================
# 七、人机协同（Human-in-the-Loop）
# ============================================================

def node_human_approval(state: DocState) -> dict:
    """【人机协同】暂停等待人工审批"""
    # interrupt() 会在此处暂停，等待人工介入
    approval = interrupt({
        "message": f"请审批文档《{state['doc_title']}》的处理结果",
        "文档类型": state["doc_type"],
        "风险等级": state["risk_level"],
        "风险详情": state["risk_detail"],
        "摘要": state["summary"],
        "质量评分": state["quality_score"],
        "提取信息": state["extracted_info"],
        "操作": "请输入 'approve' 批准 或 'reject' 驳回",
    })

    if isinstance(approval, str) and approval.lower() == "approve":
        return {
            "human_approved": True,
            "approval_comment": "人工审批通过",
            "logs": [f"[审批] ✅ 人工审批通过"],
        }
    else:
        return {
            "human_approved": False,
            "approval_comment": f"人工审批驳回: {approval}",
            "logs": [f"[审批] ❌ 人工审批驳回"],
        }


def route_after_approval(state: DocState) -> Literal["node_archive", "node_reject"]:
    """审批后路由：通过 → 归档，驳回 → 拒绝处理"""
    if state["human_approved"]:
        return "node_archive"
    return "node_reject"


def node_archive(state: DocState) -> dict:
    """归档：文档处理完成，归档保存"""
    return {
        "logs": [f"[归档] ✅ 文档《{state['doc_title']}》处理完成，已归档。"
                f"类型={state['doc_type']}, 风险={state['risk_level']}, 重试={state['retry_count']}次"],
    }


def node_reject(state: DocState) -> dict:
    """拒绝处理：审批不通过，记录原因"""
    return {
        "logs": [f"[拒绝] ❌ 文档《{state['doc_title']}》审批未通过，原因: {state['approval_comment']}"],
    }


# ============================================================
# 八、构建图（Graph）— 把所有节点和边组织起来
# ============================================================

def build_graph() -> StateGraph:
    """构建完整的文档处理工作流图"""
    builder = StateGraph(DocState)

    # --- 添加节点 ---
    # 串行链路节点
    builder.add_node("receive_doc", node_receive_doc)
    builder.add_node("preprocess", node_preprocess)
    builder.add_node("classify", node_classify)

    # 分支处理节点
    builder.add_node("handle_contract", node_handle_contract)
    builder.add_node("handle_report", node_handle_report)
    builder.add_node("handle_mail", node_handle_mail)
    builder.add_node("handle_unknown", node_handle_unknown)

    # 并行处理节点
    builder.add_node("extract_content", node_extract_content)
    builder.add_node("analyze_risk", node_analyze_risk)
    builder.add_node("generate_summary", node_generate_summary)

    # 质量检查 & 循环
    builder.add_node("quality_check", node_quality_check)
    builder.add_node("retry_count", node_retry_count)

    # 人机协同
    builder.add_node("human_approval", node_human_approval)
    builder.add_node("archive", node_archive)
    builder.add_node("reject", node_reject)

    # --- 添加边 ---
    # 串行链路：receive → preprocess → classify
    builder.add_edge(START, "receive_doc")
    builder.add_edge("receive_doc", "preprocess")
    builder.add_edge("preprocess", "classify")

    # 条件分支：根据文档类型路由
    builder.add_conditional_edges(
        "classify",
        route_by_doc_type,
        {
            "handle_contract": "handle_contract",
            "handle_report": "handle_report",
            "handle_mail": "handle_mail",
            "handle_unknown": "handle_unknown",
        }
    )

    # 所有分支处理完后，汇聚到并行处理
    builder.add_edge("handle_contract", "extract_content")
    builder.add_edge("handle_contract", "analyze_risk")
    builder.add_edge("handle_contract", "generate_summary")
    builder.add_edge("handle_report", "extract_content")
    builder.add_edge("handle_report", "analyze_risk")
    builder.add_edge("handle_report", "generate_summary")
    builder.add_edge("handle_mail", "extract_content")
    builder.add_edge("handle_mail", "analyze_risk")
    builder.add_edge("handle_mail", "generate_summary")
    builder.add_edge("handle_unknown", "extract_content")
    builder.add_edge("handle_unknown", "analyze_risk")
    builder.add_edge("handle_unknown", "generate_summary")

    # 并行汇聚到质量检查
    builder.add_edge("extract_content", "quality_check")
    builder.add_edge("analyze_risk", "quality_check")
    builder.add_edge("generate_summary", "quality_check")

    # 质量检查 → 条件路由（循环 or 继续）
    builder.add_conditional_edges(
        "quality_check",
        route_quality,
        {
            "parallel_processing": "retry_count",
            "human_approval": "human_approval",
        }
    )

    # 重试 → 回到并行处理
    builder.add_edge("retry_count", "extract_content")
    builder.add_edge("retry_count", "analyze_risk")
    builder.add_edge("retry_count", "generate_summary")

    # 审批 → 条件路由
    builder.add_conditional_edges(
        "human_approval",
        route_after_approval,
        {
            "node_archive": "archive",
            "node_reject": "reject",
        }
    )

    # 终点
    builder.add_edge("archive", END)
    builder.add_edge("reject", END)

    return builder


# ============================================================
# 九、编译图 & 运行入口
# ============================================================

# 编译图（LangGraph API 平台自带持久化，无需自定义 checkpointer）
graph = build_graph().compile()

# ============================================================
# 如果直接运行此文件，执行一个快速演示
# ============================================================
if __name__ == "__main__":
    print("=" * 60)
    print("LangGraph 智能文档处理系统 — 快速演示")
    print("=" * 60)

    # 独立运行时使用内存检查点
    demo_checkpointer = InMemorySaver()
    demo_graph = build_graph().compile(checkpointer=demo_checkpointer)

    # 测试用例：一份合同
    test_input = {
        "doc_title": "XX采购合同",
        "doc_content": "甲方：XX公司\n乙方：YY供应商\n合同金额：100万元\n交货日期：2026年8月",
        "doc_type": "",
        "extracted_info": {},
        "risk_level": "",
        "risk_detail": "",
        "summary": "",
        "quality_score": 0,
        "retry_count": 0,
        "human_approved": False,
        "approval_comment": "",
        "logs": [],
        "preprocessed": False,
    }

    config = {"configurable": {"thread_id": "demo-001"}}

    # 第一次执行：会停在 human_approval 节点等待审批
    print("\n>>> 第一轮执行（会停在审批节点）...")
    try:
        result = demo_graph.invoke(test_input, config)
        print("结果:", result.get("logs", [])[-3:])
    except Exception as e:
        print(f"预期中断: {e}")

    # 模拟人工审批通过
    print("\n>>> 人工审批：通过！")
    from langgraph.types import Command
    demo_graph.invoke(Command(resume="approve"), config)

    # 获取最终状态
    final_state = demo_graph.get_state(config)
    print("\n>>> 最终状态:")
    print(f"  文档类型: {final_state.values.get('doc_type', 'N/A')}")
    print(f"  风险等级: {final_state.values.get('risk_level', 'N/A')}")
    print(f"  摘要: {final_state.values.get('summary', 'N/A')}")
    print(f"  重试次数: {final_state.values.get('retry_count', 'N/A')}")
    print(f"  是否批准: {final_state.values.get('human_approved', 'N/A')}")
    print(f"\n>>> 完整日志:")
    for log in final_state.values.get("logs", []):
        print(f"  {log}")
    print("\n" + "=" * 60)
    print("演示完成！启动 langgraph dev 可在 Studio 中可视化查看此图。")
    print("=" * 60)