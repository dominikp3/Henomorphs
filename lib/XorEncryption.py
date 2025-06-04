import hashlib

class XorEncryption:

    @staticmethod
    def _get_key(p):
        m=hashlib.sha512()
        m.update(p)
        return m.digest()
    
    @staticmethod
    def Encrypt(d:str, k:str):
        d = b"TEST" + d.encode()
        k2 = XorEncryption._get_key(k.encode())
        o = bytearray()
        for i in range(len(d)):
            o.append(d[i] ^ k2[i % len(k2)])
        return o

    @staticmethod
    def Decrypt(d:str, k:str):
        k2 = XorEncryption._get_key(k.encode())
        o = bytearray()
        for i in range(len(d)):
            o.append(d[i] ^ k2[i % len(k2)])
        if o[:4] != b"TEST":
            raise Exception("Invalid key")
        return o[4:].decode()