from langchain_core.messages import (
    SystemMessage, 
    HumanMessage, 
    AIMessage, 
    ToolMessage,
    ChatMessage
)

def print_message(msg):
    print(f"\n🔹 [{type(msg).__name__}]")
    print(f"   Content: {msg.content}")
    # 打印额外属性
    if hasattr(msg, "tool_calls") and msg.tool_calls:
        print(f"   Tool Calls: {msg.tool_calls}")
    if hasattr(msg, "tool_call_id"):
        print(f"   Tool Call ID: {msg.tool_call_id}")
    if hasattr(msg, "role"): # ChatMessage 特有
        print(f"   Role: {msg.role}")

def run_demo():
    print("=== LangChain Message 体系详解 ===")

    # 1. SystemMessage: 系统的"Manifest"或"Config"
    # 作用：设定 AI 的人设、背景、规则。通常放在对话列表的第一个。
    sys_msg = SystemMessage(content="你是一个资深的 Android 架构师，擅长用 Kotlin 解释复杂概念。")
    print_message(sys_msg)

    # 2. HumanMessage: 用户的"Event"或"Action"
    # 作用：代表人类用户的输入。
    human_msg = HumanMessage(content="如何理解 MVVM 模式？")
    print_message(human_msg)

    # 3. AIMessage (普通): UI 层的"State" (ShowContent)
    # 作用：AI 的自然语言回复。
    ai_msg_normal = AIMessage(content="MVVM 分为 Model, View, ViewModel...")
    print_message(ai_msg_normal)

    # 4. AIMessage (带工具调用): UI 层的"State" (Loading / Requesting)
    # 作用：AI 想要执行动作。注意 content 通常为空或思考过程，关键在于 tool_calls。
    # Android 类比：ViewModel 发出一个 "FetchDataEvent"
    ai_msg_tool = AIMessage(
        content="",
        tool_calls=[{
            "name": "get_weather",
            "args": {"city": "Beijing"},
            "id": "call_123456" # 唯一 ID，用于匹配结果
        }]
    )
    print_message(ai_msg_tool)

    # 5. ToolMessage: Repository 层的"Result"
    # 作用：工具执行的结果。必须包含 tool_call_id 以匹配请求。
    # Android 类比：Network Callback 返回的 Success 数据
    tool_msg = ToolMessage(
        content="25°C, Sunny",
        tool_call_id="call_123456", # 必须与上面的 ID 一致！
        name="get_weather"
    )
    print_message(tool_msg)

    # 6. (不常用) ChatMessage: 自定义角色
    # 作用：当需要非标准角色时使用（如 'summary', 'db_log' 等）
    chat_msg = ChatMessage(role="summary", content="前文对话总结：用户询问了 MVVM。")
    print_message(chat_msg)

    print("\n\n=== 完整的对话上下文 (Context) 示例 ===")
    # 这就是传给 LLM 的最终 List
    conversation = [
        sys_msg,
        human_msg,
        ai_msg_tool, # AI 请求工具
        tool_msg,    # 工具返回结果
        AIMessage(content="北京今天是晴天，25度。适合出门。") # AI 最终回复
    ]
    
    print(f"Total Messages: {len(conversation)}")
    for i, m in enumerate(conversation):
        print(f"{i}. {type(m).__name__}: {m.content[:20]}...")

if __name__ == "__main__":
    run_demo()
