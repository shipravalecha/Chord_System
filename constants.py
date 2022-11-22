"""
This is the file with all the constants used in this project
Author: Fnu Shipra
Version: 1.0
"""
M = 7  # FIXME: Test environment, normally = hashlib.sha1().digest_size * 8
NODES = 2**M
BUF_SZ = 4096  # socket recv arg
BACKLOG = 100  # socket listen arg
TEST_BASE_PORT = 17100  # for testing use port numbers on localhost at TEST_BASE+n
LOCAL_HOST = "127.0.0.1"