

import json
import logging
import os
import sys
from pathlib import Path
import time
import threading
from typing import Any, Dict
from typing_extensions import Annotated
import uvicorn
from dotenv import load_dotenv
_ = load_dotenv() # forcar a execucao

from app.schema import Payload, Message, Audio, Image, User
from app.domain import message_service


from fastapi import FastAPI, Query, HTTPException, Depends, Request, BackgroundTasks

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

IS_DEV_ENVIRONMENT = True
DEBUG = True
VERIFICATION_TOKEN = os.getenv("VERIFICATION_TOKEN")

app = FastAPI(
    title="WhatsApp Bot",
    version="0.1.0",
    openapi_url=f"/openapi.json" if IS_DEV_ENVIRONMENT else None,
    docs_url=f"/docs" if IS_DEV_ENVIRONMENT else None,
    redoc_url=f"/redoc" if IS_DEV_ENVIRONMENT else None,
    swagger_ui_oauth2_redirect_url=f"/docs/oauth2-redirect" if IS_DEV_ENVIRONMENT else None,
)

log = logging.getLogger(__name__)

MESSAGE_EXPIRY_MINUTES = 5  # Mensagens mais antigas que 5 minutos são descartadas

def is_message_too_old(message_timestamp, max_age_minutes=MESSAGE_EXPIRY_MINUTES):
    """
    Check if a message is too old to process.
    
    Args:
        message_timestamp: Can be string or int/float timestamp
        max_age_minutes: Maximum age in minutes before considering message too old
    
    Returns:
        bool: True if message is too old, False otherwise
    """
    current_time = time.time()
    
    # Convert message_timestamp to float if it's a string
    try:
        if isinstance(message_timestamp, str):
            message_time = float(message_timestamp)
        else:
            message_time = float(message_timestamp)
    except (ValueError, TypeError):
        # If we can't parse the timestamp, consider it too old to be safe
        return True
    
    # Calculate age in minutes
    age_minutes = (current_time - message_time) / 60
    
    return age_minutes > max_age_minutes

def parse_message(payload: Payload) -> Message | None:
    if not payload.entry[0].changes[0].value.messages:
        return None
    return payload.entry[0].changes[0].value.messages[0]

def get_current_user(message: Annotated[Message, Depends(parse_message)]) -> User | None:
    if not message:
        return None
    return message_service.authenticate_user_by_phone_number(message.from_)

def parse_audio_file(message: Annotated[Message, Depends(parse_message)]) -> Audio | None:
    if message and message.type == "audio":
        return message.audio
    return None

def parse_image_file(message: Annotated[Message, Depends(parse_message)]) -> Image | None:
    if message and message.type == "image":
        return message.image
    return None

def message_extractor(
        message: Annotated[Message, Depends(parse_message)],
        audio: Annotated[Audio, Depends(parse_audio_file)],
):
    if audio:
        return message_service.transcribe_audio(audio)
    if message and message.text:
        return message.text.body
    return None

###

@app.get("/health")
def health():
    return {"status": "healthy"}


@app.get("/readiness")
def readiness():
    return {"status": "ready"}

@app.get("/webhook")
def verify_whatsapp(
        hub_mode: str = Query("subscribe", description="The mode of the webhook", alias="hub.mode"),
        hub_challenge: int = Query(..., description="The challenge to verify the webhook", alias="hub.challenge"),
        hub_verify_token: str = Query(..., description="The verification token", alias="hub.verify_token"),
):
    if hub_mode == "subscribe" and hub_verify_token == VERIFICATION_TOKEN:
        return hub_challenge

    raise HTTPException(status_code=403, detail="Invalid verification token")

@app.post('/webhook', status_code=200)
def whatsapp_webhook(data: Dict[Any, Any], background_tasks: BackgroundTasks):
    """
    Endpoint para receber webhooks do WhatsApp
    """
    start_time = time.time()

    if DEBUG:
        print("Received WhatsApp message:\n", json.dumps(data, indent=2))
    
    payload = Payload(**data)
    message = parse_message(payload=payload)
    user = get_current_user(message)
    audio = parse_audio_file(message)
    user_message = message_extractor(message, audio)
    image = parse_image_file(message)

    if not user and not user_message and not image:
        # status message
        return {"status": "ok"}

    if message and is_message_too_old(message.timestamp):
        raise HTTPException(status_code=422, detail={
            "error": "message_expired",
            "message": "Message is too old to be processed",
            "max_age_minutes": MESSAGE_EXPIRY_MINUTES
        })
        
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if not user_message and not image:
        raise HTTPException(status_code=400, detail="No message content found")
    
    if image:
        return print("Image received")

    if user_message:
        print(f"Received message from user {user.first_name} {user.last_name} ({user.phone})")
        background_tasks.add_task(message_service.respond_and_send_message, user_message, user)
        return {
            "status": "accepted", 
            "type": message.type,
            "user_phone": user.phone,
            "processing_time_ms": round((time.time() - start_time) * 1000, 2)
        }

    # Fallback (não deveria chegar aqui)
    return {"status": "no_action_taken"}

if __name__ == "__main__":
    # noinspection PyTypeChecker
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)  # nosec
