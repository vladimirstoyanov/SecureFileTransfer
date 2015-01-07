import base64
import hashlib
from Crypto import Random
from Crypto.Cipher import AES


class AESCipher:
    def __init__(self, key): 
        self.bs = 32
        self.key = hashlib.sha256(key.encode()).digest()
    
    def pad_(self, s):
	"""
	Lenght of 's' must to be divided of 16 and this method do that
	"""
	return s + b"\0" * (AES.block_size - len(s) % AES.block_size)
    
    def pad(self, s):
	"""
	Lenght of 's' must to be divided of 16 and this method do that
	"""
	if (len(s)==0):
	   return s
	elif len(s) % 16 !=0:
	  s+=' ' * (16-len(s)%16)
	return s
      
    def encrypt_(self,message):
        """
        Encrypt 'message' string.
        """
	message = self.pad_(message)
	iv = Random.new().read(AES.block_size)
	cipher = AES.new(self.key, AES.MODE_CBC, iv)
	return iv + cipher.encrypt(message)

    def decrypt_(self,ciphertext):
	"""
	Decrypt 'ciphertext' string.
	"""
	iv = ciphertext[:AES.block_size]
	cipher = AES.new(self.key, AES.MODE_CBC, iv)
	plaintext = cipher.decrypt(ciphertext[AES.block_size:])
	return plaintext.rstrip(b"\0")
      
    def encrypt(self, message):  
	"""
        Encrypt 'message' string. Used for a file.
        """
	message = self.pad(message)
	#iv = ''.join(chr(random.randint(0,0xFF)) for i in range(16))
	iv = Random.new().read(AES.block_size)
	cipher = AES.new(self.key, AES.MODE_CBC, iv)
	return iv + cipher.encrypt(message)

    def decrypt(self, ciphertext):
	"""
        Decrypt 'message' string. Used for a file.
        """
	iv = ciphertext[:AES.block_size]
	cipher = AES.new(self.key, AES.MODE_CBC, iv)
	plaintext = cipher.decrypt(ciphertext)
	return plaintext[AES.block_size:]