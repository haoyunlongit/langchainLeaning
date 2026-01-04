import os
from dotenv import load_dotenv
from langchain_core.prompts import (
    ChatPromptTemplate,
    FewShotChatMessagePromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
from langchain_openai import ChatOpenAI

# 1. Load Environment Variables
load_dotenv()
if not os.getenv("DEEPSEEK_API_KEY"):
    print("⚠️ Please set DEEPSEEK_API_KEY in .env file")
    exit(1)

llm = ChatOpenAI(
    model="deepseek-chat", 
    temperature=0,
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url=os.getenv("DEEPSEEK_API_BASE")
)

def demo_system_prompt_best_practices():
    print("\n--- 1. System Prompt Best Practices ---")
    # Pattern: Role + Context + Constraints + Output Format
    system_template = (
        "你是一位精通 Python 文档的资深技术作家。\n"
        "你的任务是将用户杂乱的代码注释重写为专业的 Docstrings。\n"
        "约束条件：\n"
        "- 使用 Google 风格的 Python Docstrings。\n"
        "- 不要修改代码逻辑。\n"
        "- 保持简洁。"
    )
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_template),
        ("human", "{code_snippet}"),
    ])
    
    code = "def add(a,b): # adds two numbers and returns result\n    return a+b"
    
    chain = prompt | llm
    result = chain.invoke({"code_snippet": code})
    print(f"Input Code:\n{code}")
    print(f"Output Docstring:\n{result.content}")

def demo_few_shot_prompting():
    print("\n--- 2. Few-Shot Prompting (Structured) ---")
    # Use Few-Shot to teach the model a specific tone or format that is hard to describe.
    
    # 1. Define examples
    examples = [
        {"input": "今天天气真好。", "output": "情感：正面 | Emoji：☀️"},
        {"input": "我被堵在路上了。", "output": "情感：负面 | Emoji：🚗"},
        {"input": "我不知道吃什么。", "output": "情感：中性 | Emoji：🍽️"},
    ]
    
    # 2. Define a prompt template for the examples
    example_prompt = ChatPromptTemplate.from_messages([
        ("human", "{input}"),
        ("ai", "{output}"),
    ])
    
    # 3. Create the FewShot template
    few_shot_prompt = FewShotChatMessagePromptTemplate(
        example_prompt=example_prompt,
        examples=examples,
    )
    
    # 4. Combine with final prompt
    final_prompt = ChatPromptTemplate.from_messages([
        ("system", "你是一个情感分析机器人。请按格式输出：情感：X | Emoji：Y"),
        few_shot_prompt,
        ("human", "{user_input}"),
    ])
    
    chain = final_prompt | llm
    user_input = "我的代码终于跑通了！"
    result = chain.invoke({"user_input": user_input})
    print(f"User: {user_input}")
    print(f"Agent: {result.content}")

def demo_chain_of_thought():
    print("\n--- 3. Chain of Thought (CoT) ---")
    # Explicitly asking the model to "think step by step" to improve logic.
    
    question = "如果我有3个苹果，吃掉了1个，又买了5个，然后把总数的一半给朋友，我还剩多少个？"
    
    # Without CoT (sometimes fails on complex logic, though simple math is usually fine)
    # With CoT (explicit instruction)
    prompt = ChatPromptTemplate.from_messages([
        ("system", "你是一个逻辑严密的数学助手。"),
        ("human", "{question}\n请一步步思考。"),
    ])
    
    chain = prompt | llm
    result = chain.invoke({"question": question})
    print(f"Question: {question}")
    print(f"Answer (Step-by-Step):\n{result.content}")

if __name__ == "__main__":
    demo_system_prompt_best_practices()
    demo_few_shot_prompting()
    demo_chain_of_thought()
