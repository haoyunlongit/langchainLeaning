# 07 Bonus. LangChain 消息体系详解

## 一句话总结

**BaseMessage** 是对话的原子单位，不同的子类代表了对话中不同的**角色 (Role)**。在 Android 开发中，它们对应着从 **Config -> Event -> State -> Data** 的完整数据流。

## 1. 核心消息类型对比

| Message 类型 | 角色 (Role) | 核心属性 | Android 类比 |
| :--- | :--- | :--- | :--- |
| **SystemMessage** | `system` | `content` | **Manifest / Global Config**<br>应用的全局配置，定义 AI 的行为基准。 |
| **HumanMessage** | `user` | `content` | **UI Event / Action**<br>用户点击按钮或输入文本，触发业务逻辑。 |
| **AIMessage** | `assistant` | `content`, `tool_calls` | **UI State / ViewModel State**<br>展示给用户的内容，或发出的指令（如 Loading, Navigation）。 |
| **ToolMessage** | `tool` | `content`, `tool_call_id` | **Repository Result / Callback**<br>数据层返回的原始数据，供 ViewModel (AI) 消费。 |

## 2. 关键属性详解

### 2.1 `AIMessage` 的 `tool_calls`
当 AI 决定调用工具时，它不会返回普通的文本，而是填充 `tool_calls` 字段。
这是一个结构化的列表，包含：
- `name`: 要调用的函数名
- `args`: 参数字典
- `id`: **关键**，这次调用的唯一标识符 (Request ID)

```python
# Android 类比：sealed class ViewState
AIMessage(
    content="", 
    tool_calls=[{
        "name": "get_weather",
        "args": {"city": "Beijing"},
        "id": "req_123"  # Request ID
    }]
)
```

### 2.2 `ToolMessage` 的 `tool_call_id`
工具执行完后，必须将结果封装为 `ToolMessage` 塞回历史。
**必须包含 `tool_call_id`**，且必须与 `AIMessage` 中的 `id` 完全一致。

```python
# Android 类比：Network Callback
ToolMessage(
    content="Sunny, 25C",
    tool_call_id="req_123" # Response 必须带上 Request ID，否则 AI 对应不上
)
```

## 3. 常见误区

1.  **手动拼接字符串**：不要自己去拼 `"User: ..."` 这样的字符串，一定要用对象。不同模型的 Prompt 格式不同（ChatML, Llama2 等），LangChain 会自动帮你处理格式化。
2.  **遗漏 ToolMessage**：如果 AI 发起了 `tool_calls`，下一条消息**必须**是 `ToolMessage`。如果跳过直接发 `HumanMessage`，模型会报错或产生幻觉（因为它还在等函数返回）。
3.  **ChatMessage**：虽然有一个通用的 `ChatMessage(role="...", content="...")`，但尽量不要用，除非你在做非常特殊的自定义模型适配。尽量用标准的强类型子类。
