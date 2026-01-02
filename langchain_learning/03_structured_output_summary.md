# 03. 结构化输出 (Structured Output)

> **一句话总结**：Structured Output 就是用**面向对象**的格式来**约束**大模型输出。

## 1. 核心概念
**Structured Output** 是将 LLM 生成的非结构化文本（Natural Language）转换为结构化数据（如 JSON、Object）的过程。这是将 LLM 接入工程系统的**关键桥梁**。

## 2. 为什么需要它？ (Why)
- **工程对接**: 你的代码（App/Backend）需要对象（Object/Class），而 LLM 输出的是字符串。
- **稳定性**: 依靠 Prompt 说 "请返回 JSON" 是不稳定的，OutputParser 封装了更严谨的指令和解析逻辑。
- **验证**: Pydantic 可以验证 LLM 返回的数据类型是否正确（如字段是否存在、类型是否匹配）。

## 3. Android 开发者类比
| LangChain 概念 | Android 类比 | 作用 |
| :--- | :--- | :--- |
| **Prompt** | **HTTP Request** | 向服务端（LLM）发起请求 |
| **OutputParser** | **Gson / Moshi / Kotlin Serialization** | 将响应体（String/JSON）转换为对象 |
| **Pydantic Model** | **Data Class / POJO** | 定义数据的结构和类型 |

## 4. 核心步骤
1. **定义模型**: 使用 `pydantic.BaseModel` 定义你期望的数据结构。
2. **创建解析器**: `parser = PydanticOutputParser(pydantic_object=MyModel)`
3. **注入指令**: 在 Prompt 中添加 `{format_instructions}`，让 LLM 知道如何格式化输出。
4. **组装链**: `chain = prompt | model | parser`

## 5. 常见误区
- **误区**: 认为只需要在 Prompt 里写 "请返回 JSON" 就够了。
  - **现实**: LLM 可能会返回 "好的，这是你的 JSON: {...}"，这会导致解析失败。OutputParser 配合 Prompt 模板能更好地处理这种情况。
- **误区**: 忽略 `description`。
  - **现实**: Pydantic 的 `Field(description="...")` 非常重要，它是传给 LLM 的语义说明，告诉 LLM 这个字段该填什么。

## 6. 进阶思考
如果 LLM 返回的格式错了怎么办？
- **Auto-fixing Parser**: LangChain 提供了一个自动修复解析器，当解析失败时，它会把错误信息和错误的输出再次发给 LLM，让 LLM "自我修正"。这类似网络请求的 Retry 机制。
