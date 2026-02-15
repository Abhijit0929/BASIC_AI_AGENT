from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage,AIMessage

chat_history=[]

load_dotenv()

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0.9
)

print("🤖 Gemini Chatbot (type 'exit' to stop)\n")

while True:
    user_input = input("You: ")

    if user_input.lower() in ["exit", "quit", "bye"]:
        print("🤖 Goodbye!")
        break
    
    chat_history.append(HumanMessage(content=user_input))
    

    response = llm.invoke(chat_history)
    
    chat_history.append(AIMessage(content=response.content))
    print("Gemini:", response.content)