from fastapi import FastAPI, Depends, BackgroundTasks, HTTPException, status
from typing import Annotated
import logging
import time
from datetime import datetime

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Suas funções de dependência existentes (mantém como estão)
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
) -> str | None:
    if audio:
        return message_service.transcribe_audio(audio)
    if message and message.text:
        return message.text.body
    return None

# Função para verificar se mensagem está expirada
def is_message_too_old(message_timestamp: str, max_age_minutes: int = 5) -> bool:
    """
    Verifica se a mensagem é muito antiga para processar
    """
    try:
        current_time = time.time()
        message_time = float(message_timestamp)
        age_minutes = (current_time - message_time) / 60
        return age_minutes > max_age_minutes
    except (ValueError, TypeError):
        return True  # Se não conseguir parsear, considera como antiga

# Dependência para validar idade da mensagem
def validate_message_age(message: Annotated[Message, Depends(parse_message)]) -> Message | None:
    """
    Valida se a mensagem não está expirada
    """
    if not message:
        return None
    
    if is_message_too_old(message.timestamp):
        logger.warning(f"Expired message from {message.from_}. Timestamp: {message.timestamp}")
        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail="Message has expired and cannot be processed"
        )
    
    return message

# FUNÇÃO DE PROCESSAMENTO EM BACKGROUND
def process_message_background(user_message: str, user: User, message_type: str = "text"):
    """
    Função que processa a mensagem em background
    """
    start_time = time.time()
    
    try:
        logger.info(f"Starting message processing for user {user.phone} - Type: {message_type}")
        
        # Aqui você chama sua função existente
        response = message_service.respond_and_send_message(user_message, user)
        
        processing_time = time.time() - start_time
        logger.info(
            f"Message processed successfully for {user.first_name} {user.last_name} ({user.phone}) "
            f"in {processing_time:.2f}s"
        )
        
        return response
        
    except Exception as e:
        processing_time = time.time() - start_time
        logger.error(
            f"Error processing message for {user.first_name} {user.last_name} ({user.phone}) "
            f"after {processing_time:.2f}s: {str(e)}"
        )
        
        # Opcionalmente, enviar mensagem de erro para o usuário
        try:
            error_message = "Desculpe, ocorreu um erro ao processar sua mensagem. Tente novamente."
            # Substitua pela sua função de envio
            # whatsapp_service.send_message(user.phone, error_message)
        except Exception as send_error:
            logger.error(f"Failed to send error message to {user.phone}: {send_error}")

# FUNÇÃO PARA PROCESSAMENTO DE IMAGENS
def process_image_background(image: Image, user: User):
    """
    Função específica para processar imagens em background
    """
    start_time = time.time()
    
    try:
        logger.info(f"Starting image processing for user {user.phone} - Image ID: {image.id}")
        
        # Sua lógica de processamento de imagem
        response = message_service.process_image_and_respond(image, user)
        
        processing_time = time.time() - start_time
        logger.info(
            f"Image processed successfully for {user.phone} in {processing_time:.2f}s"
        )
        
        return response
        
    except Exception as e:
        processing_time = time.time() - start_time
        logger.error(
            f"Error processing image for {user.phone} after {processing_time:.2f}s: {str(e)}"
        )

