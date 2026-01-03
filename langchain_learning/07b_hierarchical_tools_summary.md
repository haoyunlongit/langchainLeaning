# 07b. 分层工具选择 (Hierarchical Tool Selection)

## 一句话总结

当工具数量庞大时，采用**“先分类，后绑定”**的策略：先通过意图识别（Router）锁定工具子集，再将子集绑定到模型执行具体任务。这能有效降低 Token 消耗，减少幻觉，提升准确率。

## 1. 核心概念详解 (Android 类比)

| LangChain 概念 | 解释 | Android 类比 |
| :--- | :--- | :--- |
| **Router (Intent Classifier)** | **意图路由**。不解决具体问题，只负责分发任务到对应的“部门”。 | `AndroidManifest.xml` 中的 **Intent Filter**；或者路由框架 (ARouter) 的分发器。 |
| **Specific Toolset** | **专用工具包**。针对特定领域（如数学、法律、绘图）的一组工具集合。 | 具体的 **Feature Module** (如 `:feature:payment`, `:feature:login`)。 |
| **Dynamic Binding** | **动态绑定**。运行时根据意图，只将相关的 3-5 个工具绑定给 LLM，而不是全部 50 个。 | 动态加载 (**Dynamic Delivery**)；按需初始化 SDK。 |

---

## 2. 为什么需要分多步？ (Why Hierarchical?)

假设你有一个包含 100 个工具的超级助手（计算器、天气、股票、法律、翻译、绘图...）。

### 直接丢给 LLM 的问题 (Single Step)
```python
# ❌ 试图一次性塞入所有工具
model.bind_tools(all_100_tools)
```
1.  **上下文爆炸**：100 个工具的描述可能耗尽 Token 上限。
2.  **注意力分散**：LLM 容易在大量无关工具中迷失，导致选错（幻觉）。
3.  **性能低下**：每次请求都要处理巨大的 Prompt，延迟高，费用贵。

### 分层处理的优势 (Hierarchical)
```python
# ✅ Step 1: 先分类
category = classifier.classify("计算 123 * 45") # -> "MATH"

# ✅ Step 2: 只加载相关工具
if category == "MATH":
    model.bind_tools(math_tools) # 只绑定 2-3 个数学工具
```
1.  **专注**：LLM 只需要在 3 个工具里选，准确率极高。
2.  **省钱**：Prompt 短小精悍。
3.  **模块化**：新增“医疗工具包”不影响“数学工具包”的稳定性。

---

## 3. 代码实现模式

代码逻辑通常分为两层：

1.  **路由层 (Router Layer)**
    *   **输入**：用户 Query。
    *   **处理**：使用轻量级 Prompt 或微调模型判断类别（Math / Info / Chat）。
    *   **输出**：类别标签。

2.  **执行层 (Execution Layer)**
    *   **输入**：用户 Query + 类别标签。
    *   **处理**：
        *   根据标签 `import` 或 `get` 对应的工具列表。
        *   `model.bind_tools(selected_tools)`。
        *   执行常规的 Agent 流程。
    *   **输出**：最终结果。

## 4. 关联代码

- 演示脚本：[07b_hierarchical_tools.py](file:///Users/stevenhao/Desktop/langchainLeaning/langchain_learning/07b_hierarchical_tools.py)

## 5. 什么时候使用？

| 场景 | 推荐模式 | 理由 |
| :--- | :--- | :--- |
| **工具 < 10 个** | **单步模式** | 简单直接，开发成本低，一次 LLM 调用即可。 |
| **工具 > 20 个** | **分层模式** | 必须分层，否则准确率和延迟无法接受。 |
| **工具间有冲突** | **分层模式** | 如 `search_user(id)` 和 `search_order(id)` 容易混淆，分层能物理隔离。 |
| **需要极高稳定性** | **分层模式** | 路由层可以使用更简单、更确定的逻辑（甚至关键词匹配）来兜底。 |
