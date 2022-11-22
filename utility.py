"""
This file has all the utility methods used in the multiple files of the program
Author: Fnu Shipra
Version: 1.0
"""
import socket
import pickle
import hashlib

from constants import *

"""
This method takes the method name and arguments and calls that method
"""
def invokeRPC(node, method, *args) :
    retry_attempt = 1
    for retry_attempt in range(1, 5):
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((LOCAL_HOST, TEST_BASE_PORT + node))
            client_socket.sendall(pickle.dumps((method, *args)))
            data =  pickle.loads(client_socket.recv(BUF_SZ))
            client_socket.close()
            return data
        except OSError as error :
            print("retrying")
            client_socket.close()
            retry_attempt+=1
        except Exception as e:
            client_socket.close()
            print(f"some other error {e}")

"""
This method creates the SHA1 of the key provided to it
"""
def get_sha1(key):
        sha_1 = hashlib.sha1()
        sha_1.update(key)
        hexDigest = sha_1.hexdigest()
        digest = sha_1.digest()
        return digest, hexDigest