import os
from typing import List
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain_classic.output_parsers import OutputFixingParser
from utils import get_model

if os.getenv("DEEPSEEK_API_KEY"):
    model = get_model("deepseek")
else:
    model = get_model("openai")

class ContactCard(BaseModel):
    name: str = Field(description="联系人姓名")
    email: str = Field(description="邮箱地址")
    phone: str = Field(description="手机号，字符串格式")
    tags: List[str] = Field(description="标签列表")

parser = PydanticOutputParser(pydantic_object=ContactCard)
fixing_parser = OutputFixingParser.from_llm(parser=parser, llm=model)

prompt = ChatPromptTemplate.from_template(
    "请根据以下信息生成联系人卡片：{raw}\n{format_instructions}"
)

chain_strict = prompt | model | parser
chain_fixing = prompt | model | fixing_parser

def run_demo():
    raw = "姓名: 张三, 邮箱: zhangsan@example.com, 电话: 13800000000, 标签: 好友,同事。请返回JSON。"
    try:
        result = chain_strict.invoke({
            "raw": raw,
            "format_instructions": parser.get_format_instructions()
        })
        print("Strict Parsed:", result)
    except Exception as e:
        print("Strict Failed:", e)
        fixed = chain_fixing.invoke({
            "raw": raw,
            "format_instructions": parser.get_format_instructions()
        })
        print("Fixed Parsed:", fixed)
        print("First Tag:", fixed.tags[0] if fixed.tags else "")

if __name__ == "__main__":
    run_demo()
