import hashlib
import time

import bcrypt


def validate_password(password, user_password):
    password_hash = bcrypt.hashpw(password.encode(), user_password.encode())
    return user_password == password_hash.decode()


def generate_token(user_id):
    token = '%s-%s' % (time.time(), user_id)
    return hashlib.sha1(token.encode()).hexdigest()
