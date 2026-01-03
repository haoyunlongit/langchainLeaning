import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_core.tools import tool
from langchain_core.prompts import ChatPromptTemplate
from typing import Literal

# 加载环境变量
load_dotenv()

def get_model():
    if os.getenv("DEEPSEEK_API_KEY"):
        print("🤖 使用 DeepSeek 模型")
        return ChatOpenAI(
            model="deepseek-chat",
            openai_api_key=os.getenv("DEEPSEEK_API_KEY"),
            openai_api_base=os.getenv("DEEPSEEK_API_BASE"),
            temperature=0.1  # 路由任务需要更低的随机性，越精确越好
        )
    else:
        return ChatOpenAI(model="gpt-3.5-turbo", temperature=0.1)

model = get_model()

# ==========================================
# 1. 定义两组具体的工具 (Specific Tools)
# ==========================================

# --- 数学工具组 ---
@tool
def multiply(a: int, b: int) -> int:
    """计算两个数的乘积"""
    return a * b

@tool
def add(a: int, b: int) -> int:
    """计算两个数的和"""
    return a + b

math_tools = [multiply, add]

# --- 信息工具组 ---
@tool
def get_weather(city: str) -> str:
    """查询指定城市的天气"""
    return f"{city} 今天晴转多云，25度"

@tool
def get_legal_info(topic: str) -> str:
    """查询法律相关条款"""
    return f"关于 {topic} 的法律条款：根据民法典..."

info_tools = [get_weather, get_legal_info]

# ==========================================
# 2. 第一步：意图分类 (Router / Abstract Tool Selection)
# ==========================================

# 我们让 LLM 输出结构化的分类结果
# 这种方式比让 LLM 说话更稳定
class IntentClassifier(object):
    def __init__(self, model):
        self.model = model
        # 定义分类系统的 Prompt
        self.system_prompt = """你是一个意图分类器。
你的任务是判断用户的输入属于以下哪个类别：
- "MATH": 涉及数字计算、加减乘除等。
- "INFO": 涉及查询天气、法律、新闻、百科知识等。
- "OTHER": 闲聊或其他无法分类的内容。

只返回类别名称，不要解释。
"""
    
    def classify(self, query: str) -> str:
        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=query)
        ]
        # 这里为了演示简单，直接用 content 匹配。
        # 生产环境通常使用 model.with_structured_output(Schema) 获得更强类型的输出
        response = self.model.invoke(messages)
        category = response.content.strip().upper()
        
        # 简单的清洗，防止模型多说话
        if "MATH" in category: return "MATH"
        if "INFO" in category: return "INFO"
        return "OTHER"

# ==========================================
# 3. 第二步：分发执行 (Specific Execution)
# ==========================================

def run_hierarchical_agent(query: str):
    print(f"\n🚀 用户输入: {query}")
    
    # --- Step 1: 路由 (找抽象方向) ---
    classifier = IntentClassifier(model)
    category = classifier.classify(query)
    print(f"📡 Step 1 意图分类: [{category}]")
    
    selected_tools = []
    system_instruction = ""

    # 根据分类结果，动态加载工具包
    if category == "MATH":
        selected_tools = math_tools
        system_instruction = "你是一个数学助手。请使用工具进行计算。"
    elif category == "INFO":
        selected_tools = info_tools
        system_instruction = "你是一个信息查询助手。请使用工具查询信息。"
    else:
        print("🤖 直接回复（无工具）: 好的，我们可以聊聊别的。")
        # 这里可以直接调用无工具的 LLM 进行闲聊
        response = model.invoke([HumanMessage(content=query)])
        print(f"💬 回复: {response.content}")
        return

    # --- Step 2: 绑定具体工具并执行 (找具体工具) ---
    print(f"🛠️  Step 2 加载工具包: {[t.name for t in selected_tools]}")
    
    # 动态绑定工具！
    # 关键点：这里的 model 此时只“看得到”与当前意图相关的几个工具，而不是全部。
    agent_executor = model.bind_tools(selected_tools)
    
    messages = [
        SystemMessage(content=system_instruction),
        HumanMessage(content=query)
    ]
    
    ai_msg = agent_executor.invoke(messages)
    
    # 处理工具调用结果 (简化版逻辑)
    if ai_msg.tool_calls:
        for tool_call in ai_msg.tool_calls:
            print(f"🎯 Step 3 决定调用具体工具: {tool_call['name']} 参数: {tool_call['args']}")
            # 这里为了演示，我们就不真的执行后续回环了，只展示决策过程
            # 真实场景会执行工具 -> 拿到结果 -> 再丢给 LLM 组织语言
            
            # 简单模拟执行，为了让输出完整
            tools_map = {t.name: t for t in selected_tools}
            tool_func = tools_map[tool_call['name']]
            res = tool_func.invoke(tool_call['args'])
            print(f"   ↳ 执行结果: {res}")

    else:
        print(f"🤖 Step 3 AI 决定不调用工具，直接回复: {ai_msg.content}")

# ==========================================
# 运行演示
# ==========================================
if __name__ == "__main__":
    print("=== 分层工具选择模式 (Hierarchical Tool Selection) ===")
    
    # Case 1: 数学问题
    run_hierarchical_agent("计算 123 乘以 456 是多少？")
    
    # Case 2: 信息查询
    run_hierarchical_agent("北京今天天气怎么样？")
    
    # Case 3: 混合/闲聊
    run_hierarchical_agent("你好，讲个笑话吧")
