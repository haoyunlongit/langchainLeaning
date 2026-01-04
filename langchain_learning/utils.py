import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
# Try importing Google Generative AI, handle if not installed
try:
    from langchain_google_genai import ChatGoogleGenerativeAI
except ImportError:
    ChatGoogleGenerativeAI = None

# Load environment variables once when this module is imported
load_dotenv()

def get_model(provider="openai", temperature=0.7):
    """
    根据 provider 返回不同的 Model 实现。
    这就像 Android 中的 Product Flavors 或者 Dependency Injection (Hilt/Dagger)。
    """
    # Allow overriding provider via environment variable if not explicitly passed (optional enhancement)
    # But sticking to the user's logic structure first.
    
    if provider == "openai":
        print(f"🔄 正在初始化 OpenAI Model...")
        return ChatOpenAI(
            model="gpt-3.5-turbo",
            temperature=temperature
        )
    
    elif provider == "deepseek":
        print(f"🔄 正在初始化 DeepSeek Model (via OpenAI Protocol)...")
        # DeepSeek 兼容 OpenAI 协议，只需要修改 base_url 和 api_key
        return ChatOpenAI(
            model="deepseek-chat",
            openai_api_key=os.getenv("DEEPSEEK_API_KEY"),
            openai_api_base=os.getenv("DEEPSEEK_API_BASE"),
            temperature=temperature
        )
        
    elif provider == "google":
        print(f"🔄 正在初始化 Google Gemini Model...")
        if ChatGoogleGenerativeAI is None:
            raise ImportError("Please install langchain-google-genai to use Google models.")
            
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
    返回 Embeddings 模型
    """
    if provider == "openai":
        if not os.getenv("OPENAI_API_KEY"):
             # Fallback or warning? user logic checked this in 08_rag_basic.py
             pass
        return OpenAIEmbeddings(model="text-embedding-3-small")
    
    # Can add more providers here (e.g., HuggingFace, DeepSeek if they have embeddings endpoint compatible)
    # For now, DeepSeek often uses OpenAI compatible embeddings or we stick to OpenAI
    # If provider is deepseek, we might still want to use OpenAI embeddings or a specific one.
    # For this refactor, I will stick to what was in 08_rag_basic.py which is OpenAIEmbeddings.
    
    elif provider == "deepseek":
         # DeepSeek does not strictly have an embedding model in the same chat API path usually, 
         # but let's assume we use OpenAI embeddings for now or local. 
         # The user requirement was just to implement the factory logic, 
         # and 08_rag_basic used OpenAIEmbeddings.
         # I will default to OpenAI embeddings for now unless specifically asked otherwise.
         print("⚠️ DeepSeek embeddings not configured, falling back to OpenAI Embeddings")
         return OpenAIEmbeddings(model="text-embedding-3-small")

    else:
        return OpenAIEmbeddings(model="text-embedding-3-small")
