import os
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from model_factory import get_model
from dotenv import load_dotenv

# 0. 加载环境变量
load_dotenv()

# ==========================================
# Model Factory (类似 ViewModelFactory)
# ==========================================
# 核心逻辑已移动到 model_factory.py

# ==========================================
# 阶段一：Model I/O (View & ViewModel)
# ==========================================

# 1. 选择你的 "Flavor" (这里你可以修改为 'deepseek' 或 'google' 来测试)
#CURRENT_PROVIDER = "openai" 
CURRENT_PROVIDER = "deepseek"
# CURRENT_PROVIDER = "google"

try:
    # 初始化 Model
    model = get_model(CURRENT_PROVIDER)

    # 2. 定义 Prompt (Intent)
    prompt_template = ChatPromptTemplate.from_messages([
        ("system", "你是一个专业的翻译助手。请直接输出翻译结果，不要带有多余的解释。"),
        ("user", "请将这段文字翻译成 {language}: {text}")
    ])

    # 3. 定义 Parser
    parser = StrOutputParser()

    # 4. 构建 Chain (LCEL Stream)
    chain = prompt_template | model | parser

    # 5. 执行
    print(f"--- 开始翻译任务 [{CURRENT_PROVIDER}] ---")
    input_data = {"language": "英文", "text": "LangChain 让切换大模型变得像切换 Android 主题一样简单。"}
    
    result = chain.invoke(input_data)
    
    print(f"原文: {input_data['text']}")
    print(f"译文: {result}")

except Exception as e:
    print(f"❌ 发生错误: {e}")
    print("提示: 请检查 .env 文件是否配置了对应的 API Key")
