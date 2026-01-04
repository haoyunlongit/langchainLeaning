# Phase 09: Prompt 设计与模式

## 1. 核心理念
在 LangChain 开发中，**Prompt 是源代码的一部分**。高质量的 Prompt 设计能显著提升系统的稳定性与能力边界。

## 2. 常见 Prompt 模式 (Patterns)

### A. System Prompt 结构化
不要只写一句话。一个健壮的 System Prompt 应包含：
1.  **Role (角色)**: 定义 AI 的身份 (e.g., "Senior Python Engineer").
2.  **Task (任务)**: 明确要做什么 (e.g., "Refactor code").
3.  **Constraints (约束)**: 明确**不**做什么 (e.g., "No explanation, code only").
4.  **Output Format (格式)**: 期望的输出结构 (e.g., JSON, Markdown).

### B. Few-Shot Prompting (少样本提示)
当指令难以描述时，**举例子**是最有效的方法。
-   **LangChain 组件**: `FewShotChatMessagePromptTemplate`
-   **原理**: 在 System Prompt 和 User Input 之间插入几组 `Human` -> `AI` 的对话历史作为示例。
-   **优势**: 显著提升格式遵循度和风格一致性。

### C. Chain of Thought (CoT, 思维链)
对于逻辑推理任务，强制模型展示思考过程。
-   **Magic Phrase**: "Let's think step by step" (让我们一步步思考)。
-   **效果**: 减少计算错误和逻辑跳跃，方便 Debug 中间过程。

## 3. 代码实现要点 (`09_prompt_patterns.py`)

### 结构化 System Prompt
```python
system_template = (
    "Role: {role}\n"
    "Task: {task}\n"
    "Constraints: {constraints}"
)
```

### Few-Shot 构造
```python
# 1. 定义示例
examples = [
    {"input": "happy", "output": "positive"},
    {"input": "sad", "output": "negative"}
]

# 2. 构造模板
few_shot_prompt = FewShotChatMessagePromptTemplate(
    example_prompt=ChatPromptTemplate.from_messages([("human", "{input}"), ("ai", "{output}")]),
    examples=examples
)

# 3. 组合
final_prompt = ChatPromptTemplate.from_messages([
    ("system", "Classify sentiment."),
    few_shot_prompt,
    ("human", "{user_input}")
])
```

## 4. 工程建议
1.  **版本控制**: Prompt 变动应像代码一样被 Git 管理，不要硬编码在深层逻辑中。
2.  **Prompt 模板分离**: 尽量将长 Prompt 抽取为独立文件或常量，保持 Python 代码整洁。
3.  **动态注入**: 利用 `Partial Prompt` (阶段 05) 预填全局配置（如当前时间、用户偏好）。
