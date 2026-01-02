# 04. 解析失败自动修复 (OutputFixingParser)

## 1. 一句话总结
当 LLM 未严格遵守结构化输出时，用 OutputFixingParser 将错误输出与错误信息回传给模型，让其自我修复后再解析，等价于“解析层的 Retry + Clean”。

## 2. 核心思路
- 明确目标 Schema（Pydantic 模型）
- 先用严格解析器（PydanticOutputParser）尝试解析
- 失败则切换到 OutputFixingParser，携带错误上下文进行自修复

## 3. 代码入口
- [04_output_fixing_parser.py](file:///Users/stevenhao/Desktop/Langchain/langchain_learning/04_output_fixing_parser.py)

## 4. 适用场景
- LLM 偶尔返回多余前后缀（如“好的，这是 JSON：...”）
- 字段存在、类型不稳定但可纠正
- 需要更稳的生产级解析与容错

