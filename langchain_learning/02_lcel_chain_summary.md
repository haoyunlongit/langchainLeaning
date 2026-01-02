# LCEL Chain 进阶知识点总结 (02_lcel_chain.py)

> 一句话总结：`RunnablePassthrough.assign` 解决了链式调用中的参数透传问题，它将中间步骤的结果“追加”到数据流中，让后续步骤既能看到最新输出，也能访问原始输入（全局上下文）。

## 1. 链式组合 (Sequential Chains)

- **概念**: 将多个独立的 Chain (`explain_chain`, `code_chain`) 串联成一个复杂的任务流。
- **优势**: 逻辑解耦，模块化。
- **语法**: `ChainA | ChainB`

## 2. 上下文传递 (`RunnablePassthrough.assign`)

- **核心痛点**: 下游 Chain 往往既需要**上游的输出**，也需要**原始的输入**。直接使用 `|` 会导致原始输入被覆盖。
- **解决方案**: 使用 `RunnablePassthrough.assign(key=chain)`。
- **作用**:
  - **并行执行**: 执行传入的 chain。
  - **数据合并**: 将结果作为新字段 `key` 合并到当前的输入字典中，**保留原始数据**。
- **数据流向示例**:

  ```python
  # 1. 初始输入
  # {"topic": "LiveData"}

  # 2. 经过 assign
  RunnablePassthrough.assign(explanation=explain_chain)

  # 3. 合并后的输出 (传给下一级)
  # {
  #   "topic": "LiveData",
  #   "explanation": "LiveData 是 Android Jetpack 的组件..."
  # }
  ```

## 3. 模块化设计

- **拆分 Prompt**: 将复杂的 Prompt 拆分为多个简单的 Prompt (解释概念 Prompt + 写代码 Prompt)。
- **复用性**: `explain_chain` 可以被单独调用，也可以被组合在更大的 Chain 中。
