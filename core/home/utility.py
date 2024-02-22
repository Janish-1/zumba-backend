# utils.py
import random
import string

def generate_unique_referral_code(user_id):
    user_id_str = str(user_id)
    random_string = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    return f'REF{user_id_str}{random_string}'
