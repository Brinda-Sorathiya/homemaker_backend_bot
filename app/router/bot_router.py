from fastapi import APIRouter, HTTPException, Request
from app.agent.graph import chat_agent

router = APIRouter()

@router.get("/chat")
async def check():
    return {"message": "Housing Real Estate AI Agent API"}

@router.post("/chat")
async def ai_qa_chat(request: Request):
    data = await request.json()
    question = data.get("question")
    
    if not question:
        raise HTTPException(status_code=400, detail="Missing 'question' in request body.")
    try:
        answer = await chat_agent(question)
        return {"answer": answer}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 