# 阶段性总结（01-03）

> 一句话总览：
> - 01 Model I/O：以 Prompt | Model | Parser 的流水线展示 LangChain 的基本运行机制，让输入到解析的全链路具象化，并用 LCEL 将模型任务组织成可组合的链。
> - 02 LCEL Chain：`RunnablePassthrough.assign` 解决链式调用中的参数透传问题，后续步骤既能看到最新输出，也能访问原始输入（全局上下文）。
> - 03 Structured Output：用 Pydantic 模型 + PydanticOutputParser + format_instructions，将不确定的文本输出约束为强类型对象。

**关联代码**
- [01_model_io.py](file:///Users/stevenhao/Desktop/Langchain/langchain_learning/01_model_io.py)
- [02_lcel_chain.py](file:///Users/stevenhao/Desktop/Langchain/langchain_learning/02_lcel_chain.py)
- [03_structured_output.py](file:///Users/stevenhao/Desktop/Langchain/langchain_learning/03_structured_output.py)

**关键要点**
- Model I/O：三件套（Prompt、Model、Parser）通过 `|` 串联，`invoke` 触发执行，数据沿链路自动流转。
- LCEL Chain：使用 `RunnablePassthrough.assign(key=chain)` 将中间产物追加到输入字典，形成“滚雪球式”的上下文累加。
- Structured Output：字段 `description` 传递语义约束，`{format_instructions}` 明确输出结构，解析失败可用 OutputFixingParser 进行自我修复。

**使用建议**
- 当输出需要继续被程序消费（存库、渲染 UI、调用接口）时，优先使用 Structured Output。
- 多步骤场景尽量模块化拆分 Prompt 与 Chain，再用 `assign` 做上下文累加，避免隐式依赖。
- 将 LCEL 链当作“数据管线”，明确每一步的输入/输出形态，调试时可单步 `invoke` 验证。

