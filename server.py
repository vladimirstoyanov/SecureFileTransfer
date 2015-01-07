#!/usr/bin/env python

import socket, threading
import aes
from random import randint
import hashlib
import os

private_key = 'password'
file_destination = ''

class ClientThread(threading.Thread): 
    def __init__(self,ip,port, socket):
        threading.Thread.__init__(self)
        self.ip = ip 
        self.port = port
        self.socket = socket
        print "[+] New thread started for "+ip+":"+str(port)

    def ReturnHashOfFile(self, filepath, block_size=2**20):
		"""
		Return hash sum of file (filepath var)
		"""
		sha256 = hashlib.sha256()
		try:
		        f = open(filepath, 'rb')
		except IOError:
		        return ""
		while True:
			try:
			        data = f.read(block_size)
			except IOError:       
			        f.close()
			        return ""
			if not data:
				break
			sha256.update(data)
		f.close()
		return sha256.hexdigest()

    def getRandomKey(slef):
      """
      Generate and return random digit key
      """
      key=""
      for i in range(32):
	  key+=str(chr(randint(48,57)))
      return key
    
    
    def getHashAndFileName(self, data):
      """
      Return size, hash sum and name of file who will be received 
      """
      file_size = ""
      file_hash = ""
      file_name = ""
      
      if len(data)==0:
	  return file_size,file_hash,file_name
      
      i=0;
      while(i<len(data) and data[i]!='#'):
	file_size+=data[i]
	i+=1  
      i+=1
      
      while(i<len(data) and data[i]!='#'):
	file_hash+=data[i]
	i+=1  
      i+=1
      
      for j in range(i,len(data),1):
	  file_name+=data[j]
      return file_size, file_hash, file_name
	
	
    def run(self):    
        print "-------Connection from : "+ip+":"+str(port)

	key = self.getRandomKey() ##generating new key
	crypt = aes.AESCipher(private_key)
	cypher_text = crypt.encrypt_(key) ##encrypt and send the new key

        self.socket.send(cypher_text)
	data = self.socket.recv(2048)
	
	crypt = aes.AESCipher(key)
	plain_text = crypt.decrypt_(data)
	
	if (plain_text != "hello"):
	  print "Error: data!=hello"
	  self.socket.close()
	  return
      
	cypher_text = crypt.encrypt_('get hash and file name')
	self.socket.send(cypher_text)
	data = self.socket.recv(2048)
	plain_text = crypt.decrypt_(data)

	file_size, file_hash, file_name = self.getHashAndFileName(plain_text)
	
	try:
	  file_size = int(file_size)
	except:
	  print "Error: Cant convert file_size to int..."
	  self.socket.close()
	  return
	
	if (len(file_hash) == 0 or len(file_name) == 0 or file_size < 1):
	    print "Error: if (len(file_hash) == 0 or len(file_name)==0 or file_size == 0):"
	    self.socket.close()
	    return

	cypher_text = crypt.encrypt_('get file')
	self.socket.send(cypher_text)

	##receiving encrypted file
	print "Receiving encrypted file..."
	f = open(file_destination + file_name + '_en', 'wb')
	data = self.socket.recv(2048)
        while len(data)!=0:
	    f.write(data)
            data = self.socket.recv(2048)
	f.close()
	
	if (os.path.isfile(file_destination+file_name+'_en') == False):
	  print "Error: Failed to receive file!"
	  self.socket.close()
	  return
	
	f=open(file_destination+file_name+'_en','rb')
	f1=open(file_destination + file_name, 'wb')
	
	print "Decrypting file..."
	l = f.read(2048)
	while (l):
	  data = crypt.decrypt(l)
	  f1.write(data)
	  l = f.read(2048)
	
	
	f.close()
	f1.truncate(file_size)
	f1.close()
	
	os.remove(file_destination+file_name+'_en')
	
	print "Calculating checksum of " + file_destination + file_name
	file_hash2 = self.ReturnHashOfFile(file_destination + file_name)
	
	if (file_hash!=file_hash2):
	    print 'Error: Failed to receive file.'
	else:
	    print 'Done.'
	    
	self.socket.close()


host = "0.0.0.0"
port = 10128

tcpsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcpsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

tcpsock.bind((host,port))
threads = []


while True:
    tcpsock.listen(4)
    print "\nListening for incoming connections..."
    (clientsock, (ip, port)) = tcpsock.accept()
    clientsock.settimeout(5.0)
    newthread = ClientThread(ip, port, clientsock)
    newthread.start()
    threads.append(newthread)

for t in threads:
    t.join()
