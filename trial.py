from langchain_nvidia_ai_endpoints import ChatNVIDIA
from dotenv import load_dotenv

load_dotenv(override=True)

gpt=ChatNVIDIA(model='openai/gpt-oss-20b')

response = gpt.invoke([{"role":"user","content":"hi there how are you "}])
print(response.content)