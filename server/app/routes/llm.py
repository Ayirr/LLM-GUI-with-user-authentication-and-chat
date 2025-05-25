from fastapi import APIRouter, HTTPException, Depends
from app.models import LLMRequest, Conversation, Message
from app.auth import get_current_user
from app.database import conversations_collection
from datetime import datetime
from bson import ObjectId
import openai
from decouple import config
import logging

router = APIRouter()

# Configure OpenAI (you can replace this with any LLM API)
openai.api_key = config("OPENAI_API_KEY")
if not openai.api_key:
    raise ValueError("OPENAI_API_KEY not set")

@router.post("/chat")
async def chat_with_llm(request: LLMRequest, current_user: dict = Depends(get_current_user)):
    try:
        # Get conversation or create new one
        conversation = None
        if request.conversation_id:
            conversation = await conversations_collection.find_one({"_id": ObjectId(request.conversation_id)})
        
        if not conversation:
            # Create new conversation
            conversation = {
                "user_id": str(current_user["_id"]),
                "title": request.message[:50] + "..." if len(request.message) > 50 else request.message,
                "messages": [],
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            result = await conversations_collection.insert_one(conversation)
            conversation["_id"] = result.inserted_id
        
        # Add user message
        user_message = {
            "role": "user",
            "content": request.message,
            "timestamp": datetime.utcnow()
        }
        
        # Simple LLM response (replace with your preferred LLM)
        # For demo purposes, using a simple echo response
        assistant_message = {
            "role": "assistant",
            "content": f"Echo: {request.message}",
            "timestamp": datetime.utcnow()
        }
        
        # For real OpenAI integration, uncomment below:
        # try:
        #     response = openai.ChatCompletion.create(
        #         model="gpt-3.5-turbo",
        #         messages=[{"role": "user", "content": request.message}]
        #     )
        #     assistant_message["content"] = response.choices[0].message.content
        # except Exception as e:
        #     assistant_message["content"] = "I'm sorry, I encountered an error processing your request."
        import logging

        # try:
        #     response = openai.chat.completions.create(
        #         model="gpt-3.5-turbo",
        #         messages=[{"role": "user", "content": request.message}]
        #     )
        #     assistant_message["content"] = response.choices[0].message.content
        # except Exception as e:
        #     import logging
        #     import traceback
        #     logging.error(f"OpenAI API error: {e}")
        #     logging.error(traceback.format_exc())
        #     raise HTTPException(status_code=500, detail=f"OpenAI Error: {str(e)}")

        
        # Update conversation
        await conversations_collection.update_one(
            {"_id": conversation["_id"]},
            {
                "$push": {"messages": {"$each": [user_message, assistant_message]}},
                "$set": {"updated_at": datetime.utcnow()}
            }
        )
        
        return {
            "conversation_id": str(conversation["_id"]),
            "response": assistant_message["content"],
            "timestamp": assistant_message["timestamp"]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/conversations")
async def get_conversations(current_user: dict = Depends(get_current_user)):
    conversations = []
    async for conv in conversations_collection.find({"user_id": str(current_user["_id"])}):
        conversations.append({
            "id": str(conv["_id"]),
            "title": conv["title"],
            "created_at": conv["created_at"],
            "updated_at": conv["updated_at"],
            "message_count": len(conv.get("messages", []))
        })
    return {"conversations": conversations}

@router.get("/conversations/{conversation_id}")
async def get_conversation(conversation_id: str, current_user: dict = Depends(get_current_user)):
    conversation = await conversations_collection.find_one({
        "_id": ObjectId(conversation_id),
        "user_id": str(current_user["_id"])
    })
    
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    return {
        "id": str(conversation["_id"]),
        "title": conversation["title"],
        "messages": conversation.get("messages", []),
        "created_at": conversation["created_at"],
        "updated_at": conversation["updated_at"]
    }