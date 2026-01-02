import os
from typing import List
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field

# 加载环境变量
load_dotenv()

# ==========================================
# Helper: 获取模型
# ==========================================
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
# 编程题：食谱推荐助手
# 目标：实现一个 Structured Output 流程，让 LLM 推荐食谱并返回结构化数据。
# ==========================================

# 1. 定义数据模型 (Data Class)
# TODO: 请定义一个 Recipe 类
# 要求包含字段：
# - name: 菜名 (str)
# - ingredients: 主要食材列表 (List[str])
# - difficulty: 难度 (str, e.g., "Easy", "Medium", "Hard")
# - cooking_time_minutes: 烹饪时间 (int)
class Recipe(BaseModel):
    name: str = Field(description="菜名")
    ingredients: List[str] = Field(description="主要食材列表")
    difficulty: str = Field(description="难度 (e.g., 'Easy', 'Medium', 'Hard')")
    cooking_time_minutes: int = Field(description="烹饪时间 (分钟)")
    ##烹饪步骤: 详细的烹饪步骤列表 (List[str])
    cooking_steps: List[str] = Field(description="详细的烹饪步骤列表")

# TODO: 请定义一个 DailyMenu 类
# 要求包含字段：
# - date: 日期 (str)
# - theme: 今日主题 (str, e.g., "健康轻食", "川菜风味")
# - recipes: 食谱列表 (List[Recipe])
class DailyMenu(BaseModel):
    date: str = Field(description="日期 (e.g., '2024-10-25')")
    theme: str = Field(description="今日主题 (e.g., '健康轻食', '川菜风味')")
    recipes: List[Recipe] = Field(description="食谱列表")


# 2. 创建解析器 (Parser)
# TODO: 使用 PydanticOutputParser 创建解析器，解析目标是 DailyMenu
# parser = ...
parser = PydanticOutputParser[DailyMenu](pydantic_object=DailyMenu)

# 3. 构建 Prompt
# TODO: 创建 PromptTemplate
# 要求：
# 1. 角色设定：资深大厨
# 2. 任务：根据用户输入的 {cuisine} (菜系)，推荐 3 道菜
# 3. 必须注入 {format_instructions}
prompt = ChatPromptTemplate.from_template(
    """
    你是一个资深大厨，擅长推荐不同菜系的美食。
    任务：根据用户输入的 {cuisine} (菜系)，推荐 3 道菜。
    要求：
    1. 菜名必须是 {cuisine} 特有的。
    2. 每个菜的主要食材必须包含在用户输入的 {ingredients} 中。
    3. 必须符合用户输入的 {difficulty} 难度要求。
    4. 烹饪时间必须在 {cooking_time_minutes} 分钟内。
    5. 每个菜的烹饪步骤必须详细，包含必要的食材和操作步骤。
    
    {format_instructions}
    """
)


# 4. 组装链 (Chain)
# TODO: 将 prompt, model, parser 组装成 chain
# chain = ...
chain = prompt | model | parser


# 5. 执行与验证
def run_exercise():
    cuisine = "川菜"
    print(f"--- 正在请求关于 '{cuisine}' 的今日菜单 ---")
    
    try:
        # TODO: 调用 chain.invoke
        # 注意：不要忘记传入 format_instructions
        # result = chain.invoke(...)
        result = chain.invoke({
            "cuisine": cuisine,
            "ingredients": "鱼, 葱, 姜, 料酒, 盐, 味精",
            "difficulty": "Medium",
            "cooking_time_minutes": 60,
            "format_instructions": parser.get_format_instructions()
        })
        
        if result:
            print(f"\n✅ 解析成功!")
            print(f"主题: {result.theme}")
            print(f"日期: {result.date}")
            print("\n📋 菜单列表:")
            for recipe in result.recipes:
                print(f"- {recipe.name} ({recipe.difficulty}, {recipe.cooking_time_minutes} 分钟)")
                print("  主要食材:", ", ".join(recipe.ingredients))
                print("  烹饪步骤:")
                for step in recipe.cooking_steps:
                    print(f"    {step}")
            
            # 验证类型
            print(f"\n(调试信息: Result type is {type(result)})")
            
    except Exception as e:
        print(f"\n❌ 执行失败: {e}")

if __name__ == "__main__":
    run_exercise()
