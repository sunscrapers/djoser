import string
from random import SystemRandom

random = SystemRandom()

def create_challenge(length, challenge_characters):
    return "".join(random.choices(challenge_characters, k=length))

def username_generator(size=6, chars=string.ascii_lowercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

def token_request_limiter(function):
    def wrapper(*args, **kwargs):
        return function(*args, **kwargs)
    return wrapper

def token_redeem_limiter(function):
    def wrapper(*args, **kwargs):
        return function(*args, **kwargs)
    return wrapper
