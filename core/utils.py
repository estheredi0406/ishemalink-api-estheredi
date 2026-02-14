import random
from django.core.cache import cache

def generate_otp(user_id):
    """
    Generates a 6-digit OTP and saves it in cache for 5 minutes.
    Prints to console to simulate an SMS gateway.
    """
    otp = str(random.randint(100000, 999999))
    # Store in cache with key: 'otp_1' (where 1 is user_id)
    cache.set(f"otp_{user_id}", otp, timeout=300)
    
    print("\n" + "="*50)
    print(f" MOCK SMS SENT TO USER {user_id}")
    print(f" YOUR ISHEMALINK VERIFICATION CODE IS: {otp}")
    print("="*50 + "\n")
    
    return otp

def verify_otp_logic(user_id, provided_code):
    """
    Checks if the provided code matches the one stored in cache.
    """
    stored_code = cache.get(f"otp_{user_id}")
    if stored_code and str(stored_code) == str(provided_code):
        cache.delete(f"otp_{user_id}") # Remove after successful use
        return True
    return False