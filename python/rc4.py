class RC4:
    def __init__(self):
        self.sbox = list(range(256))
        self.idx1 = 0
        self.idx2 = 0

    def reset(self, key: bytes):
        """初始化密钥调度算法 (KSA)"""
        key_len = len(key)
        self.sbox = list(range(256))
        self.idx1 = 0
        self.idx2 = 0
        j = 0

        for i in range(256):
            j = (j + self.sbox[i] + key[i % key_len]) % 256
            self.sbox[i], self.sbox[j] = self.sbox[j], self.sbox[i]

    def crypt(self, data: bytes) -> bytes:
        """进行加密或解密"""
        result = bytearray(len(data))

        for i in range(len(data)):
            self.idx1 = (self.idx1 + 1) % 256
            self.idx2 = (self.idx2 + self.sbox[self.idx1]) % 256
            self.sbox[self.idx1], self.sbox[self.idx2] = self.sbox[self.idx2], self.sbox[self.idx1]
            j = (self.sbox[self.idx1] + self.sbox[self.idx2]) % 256
            result[i] = data[i] ^ self.sbox[j]

        return bytes(result)


# # 示例使用
# key = b'12345678'
# data = b'1234'

# rc4 = RC4()
# rc4.reset(key)

# # 加密
# ciphertext = rc4.crypt(data)
# print("Ciphertext:", ciphertext)

# # 解密（再次使用同样的对象和密钥）
# rc4.reset(key)
# decrypted = rc4.crypt(ciphertext)
# print("Decrypted:", decrypted.decode())

# with open('python/res.txt', 'rb') as f:
#     data = f.read()
#     print(data)