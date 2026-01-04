import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
# from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings

# 加载环境变量
load_dotenv()

def get_model(provider="openai", temperature=0.7):
    """
    根据 provider 返回不同的 Model 实现。
    这就像 Android 中的 Product Flavors 或者 Dependency Injection (Hilt/Dagger)。
    """
    # 优先检查环境变量中是否强制指定了 provider (可选逻辑，方便全局切换)
    # provider = os.getenv("LLM_PROVIDER", provider)
    
    if provider == "openai":
        print(f"🔄 正在初始化 OpenAI Model (temp={temperature})...")
        return ChatOpenAI(
            model="gpt-3.5-turbo",
            temperature=temperature
        )
    
    elif provider == "deepseek":
        print(f"🔄 正在初始化 DeepSeek Model (via OpenAI Protocol, temp={temperature})...")
        # DeepSeek 兼容 OpenAI 协议，只需要修改 base_url 和 api_key
        return ChatOpenAI(
            model="deepseek-chat",
            openai_api_key=os.getenv("DEEPSEEK_API_KEY"),
            openai_api_base=os.getenv("DEEPSEEK_API_BASE"),
            temperature=temperature
        )
        
    elif provider == "google":
        print(f"🔄 正在初始化 Google Gemini Model (temp={temperature})...")
        # 需要 pip install langchain-google-genai
        from langchain_google_genai import ChatGoogleGenerativeAI
        
        if not os.getenv("GOOGLE_API_KEY"):
            raise ValueError("请在 .env 中配置 GOOGLE_API_KEY")
        return ChatGoogleGenerativeAI(
            model="gemini-pro",
            temperature=temperature
        )
    
    else:
        raise ValueError(f"Unknown provider: {provider}")

def get_embeddings_model(provider="openai"):
    """
    根据 provider 返回不同的 Embeddings 实现。
    """
    if provider == "openai":
        print("🔄 正在初始化 OpenAI Embeddings...")
        return OpenAIEmbeddings(model="text-embedding-3-small")
    
    elif provider == "deepseek":
        # DeepSeek 暂时没有官方的 Embeddings 接口兼容 OpenAIEmbeddings (或者可以使用 OpenAI 的)
        # 这里为了演示，我们假设 DeepSeek 用户可能也使用 OpenAI Embeddings，或者将来替换为 HuggingFace
        print("⚠️ DeepSeek 暂无专用 Embeddings，回退使用 OpenAI Embeddings...")
        return OpenAIEmbeddings(model="text-embedding-3-small")
        
    elif provider == "google":
        print("🔄 正在初始化 Google Embeddings...")
        from langchain_google_genai import GoogleGenerativeAIEmbeddings
        return GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    
    else:
        raise ValueError(f"Unknown provider: {provider}")
