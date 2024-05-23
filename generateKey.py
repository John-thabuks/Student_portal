#Use this file to generate your secrete key.
# >run it: python3 generateKey.py


import secrets

def my_secret_key():
    my_key = secrets.token_hex(16)
    print(my_key)

my_secret_key()    