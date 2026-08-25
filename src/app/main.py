from typing import List

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import engine, get_db
from app.llm_service import generate_reply

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Intelligent Conversational AI Chatbot")

#--- Enable CORS Middleware---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=["True"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"status": "ok", "message": "Chatbot API is running. POST to /chat to talk."}


@app.post("/chat", response_model=schemas.ChatResponse)
def chat(request: schemas.ChatRequest, db: Session = Depends(get_db)):
    # Get or create the conversation
    if request.conversation_id:
        conversation = db.get(models.Conversation, request.conversation_id)
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
    else:
        conversation = models.Conversation(title=request.message[:50])
        db.add(conversation)
        db.commit()
        db.refresh(conversation)

    # Build history for context-aware generation
    history = [{"role": m.role, "content": m.content} for m in conversation.messages]

    try:
        reply_text = generate_reply(history, request.message)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"LLM error: {e}")

    # Persist both turns
    db.add(models.Message(conversation_id=conversation.id, role="user", content=request.message))
    db.add(models.Message(conversation_id=conversation.id, role="assistant", content=reply_text))
    db.commit()

    return schemas.ChatResponse(conversation_id=conversation.id, reply=reply_text)


@app.get("/conversations", response_model=List[schemas.ConversationOut])
def list_conversations(db: Session = Depends(get_db)):
    return db.query(models.Conversation).order_by(models.Conversation.created_at.desc()).all()


@app.get("/conversations/{conversation_id}", response_model=schemas.ConversationOut)
def get_conversation(conversation_id: str, db: Session = Depends(get_db)):
    conversation = db.get(models.Conversation, conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return conversation


@app.delete("/conversations/{conversation_id}")
def delete_conversation(conversation_id: str, db: Session = Depends(get_db)):
    conversation = db.get(models.Conversation, conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    db.delete(conversation)
    db.commit()
    return {"detail": "Conversation deleted"}
