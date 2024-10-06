# main.py

import datetime
import os
import sqlite3
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from llms.LLMFactory import LLMFactory
from llms.LLMEnum import LLMEnum
from langchain.prompts import ChatPromptTemplate
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI()

# Set up CORS for communication with Angular
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database setup
def get_db_connection():
    conn = sqlite3.connect('chatbot.db')
    conn.row_factory = sqlite3.Row
    return conn

# Request model
class ChatRequest(BaseModel):
    question: str
    conversation_id: int = None  # Optional for new conversations

# Initialize LLM
def initialize_model():
    provider = LLMEnum.GROQ.value
    model_name = LLMEnum.MIXTURE.value # Replace with desired model
    return LLMFactory(provider=provider, model=model_name).create()

# Prompt template
def create_prompt_template():
    template = """
    your name is "EL-ERHADOUINI chatbot".

    Answer the question below:

    Here is the conversation history: {context}

    Question: {question}

    Answer:
    """
    return ChatPromptTemplate.from_template(template)

# FastAPI endpoints
@app.on_event("startup")
def startup():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS conversations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT
    )
    ''')
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        conversation_id INTEGER,
        sender TEXT,
        message TEXT,
        FOREIGN KEY (conversation_id) REFERENCES conversations (id)
    )
    ''')
    conn.commit()
    conn.close()

@app.get("/conversations")
def get_conversations():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM conversations")
    conversations = cursor.fetchall()
    conn.close()
    result= {"conversations": [dict(row) for row in conversations]}
    # adding the id to the name
    for i in range(len(result["conversations"])):
        result["conversations"][i]["name"] = f"{result['conversations'][i]['name']} ({result['conversations'][i]['id']})"
    return result

@app.post("/conversations")
def create_conversation(request: Request, name: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(f"INSERT INTO conversations (name) VALUES ('{name}')")
    conn.commit()
    conversation_id = cursor.lastrowid
    conn.close()
    return {"conversation_id": conversation_id, "name": 'New Conversation'+" ("+str(conversation_id)+")"}

@app.get("/conversations/{conversation_id}/messages")
def get_messages(conversation_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT sender, message FROM messages WHERE conversation_id = ?", (conversation_id,))
    messages = cursor.fetchall()
    conn.close()
    return {"messages": [dict(row) for row in messages]}

@app.post("/chat")
def chat(request: ChatRequest):
    # Load chat context from database
    conn = get_db_connection()
    cursor = conn.cursor()

    context = ""
    if request.conversation_id:
        cursor.execute("SELECT message FROM messages WHERE conversation_id = ? ORDER BY id", (request.conversation_id,))
        messages = cursor.fetchall()
        context = "\n".join([msg['message'] for msg in messages])
        print(context)

    # Initialize LLM and generate response
    model = initialize_model()
    prompt = create_prompt_template()
    chain = prompt | model

    try:
        result = chain.invoke({"question": request.question, "context": context})
        result_text = result if isinstance(result, str) else result.content
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    # Store user and AI messages in database
    if not request.conversation_id:
        cursor.execute(f"INSERT INTO conversations (name) VALUES ('New Conversation')")
        conn.commit()
        request.conversation_id = cursor.lastrowid

    cursor.execute("INSERT INTO messages (conversation_id, sender, message) VALUES (?, ?, ?)",
                   (request.conversation_id, "User", request.question))
    cursor.execute("INSERT INTO messages (conversation_id, sender, message) VALUES (?, ?, ?)",
                   (request.conversation_id, "AI", result_text))
    conn.commit()
    conn.close()

    return {"response": result_text, "conversation_id": request.conversation_id}

# delete conversation with all messages
@app.delete("/conversations/{conversation_id}")
def delete_conversation(conversation_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM conversations WHERE id = ?", (conversation_id,))
    cursor.execute("DELETE FROM messages WHERE conversation_id = ?", (conversation_id,))
    conn.commit()
    conn.close()
    return {"message": "Conversation deleted"}


# Run the app
if __name__ == "__main__":
    import uvicorn
    uvicorn.run('main:app', host="0.0.0.0", port=8000, reload=True)
