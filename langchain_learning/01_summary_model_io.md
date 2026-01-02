# 核心概念总结 (Phase 1: Model I/O)

> 一句话总结：Phase 01 以 Prompt | Model | Parser 的流水线展示 LangChain 的基本运行机制，让你从输入到解析的全链路有形化，并用 LCEL 将模型任务组织成可组合的链。

本阶段对应 Android 开发中的 **MVC/MVVM 基础架构搭建**。我们学习了 LangChain 最基础的三个原子组件：Model、Prompt、OutputParser，以及如何通过 LCEL 将它们串联。

## 1. 核心组件 (The Big Three)

### 🤖 Model (大脑 / SystemService)

负责核心的推理和生成。

- **Android 类比**: `SystemService` (如 `LocationManager`) 或 `Remote Repository`。它干最重的活，但需要你给它指令。
- **关键类**: `ChatOpenAI`, `ChatGoogleGenerativeAI`。
- **核心参数**:
  - `model`: 指定具体模型版本 (如 "gpt-3.5-turbo")。
  - `temperature`: 创造性控制 (0.0 精准 ~ 1.0 奔放)。
- **代码示例**:
  ```python
  model = ChatOpenAI(model="gpt-3.5-turbo")
  ```

### 📝 Prompt (指令 / Intent)

负责包装用户的原始输入，提供上下文和格式要求。

- **Android 类比**: `Intent`。你不会直接把数据扔给 Activity，而是封装在 Intent 中，并带上 Action (`system` message) 和 Extras (`user` input)。
- **关键类**: `ChatPromptTemplate`。
- **核心方法**:
  - `from_messages()`: 定义角色对话 (System/User/AI)。
  - `from_template()`: 简单字符串模版。
- **代码示例**:
  ```python
  # 定义模版，{topic} 是占位符 (类似 String.format 的 %s)
  prompt = ChatPromptTemplate.from_template("请解释 {topic}")
  ```

### 🧩 OutputParser (解析器 / Gson)

负责将 LLM 返回的非结构化文本 (Raw String) 转换为程序可用的数据结构。

- **Android 类比**: `Gson` / `Moshi`。网络请求回来的 Body 是字符串，需要解析成 Entity 对象。
- **关键类**: `StrOutputParser` (最常用，只取内容), `JsonOutputParser`。
- **代码示例**:
  ```python
  parser = StrOutputParser()
  # 原始 response: "content='解释如下...'", 解析后: "解释如下..."
  ```

## 2. 核心机制: LCEL (LangChain Expression Language)

LangChain 的 "胶水" 语言，用于声明式地构建调用链。

### 🔗 管道操作符 (`|`)

- **语法**: `Chain = Step1 | Step2 | Step3`
- **原理**: 运算符重载 (`__or__`)。前一个组件的 **输出 (Output)** 自动成为下一个组件的 **输入 (Input)**。
- **Android 类比**: RxJava 的链式调用 (`Observable.map().flatMap()`) 或 Kotlin Flow。
- **数据流向**:
  ```mermaid
  graph LR
  Input(字典) --> Prompt --> PromptValue --> Model --> ChatMessage --> Parser --> String
  ```

### ▶️ 执行 (Invocation)

- **方法**: `chain.invoke(input_data)`
- **Android 类比**: `subscribe()` 或 `startActivity()`。定义好链之后，必须调用 invoke 才会真正执行。

## 3. 实战代码速查

```python
# 1. 准备积木
prompt = ChatPromptTemplate.from_template("翻译: {text}")
model = ChatOpenAI()
parser = StrOutputParser()

# 2. 搭建管道 (LCEL)
chain = prompt | model | parser

# 3. 通电运行
result = chain.invoke({"text": "Hello World"})
```

---

**下一步预告**: 在 Phase 2 中，我们将学习如何处理 **多参数传递** 和 **多步推理** (Output 作为下一步的 Prompt)，这将引入 `RunnablePassthrough` 等高级操作符。
