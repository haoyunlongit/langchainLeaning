import os
from typing import List, Callable
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, SystemMessage

load_dotenv()

# ==========================================
# 1. 模拟“工具海” (假设这里有成百上千个工具)
# ==========================================

@tool
def check_inventory(product_id: str) -> str:
    """查询仓库中商品的库存数量"""
    return f"商品 {product_id} 库存: 100件"

@tool
def calculate_tax(amount: float, tax_type: str = "VAT") -> float:
    """
    计算特定类型的税务金额。

    Args:
        amount: 需要计算税额的基础金额（正数）。
        tax_type: 税务类型，可选值为 'VAT' (增值税) 或 'CIT' (企业所得税)。默认为 'VAT'。
    """
    rate = 0.25 if tax_type == "CIT" else 0.1
    return amount * rate

@tool
def translate_text(text: str, target_lang: str) -> str:
    """将文本翻译成目标语言"""
    return f"Translation({target_lang}): {text}"

@tool
def get_weather(city: str) -> str:
    """查询指定城市的天气"""
    return f"{city} 天气晴朗, 25度"

@tool
def send_email(recipient: str, subject: str, body: str) -> str:
    """发送电子邮件"""
    return "Email sent successfully"

# 这是一个包含所有可用工具的“注册表”
ALL_TOOLS = [check_inventory, calculate_tax, translate_text, get_weather, send_email]

# ==========================================
# 2. 核心逻辑：工具检索器 (Tool Retriever)
# ==========================================

def get_relevant_tools(query: str) -> List[Callable]:
    """
    【核心工程逻辑】
    在真实场景中，这里会使用 VectorDB (向量数据库) 进行语义检索。
    为了演示简单，我们使用简单的关键词匹配模拟 "RAG" 过程。
    """
    print(f"\n🔍 [System] 正在根据问题 '{query}' 检索相关工具...")
    
    selected_tools = []
    
    # 简单的模拟规则：根据关键词筛选
    if "库存" in query or "商品" in query:
        selected_tools.append(check_inventory)
    if "税" in query or "钱" in query or "算" in query:
        selected_tools.append(calculate_tax)
    if "翻译" in query:
        selected_tools.append(translate_text)
    if "天气" in query or "气温" in query:
        selected_tools.append(get_weather)
    if "邮件" in query:
        selected_tools.append(send_email)
        
    # 如果没匹配到，返回通用工具或空（这里为了演示返回空）
    return selected_tools

# ==========================================
# 3. 运行演示
# ==========================================

def run_dynamic_tool_demo(question: str, use_all_tools: bool = False):
    if use_all_tools:
        print(f"\n🚀 [Mode] 强制使用所有工具 (All Tools Strategy)...")
        relevant_tools = ALL_TOOLS
    else:
        # 1. 检索阶段：只获取相关的工具
        relevant_tools = get_relevant_tools(question)
    
    if not relevant_tools:
        print("⚠️ 未找到相关工具，直接回答...")
        tools_to_bind = []
    else:
        print(f"✅ 检索到 {len(relevant_tools)} 个相关工具: {[t.name for t in relevant_tools]}")
        tools_to_bind = relevant_tools

    # 2. 绑定阶段：只绑定筛选后的工具 (Context Window 优化)
    # 注意：这里我们动态创建了一个新的 model 实例或绑定
    if os.getenv("DEEPSEEK_API_KEY"):
        print("🤖 使用 DeepSeek 模型")
        llm = ChatOpenAI(
            model="deepseek-chat",
            openai_api_key=os.getenv("DEEPSEEK_API_KEY"),
            openai_api_base=os.getenv("DEEPSEEK_API_BASE"),
            temperature=0.7
        )
    else:
        print("🤖 使用 OpenAI 模型")
        llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.7)
        
    if tools_to_bind:
        llm_with_tools = llm.bind_tools(tools_to_bind)
    else:
        llm_with_tools = llm

    # 3. 执行阶段
    print("🤖 [AI] 正在思考...")
    result = llm_with_tools.invoke([
        SystemMessage(content="你是一个智能助手。"),
        HumanMessage(content=question)
    ])
    
    # 打印结果（观察 tool_calls 是否存在）
    if result.tool_calls:
        print(f"🎯 模型决定调用工具: {result.tool_calls}")
    else:
        print(f"🗣️ 模型直接回答: {result.content}")

if __name__ == "__main__":
    print("--- 场景1：询问库存 (动态筛选) ---")
    run_dynamic_tool_demo("帮我查一下 iPhone15(产品id) 的库存")
    
    print("\n--- 场景2：询问税务 (强制使用所有工具) ---")
    # 这里演示：虽然没做筛选，但把所有工具都给它，它也能从5个里挑出 calculate_tax
    run_dynamic_tool_demo("计算 1000 元的税", use_all_tools=True)
