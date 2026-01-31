import asyncio
import logging

# Set up a logger to see output in your terminal
logger = logging.getLogger(__name__)

async def send_sms_notification(phone_number: str, message: str) -> bool:
    """
    Simulates sending an SMS.
    'await asyncio.sleep(2)' pauses THIS function for 2 seconds,
    but lets the server handle other requests in the meantime.
    """
    logger.info(f"Generated SMS task for {phone_number}...")
    
    # Simulate network latency (Non-blocking delay)
    await asyncio.sleep(2)
    
    # In a real app, this is where you'd call Twilio or a local gateway
    print(f" [SMS SENT] To: {phone_number} | Msg: {message}")
    return True