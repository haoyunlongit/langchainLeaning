import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableLambda

# 加载环境变量
load_dotenv()

# ==========================================
# Helper: 获取模型 (复用 01 的逻辑)
# ==========================================
def get_model():
    # 优先尝试读取 DeepSeek，如果没配置则回退到 OpenAI
    # 实际开发中建议封装成单独的 utils.py
    if os.getenv("DEEPSEEK_API_KEY"):
        print("🤖 使用 DeepSeek 模型")
        return ChatOpenAI(
            model="deepseek-chat",
            openai_api_key=os.getenv("DEEPSEEK_API_KEY"),
            openai_api_base=os.getenv("DEEPSEEK_API_BASE"),
            temperature=0.7
        )
    else:
        print("🤖 使用 OpenAI 模型")
        return ChatOpenAI(model="gpt-3.5-turbo", temperature=0.7)

model = get_model()

# ==========================================
# 知识点讲解： `|` 符号 (Operator Overloading)
# ==========================================
# 1. 这是一个 Python 语法特性，叫 "运算符重载" (Operator Overloading)。
#    Python 允许类通过实现 `__or__` 魔术方法来定义 `|` 的行为。
# 2. LangChain 的所有核心组件 (Prompt, Model, Parser) 都继承自 `Runnable` 类。
#    `Runnable` 实现了 `__or__` 方法，使得 `A | B` 等价于 `RunnableSequence(A, B)`。
# 3. Android 类比:
#    这就像 Kotlin 的 `infix` 函数或者 Gradle 的 DSL。
#    WorkManager 的链式调用: workManager.beginWith(workA).then(workB).enqueue()
#    或者 OkHttp 的 Interceptor 链。

# ==========================================
# 阶段二：多步逻辑链 (Sequential Chain)
# ==========================================
# 任务目标：
# 输入一个技术名词 -> 1. 解释概念 -> 2. 基于解释写一段 Android 代码示例
# 数据流向： Input -> [Explain Chain] -> Explanation -> [Code Chain] -> Final Output

# --- 第一步：解释概念 ---
explain_prompt = ChatPromptTemplate.from_template(
    "请用简练的语言解释 Android 开发中的这个概念: {topic}"
)
# 这里我们只取解释的文本内容
explain_chain = explain_prompt | model | StrOutputParser()

# --- 第二步：写代码 ---
code_prompt = ChatPromptTemplate.from_template(
    """
    基于以下关于 "{topic}" 的解释，写一个简单的 Android (Kotlin) 代码示例。
    只返回代码，不要Markdown格式，不要解释。
    
    解释内容:
    {explanation}
    """
)
code_chain = code_prompt | model | StrOutputParser()

# --- 第三步：总结 (Chain 3) ---
# 假设我们最后还要生成一个学习总结，需要用到 topic, explanation 和 code
summary_prompt = ChatPromptTemplate.from_template(
    """
    请为以下学习内容生成一个简短的 Markdown 总结卡片：
    
    主题: {topic}
    概念: {explanation}
    代码行数: {code} (请只计算代码行数)
    
    输出格式:
    ## 学习卡片: {topic}
    - 核心概念: (一句话总结)
    - 代码复杂度: (简单/中等/复杂)
    """
)
summary_chain = summary_prompt | model | StrOutputParser()

# --- 组装总链 (3步) ---

# 这里的逻辑是：
# 1. Input: {"topic": "LiveData"}
# 2. Assign explanation -> {"topic": "...", "explanation": "..."}
# 3. Assign code -> {"topic": "...", "explanation": "...", "code": "..."} 
#    注意：这里我们用 code_chain 生成代码，并将其存入 "code" 字段，
#    这样 summary_chain 就能同时访问 topic, explanation 和 code 了。
full_chain = (
    RunnablePassthrough.assign(explanation=explain_chain) 
    | RunnablePassthrough.assign(code=code_chain)
    | summary_chain
)

# ==========================================
# 执行
# ==========================================
print("--- 开始执行多步链 ---")
topic = "LiveData"
print(f"正在生成关于 {topic} 的解释和代码...")

# invoke 触发整个管道
result = full_chain.invoke({"topic": topic})

print(f"\n[最终生成的代码]:\n{result}")

# ==========================================
# 调试技巧：查看中间步骤
# ==========================================
# 如果你想看到每一步的输出，可以单独运行 explain_chain
# print("\n[Debug] 解释内容:", explain_chain.invoke({"topic": topic}))
