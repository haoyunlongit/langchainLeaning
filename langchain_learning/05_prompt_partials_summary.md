# 05. Prompt partial 与格式注入

## 一句话总结
通过 `Prompt.partial()` 预绑定 `{format_instructions}`，将结构化输出的约束提前固化到 Prompt 层，避免每次 `invoke` 时手动传参，提升稳健性与可维护性。

## 关键要点
- `partial()` 适合绑定“恒定不变”的上下文或格式说明
- 与 `parser.get_format_instructions()` 配合，让 LLM 始终产出符合 Schema 的内容
- 代码链依旧是 `prompt | model | parser`，但调用时只需传业务参数（如 `topic`）

## 关联代码
- [05_prompt_partials.py](file:///Users/stevenhao/Desktop/Langchain/langchain_learning/05_prompt_partials.py)

