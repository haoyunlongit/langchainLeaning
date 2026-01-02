import os
from typing import List
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser

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

# ==========================================
# 05 主题：Prompt partial 与格式注入
# 目标：不再在 invoke 时传入 format_instructions，而是在 Prompt 阶段预绑定
# ==========================================

class AndroidLibrary(BaseModel):
    name: str = Field(description="库的名称，例如 Retrofit")
    category: str = Field(description="库的分类，例如 Networking, UI, DI")
    description: str = Field(description="一句话描述该库的主要功能")
    is_google_official: bool = Field(description="是否是 Google 官方推出的库 (Jetpack)")

class LibraryRecommendation(BaseModel):
    topic: str = Field(description="推荐的主题")
    libraries: List[AndroidLibrary] = Field(description="推荐的库列表")

parser = PydanticOutputParser(pydantic_object=LibraryRecommendation)

prompt = ChatPromptTemplate.from_template(
    """
    你是一个资深的 Android 架构师。
    请为我推荐 3 个关于 "{topic}" 的常用 Android 开源库。
    
    要求：
    1. 必须是目前主流、还在维护的库。
    2. 如果有 Google 官方库，优先推荐。
    
    {format_instructions}
    """
)

# 关键：通过 partial 预先绑定格式说明
prompt = prompt.partial(format_instructions=parser.get_format_instructions())

chain = prompt | model | parser

def run_demo():
    topic = "依赖注入 (DI)"
    print(f"--- 使用 partial 预绑定格式说明，生成 '{topic}' 的推荐 ---")
    try:
        result = chain.invoke({"topic": topic})
        print("✅ 解析成功:", type(result))
        print(f"主题: {result.topic}")
        for lib in result.libraries:
            tag = "[官方]" if lib.is_google_official else "[三方]"
            print(f"- {tag} {lib.name} ({lib.category}): {lib.description}")
    except Exception as e:
        print("❌ 执行失败:", e)

if __name__ == "__main__":
    run_demo()
