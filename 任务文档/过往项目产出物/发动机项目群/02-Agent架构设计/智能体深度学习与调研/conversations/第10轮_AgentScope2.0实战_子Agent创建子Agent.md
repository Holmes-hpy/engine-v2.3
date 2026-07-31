# 第10轮：AgentScope 2.0实战 — 如何让子Agent创建子Agent

## 用户提问

我现在用的就是agentscope2.0。现在已经实现让agent自己创建团队，也就是第一层，但我希望每个被创建的agent都能创建自己的子agent，我不知道该怎么做。

## 专家回答

### 方案A：不用改代码 — 利用Agent Team权限体系模拟

AgentScope 2.0的Agent Team有一个关键机制：**permission_context**和**SubAgentTemplate**。

**核心思路**：
第一层Leader有`TeamCreate`/`AgentCreate`权限。你给第二层的"子Leader"也配置`AgentCreate`权限，但通过`permission_context`限制它们只能创建特定类型的Worker（执行者角色），不能再创建Leader。

**具体做法**：

1. **定义三种AgentTemplate**：
   - `LeaderTemplate`：有全部团队工具权限
   - `SubLeaderTemplate`（部门经理）：有`AgentCreate`但只能创建`WorkerTemplate`类型
   - `WorkerTemplate`（执行者）：只有`TeamSay`，没有创建权限

2. **关键：SubLeader的first_task里明确写**：
   "你是部门经理，你可以使用AgentCreate创建员工来帮你完成任务。你创建的员工只能是执行者角色，不能创建其他经理。完成后用TeamSay向CEO汇报结果。"

3. **权限隔离通过SubAgentTemplate实现**：
   ```python
   SubAgentTemplate(
       name="dept_manager",
       system_prompt_template="你是{dept_name}部门经理...",
       permission_context={
           "allowed_tools": ["AgentCreate", "TeamSay", "Read", "Write"],
           "allowed_agent_types": ["worker_role"],  # 只能创建worker
           "max_sub_agents": 3,  # 最多创建3个
       }
   )
   ```

**这能做到什么程度**：
- 子Leader确实可以动态创建Worker
- Worker在独立Session中执行
- 子Leader收集Worker结果后汇报给CEO

**但这仍然是模拟的原因**：
- 子Leader创建的Worker和子Leader共享同一个MsgHub吗？取决于你怎么配置
- 如果子Leader用`create_app(sub_agents=[...])`创建了一个子团队，这个子团队的MsgHub是独立的
- 但Worker如果也被赋予`AgentCreate`权限，理论上可以继续创建（需要在permission_context里禁止）

### 方案B：真实现 — 利用create_app嵌套

AgentScope 2.0的`create_app`本身支持嵌套！你可以在一个App内部的Agent里再次调用`create_app`创建子App。

**关键发现**：AgentScope 2.0的`AgentTeam`本身就是通过`create_app`创建的。如果你的子Leader Agent的toolkit里包含一个"create_sub_team"工具，它就可以在自己的执行过程中创建一个新的AgentTeam（子团队）。

**但需要注意**：
- 子团队的MsgHub是独立的（天然隔离）
- 子团队的结果通过父Agent的工具返回
- 需要手动实现结果汇总
- 递归深度需要你自己在代码里控制（AgentScope 2.0不会自动阻止递归）

### 如果你要完全自定义底层行为

需要在AgentScope 2.0基础上扩展：
1. 自定义`SpawnAgentTool` — 包装create_app，自动设置深度限制
2. 自定义`RecursionGuard` — 在每次创建前检查深度
3. 自定义`SubTeamMsgHub` — 支持跨层消息路由

## 本轮核心知识点

- AgentScope 2.0中通过permission_context和SubAgentTemplate可以模拟子Leader创建子Agent
- 关键：定义Leader/SubLeader/Worker三种模板，权限逐级递减
- create_app天然支持嵌套，但递归深度需要自己控制
- 真正底层支持需要自定义SpawnAgentTool + RecursionGuard
