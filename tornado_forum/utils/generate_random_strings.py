import os


def generate_random_string(length:int) -> str:
    return str(os.urandom(length))