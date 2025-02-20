import os
import hashlib
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes

def derive_key(password: str, salt: bytes) -> bytes:
    """从密码和盐值派生AES密钥"""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,  # AES-256
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    return kdf.derive(password.encode())

def encrypt_file(file_path: str, password: str) -> dict:
    """
    使用AES-GCM算法加密文件（双层密钥体系）。
    参数:
    file_path (str): 要加密的文件路径。
    password (str): 用于派生主加密密钥的密码。
    返回:
    dict: 包含加密文件数据和密钥文件数据的字典。
        - "encrypted_file" (bytes): 加密后的文件数据，结构为 nonce_file(12) + tag_file(16) + cipher_file_data。
        - "key_file" (bytes): 密钥文件数据，结构为 salt(16) + nonce_k2(12) + tag_k2(16) + encrypted_k2(32)。
    """
    # ================= 密钥派生层 =================
    salt = os.urandom(16)
    key_k1 = derive_key(password, salt)          # 主加密密钥
    key_k2 = os.urandom(32)                      # 文件加密密钥
    
    # 加密k2的GCM参数
    nonce_encrypt_k2 = os.urandom(12)
    cipher_k1 = Cipher(algorithms.AES(key_k1), modes.GCM(nonce_encrypt_k2), backend=default_backend())
    encryptor_k1 = cipher_k1.encryptor()
    encrypted_k2 = encryptor_k1.update(key_k2) + encryptor_k1.finalize()
    tag_encrypt_k2 = encryptor_k1.tag  # 固定16字节

    # ================= 文件加密层 =================
    # 加密文件的GCM参数
    nonce_encrypt_file = os.urandom(12)
    cipher_k2 = Cipher(algorithms.AES(key_k2), modes.GCM(nonce_encrypt_file), backend=default_backend())
    encryptor_k2 = cipher_k2.encryptor()
    
    with open(file_path, 'rb') as f:
        encrypted_file_data = encryptor_k2.update(f.read()) + encryptor_k2.finalize()
    tag_encrypt_file = encryptor_k2.tag  # 固定16字节

    # ================= 数据打包 =================
    # 密钥文件结构: salt(16) + nonce_k2(12) + tag_k2(16) + encrypted_k2(32)
    key_file_data = salt + nonce_encrypt_k2 + tag_encrypt_k2 + encrypted_k2
    
    # 加密文件结构: nonce_file(12) + tag_file(16) + cipher_file_data
    encrypted_file_combined = nonce_encrypt_file + tag_encrypt_file + encrypted_file_data

    return {
        "encrypted_file_combined": encrypted_file_combined,
        "key_file_data": key_file_data
    }

def decrypt_file(enc_file_path: str, key_file_path: str, password: str) -> bytes:
    """
    使用AES-GCM算法解密文件。
    参数:
    enc_file_path (str): 加密文件的路径。
    key_file_path (str): 密钥文件的路径。
    password (str): 用于派生密钥的密码。
    返回:
    bytes: 解密后的文件内容。
    异常:
    ValueError: 如果解密过程中出现错误。
    """
    # ================= 读取密钥文件 =================
    with open(key_file_path, 'rb') as f:
        key_file_data = f.read()

    # 解析密钥文件结构
    salt = key_file_data[:16]
    nonce_encrypt_k2 = key_file_data[16:28]  # 12字节
    tag_encrypt_k2 = key_file_data[28:44]    # 16字节
    encrypted_k2 = key_file_data[44:]        # 剩余部分（32字节）

    # ================= 解密k2 =================
    key_k1 = derive_key(password, salt)
    cipher_k1 = Cipher(algorithms.AES(key_k1), modes.GCM(nonce_encrypt_k2, tag_encrypt_k2), backend=default_backend())
    decryptor_k1 = cipher_k1.decryptor()
    key_k2 = decryptor_k1.update(encrypted_k2) + decryptor_k1.finalize()

    # ================= 解密文件 =================
    with open(enc_file_path, 'rb') as f:
        encrypted_file_data = f.read()

    # 解析加密文件结构
    nonce_encrypt_file = encrypted_file_data[:12]   # 12字节
    tag_encrypt_file = encrypted_file_data[12:28]   # 16字节
    cipher_file_data = encrypted_file_data[28:]     # 剩余部分为加密的文件数据

    # 使用k2密钥解密文件
    cipher_k2 = Cipher(algorithms.AES(key_k2), modes.GCM(nonce_encrypt_file, tag_encrypt_file), backend=default_backend())
    decryptor_k2 = cipher_k2.decryptor()

    return decryptor_k2.update(cipher_file_data) + decryptor_k2.finalize()