import string
from random import SystemRandom

random = SystemRandom()
challenge_characters = string.ascii_letters + string.digits


def create_challenge(length):
    return "".join(random.choices(challenge_characters, k=length))


def create_ukey(length):
    return create_challenge(length)