# ENDPOINT PRINCIPAL COM BACKGROUND TASKS
@app.post("/webhook")
async def whatsapp_webhook(
    payload: Payload,
    background_tasks: BackgroundTasks,
    message: Annotated[Message | None, Depends(validate_message_age)],
    user: Annotated[User | None, Depends(get_current_user)],
    user_message: Annotated[str | None, Depends(message_extractor)],
    image: Annotated[Image | None, Depends(parse_image_file)]
):
    """
    Webhook principal do WhatsApp com processamento em background
    """
    
    # Log da requisição recebida
    logger.info(f"Webhook received at {datetime.now().isoformat()}")
    
    # Se não há mensagem, retorna OK (pode ser status, etc.)
    if not message:
        logger.info("No message found in payload")
        return {"status": "no_message"}
    
    # Se usuário não encontrado
    if not user:
        logger.warning(f"User not found for phone number: {message.from_}")
        return {"status": "user_not_found"}
    
    # Log do usuário e tipo de mensagem
    logger.info(
        f"Received message from user {user.first_name} {user.last_name} ({user.phone}) "
        f"- Type: {message.type}"
    )
    
    # Processar mensagem de texto/áudio
    if user_message:
        logger.info(f"Adding text/audio message to background processing queue")
        background_tasks.add_task(
            process_message_background, 
            user_message, 
            user, 
            message.type
        )
    
    # Processar imagem
    elif image:
        logger.info(f"Adding image message to background processing queue")
        background_tasks.add_task(
            process_image_background, 
            image, 
            user
        )
    
    # Se não há conteúdo para processar
    else:
        logger.warning(f"No processable content found in message from {user.phone}")
        return {"status": "no_content"}
    
    # Retorna imediatamente (WhatsApp recebe confirmação rápida)
    return {"status": "accepted", "timestamp": datetime.now().isoformat()}

# ENDPOINT DE VERIFICAÇÃO (para desenvolvimento)
@app.get("/webhook")
async def verify_webhook(
    hub_mode: str = None,
    hub_challenge: str = None,
    hub_verify_token: str = None
):
    """
    Endpoint para verificação do webhook do WhatsApp
    """
    # Substitua pelo seu token de verificação
    VERIFY_TOKEN = "your_verify_token_here"
    
    if hub_mode == "subscribe" and hub_verify_token == VERIFY_TOKEN:
        logger.info("Webhook verified successfully")
        return int(hub_challenge)
    else:
        logger.warning("Webhook verification failed")
        raise HTTPException(status_code=403, detail="Forbidden")

# VERSÃO MAIS AVANÇADA COM RATE LIMITING
from collections import defaultdict
from datetime import datetime, timedelta

# Contador de mensagens por usuário (em memória - use Redis em produção)
user_message_count = defaultdict(list)

def rate_limit_check(user: User, max_messages: int = 10, time_window_minutes: int = 1):
    """
    Verifica rate limiting por usuário
    """
    now = datetime.now()
    window_start = now - timedelta(minutes=time_window_minutes)
    
    # Remove mensagens antigas
    user_message_count[user.phone] = [
        msg_time for msg_time in user_message_count[user.phone] 
        if msg_time > window_start
    ]
    
    # Verifica se excedeu o limite
    if len(user_message_count[user.phone]) >= max_messages:
        return False
    
    # Adiciona mensagem atual
    user_message_count[user.phone].append(now)
    return True

# VERSÃO COM RATE LIMITING
@app.post("/webhook-advanced")
async def whatsapp_webhook_advanced(
    payload: Payload,
    background_tasks: BackgroundTasks,
    message: Annotated[Message | None, Depends(validate_message_age)],
    user: Annotated[User | None, Depends(get_current_user)],
    user_message: Annotated[str | None, Depends(message_extractor)],
    image: Annotated[Image | None, Depends(parse_image_file)]
):
    """
    Versão avançada com rate limiting
    """
    
    if not message or not user:
        return {"status": "invalid_request"}
    
    # Verificar rate limiting
    if not rate_limit_check(user):
        logger.warning(f"Rate limit exceeded for user {user.phone}")
        return {"status": "rate_limited"}
    
    logger.info(f"Processing message from {user.first_name} {user.last_name} ({user.phone})")
    
    # Processar conteúdo
    if user_message:
        background_tasks.add_task(process_message_background, user_message, user, message.type)
    elif image:
        background_tasks.add_task(process_image_background, image, user)
    else:
        return {"status": "no_content"}
    
    return {"status": "accepted"}

# MONITORAMENTO DE SAÚDE
@app.get("/health")
async def health_check():
    """
    Endpoint para verificar saúde da aplicação
    """
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }