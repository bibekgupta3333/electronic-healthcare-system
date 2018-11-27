import os
from zxcvbn import zxcvbn
from django.core.exceptions import ImproperlyConfigured
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from Crypto.Util.Padding import unpad
from base64 import b64encode, b64decode
import logging

logger = logging.getLogger(__name__)


def multi_getattr(obj, attr, **kwargs):
    attributes = attr.split('.')
    for attribute in attributes:
        try:
            obj = getattr(obj, attribute)
        except AttributeError:
            if "default" in kwargs:
                return kwargs["default"]
            else:
                raise
    return obj


def get_env_variable(name):
    try:
        return os.environ[name]
    except KeyError:
        raise ImproperlyConfigured('Environment variable {env_name} not found.'.format(env_name=name))


def verify_password(password: str, first_name: str=None, last_name: str=None, email: str=None) -> dict:
    max_score = 3
    results = zxcvbn(password, user_inputs=[first_name, last_name, email])
    data = {
        'verified': True,
        'warning': None
    }
    if results.get('score',0) < max_score:
        data['verified'] = False
        data['warning'] = results.get('feedback').get('suggestions')
    return data


AES_KEY = get_env_variable('AES_KEY')


def aes_with_salt_encryption(plaintext: str, salt: str) -> str:
    try:
        plaintext_bytes = plaintext.encode()
    except AttributeError:
        plaintext_bytes = plaintext

    try:
        salt_bytes = salt.encode()
    except AttributeError:
        salt_bytes = salt

    cipher = AES.new(salt_bytes, AES.MODE_CBC)
    ciphertext_with_salt_bytes = cipher.encrypt(pad(plaintext_bytes, AES.block_size))
    iv_salt = b64encode(cipher.iv).decode('utf-8')

    ciphertext_with_salt_bytes_base64 = b64encode(ciphertext_with_salt_bytes)
    cipher2 = AES.new(AES_KEY.encode(), AES.MODE_CBC)
    ct_bytes2 = cipher2.encrypt(pad(ciphertext_with_salt_bytes_base64, AES.block_size))
    iv_aes_key = b64encode(cipher2.iv).decode('utf-8')
    ciphertext = b64encode(ct_bytes2).decode('utf-8')

    return iv_salt, iv_aes_key, ciphertext


def aes_with_salt_decryption(encrypted_with_salt: str, initial_vector: str) -> str:
    if all('$' in val for val in [encrypted_with_salt, initial_vector]):
        try:
            iv_salt = initial_vector.split('$')[0]
            iv_aes_key = initial_vector.split('$')[1]
            salt = encrypted_with_salt.split('$')[0]
            cipher_aes_text = encrypted_with_salt.split('$')[1]

            cipher = AES.new(AES_KEY.encode(), AES.MODE_CBC, b64decode(iv_aes_key))
            plain_text = unpad(cipher.decrypt(b64decode(cipher_aes_text)), AES.block_size)

            cipher = AES.new(salt.encode(), AES.MODE_CBC, b64decode(iv_salt))
            password = unpad(cipher.decrypt(b64decode(plain_text)), AES.block_size)

            return password.decode('utf-8')
        except ValueError:
            logger.error("Key incorrect or message corrupted")
