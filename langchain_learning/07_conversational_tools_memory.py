import os
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, ToolMessage
from langchain_core.tools import tool
from langchain_core.chat_history import InMemoryChatMessageHistory

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

def run_turn(history: InMemoryChatMessageHistory, question: str):
    print(f"\n👤 用户: {question}")
    user_msg = HumanMessage(content=question)
    msgs = [SystemMessage(content="你是严格遵循工具调用的助理。遇到时间、计算或汇率问题时必须调用对应工具。")]
    msgs.extend(history.messages)
    msgs.append(user_msg)
    ### 这一行是关键，确保模型绑定了工具。执行之后，模型会根据问题调用对应的工具。函数调用什么参数就已经知道了
    ai: AIMessage = bound.invoke(msgs)
    print("🤖 首次回复(可能包含工具调用):", ai.content if not getattr(ai, "tool_calls", None) else "包含工具调用")
    history.add_messages([user_msg, ai])
    if getattr(ai, "tool_calls", None):
        tools_by_name = {t.name: t for t in [now_beijing, multiply, fx_rate]}
        for call in ai.tool_calls:
            name = call["name"]
            args = call.get("args", {})
            tool_id = call.get("id")
            output = tools_by_name[name].invoke(args)
            tool_msg = ToolMessage(name=name, tool_call_id=tool_id, content=str(output))
            history.add_messages([tool_msg])
        final: AIMessage = bound.invoke(history.messages)
        history.add_messages([final])
        print("🤖 最终回答:", final.content)
    else:
        print("🤖 直接回答:", ai.content)

def run_demo():
    print("\n=== 多轮对话 + 工具调用 + 记忆 (InMemory) ===")
    history = InMemoryChatMessageHistory()
    run_turn(history, "北京时间现在几点？并计算 123*45，再告诉我 USD/CNY 的汇率。")
    run_turn(history, "把刚才的乘积结果乘以 2，并再次提供北京时间。")

if __name__ == "__main__":
    run_demo()
