from finger_entry import FingerEntry
from constants import *
import socket
import selectors
import sys
class ChordNode(object):
    def __init__(self, port):
        self.port = port
        # self.finger = [None] + [FingerEntry(n, k) for k in range(1, M+1)]  # indexing starts at 1
        self.predecessor = None
        self.finger = [None] + [FingerEntry(port, k) for k in range(1, M+1)]  # indexing starts at 1
        self.selector = selectors.DefaultSelector()
        self.socket = self.create_listening_socket(port)
        self.keys = {}
        self.start_listening()

    """
    This method creates the listening socket that listens to whatever message it receives from the peer
    so it invokes the read event and register the event in the selector to make it non blocking.
    """
    def create_listening_socket(self, port):
        lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        lsock.bind((LOCAL_HOST, TEST_BASE_PORT + port))
        lsock.listen()
        print(f"Listening on {(LOCAL_HOST, TEST_BASE_PORT +  port)}")
        lsock.setblocking(False)
        events = selectors.EVENT_READ
        self.selector.register(lsock, events, data=None)
    
    """
    This method accepts the socket connection for read and write events and
    register the events in the selector to make it non blocking.
    """
    def accept_wrapper(self, sock):
        print("accept wrapper socket ")
        print(sock)
        conn, addr = sock.accept()                                          # Should be ready to read
        print(f"Accepted connection from {addr}")
        conn.setblocking(False)
        events = selectors.EVENT_READ | selectors.EVENT_WRITE
        self.selector.register(conn, events, data=self.service_connection) # Wrote from client socket
        """
    This method is the service connection method which is a server that sends the messages to client 
    and updates the states of all the members in the group.
    """
    def service_connection(self, key, mask):
        sock = key.fileobj
        data = key.data
        if mask & selectors.EVENT_READ:                                     # Event read
            recv_data = sock.recv(1024)                                     # Should be ready to read
            if recv_data:
              print("received data " + recv_data)
        if mask & selectors.EVENT_WRITE:  
            print("inside event write")                                        # Event write

    def start_listening(self):
        try:
            while True:
                print(self.finger)
                events = self.selector.select(timeout = None)                   # This is a blocking call
                for key, mask in events:
                    if key.data is None:
                        self.accept_wrapper(key.fileobj)
                    else:
                        callback = key.data
                        callback(key, mask)
        except KeyboardInterrupt:
            print("Caught keyboard interrupt, exiting")
    @property
    def successor(self):
        return self.finger[1].node

    @successor.setter
    def successor(self, id):
        self.finger[1].node = id

    # def find_successor(self, id):
    #     """ Ask this node to find id's successor = successor(predecessor(id))"""
    #     np = self.find_predecessor(id)
    #     return self.call_rpc(np, 'successor')

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("argument with port number must be provided")
    port = sys.argv[1]
    ChordNode(int(port))