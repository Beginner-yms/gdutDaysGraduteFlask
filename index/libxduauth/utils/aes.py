from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from base64 import *
import base64


# J69IVxcXqvqNhvk1
def encrypt(v, k):
    # 统一门户的加密
    crypt = AES.new(k, AES.MODE_CBC, b'Jisniwqjwqjwqjww')
    return b64encode(crypt.encrypt(pad(b'J69IVxcXqvqNhvk1' * 4 + v, 16)))


# 小程序加密
class GdutCrypto(object):
    """
    对接小程序加密
    """

    def __init__(self, key):
        key = key.encode('utf-8')
        self.key = key

    def pkcs5padding(self, data):
        return self.pkcs7padding(data, 8)

    def pkcs7padding(self, data, block_size=16):
        if type(data) != bytearray and type(data) != bytes:
            raise TypeError("仅支持 bytearray/bytes 类型!")
        pl = block_size - (len(data) % block_size)
        return data + bytearray([pl for i in range(pl)])

    def encrypt(self, data):
        data = self.pkcs7padding(data, 16)
        aes = AES.new(self.key, AES.MODE_ECB)
        # str(base64.encodebytes(aes.encrypt(pkcs7padding(v))), encoding='utf8')
        return str(base64.encodebytes(aes.encrypt(data)), encoding='utf8')

    def decrypt(self, data):
        data = base64.decodebytes(bytes(data, encoding='utf-8'))
        aes = AES.new(self.key, AES.MODE_ECB)
        decrypt_text = aes.decrypt(data)
        return str(decrypt_text[:-int(decrypt_text[-1])], encoding='utf-8')


#
if __name__ == '__main__':
    user = GdutCrypto('gdutgdutgdutgdut')
    pwd = user.encrypt('temssomosm'.encode('utf-8'))
    print(pwd)
    print(user.decrypt(pwd))
