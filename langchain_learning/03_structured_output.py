import os
from typing import List
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from utils import get_model

# ==========================================
# Helper: 获取模型
# ==========================================
if os.getenv("DEEPSEEK_API_KEY"):
    model = get_model("deepseek")
else:
    model = get_model("openai")

# ==========================================
# 核心概念：结构化输出 (Structured Output)
# ==========================================
# 1. 问题背景:
#    LLM 默认输出是纯文本 (String)。
#    但在工程中，我们通常需要结构化数据 (JSON/Object) 来进行后续处理 (如存库、展示 UI)。
#    
# 2. Android 类比:
#    这完全等同于 Android 中的 "网络请求 + JSON 解析"。
#    - LLM = 后端服务器 API
#    - Prompt = Request Body
#    - OutputParser = Moshi/Gson/Kotlin Serialization
#    - Pydantic Model = Data Class

# ==========================================
# 第一步：定义数据模型 (Data Class)
# ==========================================
# 使用 Pydantic 定义我们需要的数据结构。
# Field 的 description 非常重要，它会被注入到 Prompt 中告诉 LLM 字段的含义。

class AndroidLibrary(BaseModel):
    name: str = Field(description="库的名称，例如 Retrofit")
    category: str = Field(description="库的分类，例如 Networking, UI, DI")
    description: str = Field(description="一句话描述该库的主要功能")
    is_google_official: bool = Field(description="是否是 Google 官方推出的库 (Jetpack)")

class LibraryRecommendation(BaseModel):
    topic: str = Field(description="推荐的主题")
    libraries: List[AndroidLibrary] = Field(description="推荐的库列表")

# ==========================================
# 第二步：创建解析器 (Parser)
# ==========================================
parser = PydanticOutputParser(pydantic_object=LibraryRecommendation)

# ==========================================
# 第三步：构建 Prompt
# ==========================================
# 关键点：必须将 format_instructions 注入到 prompt 中。
# parser.get_format_instructions() 会自动生成一段提示词，告诉 LLM 输出 JSON 格式。

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

# ==========================================
# 第四步：组装链 (Chain)
# ==========================================
# 这里的链非常简单: Prompt -> Model -> Parser
chain = prompt | model | parser

# ==========================================
# 执行与验证
# ==========================================
def run_example():
    topic = "网络请求 (Networking)"
    print(f"--- 正在请求关于 '{topic}' 的推荐 ---")
    
    # 1. 自动注入格式说明
    # 注意：我们只需要传入 topic，format_instructions 会由 LCEL 自动处理吗？
    # 不会！我们需要手动传入，或者使用 partial variables。
    # 这里我们在 invoke 时传入。
    
    try:
        # invoke 触发
        result = chain.invoke({
            "topic": topic,
            "format_instructions": parser.get_format_instructions()
        })
        
        print("\n✅ 解析成功! 得到的对象类型:", type(result))
        print(f"推荐主题: {result.topic}")
        
        print("\n📋 库列表:")
        for lib in result.libraries:
            official_tag = "[官方]" if lib.is_google_official else "[三方]"
            print(f"- {official_tag} {lib.name} ({lib.category}): {lib.description}")
            
        # 验证这真的是一个对象，可以直接访问属性
        first_lib_name = result.libraries[0].name
        print(f"\n(程序化访问验证: 第一个库是 {first_lib_name})")
        
    except Exception as e:
        print(f"\n❌ 解析失败: {e}")
        # 常见错误：LLM 没有严格遵循 JSON 格式，或者包含了额外的文本。
        # 进阶话题：OutputFixingParser 可以自动重试修复这个问题。

if __name__ == "__main__":
    run_example()
