# 07. 多轮对话 + 工具调用 + 对话记忆

## 一句话总结

在多轮语境下，将“工具调用闭环”与“会话记忆”组合：模型决定调用工具 → 执行并以 ToolMessage 回传 → 纳入历史上下文 → 再次生成最终回答，使后续轮次可引用已产生的事实结果。

## 1. 核心概念详解 (Android 类比)

| LangChain 概念                 | 解释                                                                          | Android 类比                                                                |
| :----------------------------- | :---------------------------------------------------------------------------- | :-------------------------------------------------------------------------- |
| **SystemMessage**              | **系统设定**。对话开始前预设的指令，定义 AI 的人设和规则。                    | `BaseViewModel` 初始化时的配置；App 的全局 Config。                         |
| **HumanMessage**               | **用户输入**。代表人类发出的消息。                                            | 用户点击按钮、输入文本的 **Event / Action**。                               |
| **AIMessage**                  | **AI 回复**。AI 生成的内容，可能是文本，也可能是工具调用请求 (`tool_calls`)。 | UI 层展示的数据；**ViewModel 发出的 State** (如 `Loading`, `ShowContent`)。 |
| **ToolMessage**                | **工具结果**。工具函数执行后的返回值，必须反馈给 AI。                         | **Repository/Network 层返回的数据**。Model 拿到了数据，准备更新 UI。        |
| **InMemoryChatMessageHistory** | **内存历史**。一个简单的 List，按顺序存储上述所有消息。                       | `RecyclerView` 的 **Adapter List 数据源**；`MutableStateList<Message>`。    |

---

## 2. 核心逻辑：工具调用闭环 (Tool Calling Loop)

代码中的 `if` 和 `for` 循环构成了工具调用的核心闭环。

```python
# 1. 检查 AI 是否想调用工具
if getattr(ai, "tool_calls", None):
    # 2. 准备工具映射表 (查找表)
    tools_by_name = {t.name: t for t in [now_beijing, multiply, fx_rate]}

    # 3. 遍历所有工具调用请求 (AI 可能一次想调多个)
    for call in ai.tool_calls:
        name = call["name"]
        args = call.get("args", {})
        tool_id = call.get("id") # 关键：这是这次调用的唯一身份证

        # 4. 【执行】真正的 Python 函数
        output = tools_by_name[name].invoke(args)

        # 5. 【封装】将结果包装成 ToolMessage
        # 必须带上 tool_call_id，这样 AI 才知道这个结果对应哪个请求
        tool_msg = ToolMessage(name=name, tool_call_id=tool_id, content=str(output))

        # 6. 【存档】存入历史
        history.add_messages([tool_msg])

    # 7. 【再次生成】让 AI 看到工具结果后，生成最终的自然语言回答
    final: AIMessage = bound.invoke(history.messages)
    history.add_messages([final])
```

### 为什么需要这个循环？

LLM 本质上是**“文本补全机”**。它不能直接运行 Python 代码。

1.  **第一步 (AI 思考)**：AI 收到问题，发现自己算不出来，于是输出一个特殊的结构 `tool_calls`，意思是：“请帮我运行这个函数”。
2.  **中间步 (Python 运行)**：你的代码（上述循环）充当了**执行者**。你拦截到请求，运行函数，拿到结果。
3.  **最后步 (AI 总结)**：你把结果喂回给 AI，AI 看到结果后，就像看到了“参考答案”，然后用自然语言把它说出来。

**这个过程非常像 Android 的 `Interceptor` (拦截器) 或 `Middleware` (中间件)：**
Request (用户问题) -> Interceptor 拦截 (发现需要工具) -> 执行本地逻辑 -> Response (工具结果) -> 最终处理。

---

## 3. 关键要点

- **工具绑定**：使用 `model.bind_tools([...])` 暴露可调用函数与签名
- **记忆载体**：用 `InMemoryChatMessageHistory` 维护消息序列
- **闭环消息**：严格遵循 `Human` → `AI(tool_calls)` → `ToolMessage` → `AI(final)` 的消息流
- **多轮延续**：历史中包含工具真实结果，后续轮次可继续计算或复用事实

## 4. 关联代码

- 演示脚本：[07_conversational_tools_memory.py](file:///Users/stevenhao/Desktop/Langchain/langchain_learning/07_conversational_tools_memory.py)

## 5. 常见误区

- **忽略 ToolMessage**: 如果不把工具结果回写到历史，AI 在下一轮对话中就会“失忆”，不知道刚才算出了什么。
- **tool_call_id 匹配错误**: `ToolMessage` 必须包含对应的 `tool_call_id`，否则 AI 无法将结果与请求对应起来。
