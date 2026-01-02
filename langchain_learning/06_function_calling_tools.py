import os
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, ToolMessage
from langchain_core.tools import tool

load_dotenv()

def get_model():
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

@tool
def now_beijing() -> str:
    """返回北京时间的 ISO 字符串"""
    return datetime.now(timezone(timedelta(hours=8))).isoformat()

@tool
def multiply(a: int, b: int) -> int:
    """返回两个整数的乘积"""
    return a * b

@tool
def fx_rate(pair: str) -> float:
    """返回指定货币对的汇率，如 'USD/CNY'"""
    table = {"USD/CNY": 7.10, "EUR/CNY": 7.75, "JPY/CNY": 0.05}
    return table.get(pair.upper(), -1.0)

bound = model.bind_tools([now_beijing, multiply, fx_rate])

prompt = ChatPromptTemplate.from_messages([
    ("system", "你是严格遵循工具调用的助理。遇到时间、计算或汇率问题时必须调用对应工具。"),
    ("human", "{question}")
])

def run_demo():
    question = "北京时间现在几点？再计算 123*45，最后告诉我 USD/CNY 的汇率。"
    messages = prompt.invoke({"question": question}).to_messages()
    ai: AIMessage = bound.invoke(messages)
    messages.append(ai)
    tools_by_name = {t.name: t for t in [now_beijing, multiply, fx_rate]}
    if getattr(ai, "tool_calls", None):
        for call in ai.tool_calls:
            name = call["name"]
            args = call.get("args", {})
            tool_id = call.get("id")
            output = tools_by_name[name].invoke(args)
            messages.append(ToolMessage(name=name, tool_call_id=tool_id, content=str(output)))
        final: AIMessage = bound.invoke(messages)
        print(final.content)
    else:
        print(ai.content)

if __name__ == "__main__":
    run_demo()
