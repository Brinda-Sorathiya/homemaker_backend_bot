import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()
google_api_key = os.getenv("GOOGLE_API_KEY")

llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash", # Note: double-check this model name, as mentioned previously. 'gemini-pro' or 'gemini-1.5-flash-latest' are more common.
    temperature=0,
    google_api_key=google_api_key # Use the variable here
)

