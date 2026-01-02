# 06. 工具调用（Function Calling）

## 一句话总结
通过 `bind_tools` 将函数签名暴露给模型，模型返回 `tool_calls`，按名称执行工具并将 `ToolMessage` 回传，最终得到可靠的自然语言答案。

## 关键要点
- 工具定义：使用 `@tool` 声明签名与描述
- 绑定模型：`model.bind_tools([tool1, tool2])`
- 执行流程：AIMessage -> tool_calls -> 执行工具 -> ToolMessage -> 再次模型生成
- 适用场景：需要事实型能力（时间、计算、汇率等）替代模型臆测

## 关联代码
- [06_function_calling_tools.py](file:///Users/stevenhao/Desktop/Langchain/langchain_learning/06_function_calling_tools.py)
