"""
This file has the logic to create the active nodes in the network. 
We can add any number of nodes and it creates the listening socket on each node that updates its finger table 
on the basis of the nodes that join the network.
We need to pass the nodes to initialize the network
Author: Fnu Shipra
Version: 1.0
"""
import time
from finger_entry import FingerEntry
from constants import *
import socket
import sys
import pickle
import threading
from mod_range import ModRange
from utility import get_sha1
import constants

"""
Start of the class ChordNode
"""
class ChordNode(object):

    """
    Init method that intializes the ports and creates the dictionaries and lists
    """
    def __init__(self, port):
        self.port = port
        self.predecessor = None
        self.finger = [None] + [FingerEntry(port, k) for k in range(1, M+1)]  # indexing starts at 1
        self.keys = {}

    """
    This method is used to populate the data in finger tables of the chord network
    """
    def populate_data(self, data):
        key  = data["Key"] # hex digest of first and fourth column plyerId + year
        self.keys[key] = data
        return f"inserted {data['PlayerId']} with year {data['Year']} and hexKey {key} on Node id: {self.port}"

    """
    This method gets the data for a given input key
    """
    def get_data(self, key):
        if key not in self.keys:
            return "INVALID KEY"
        return self.keys[key]
    
    """
    This method is used to get the successor from the finger table for a given input key
    """
    def get_successor(self):
        return self.finger[1].node

    """
    This method creates the listening socket that listens to whatever message it receives from the peer
    """
    def create_listening_socket(self):
        lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        lsock.bind((LOCAL_HOST, TEST_BASE_PORT + self.port))
        lsock.listen()
        self.socket = lsock
    
    """
    This method finds the successor of a node by invoking RPCs
    """
    def find_successor(self, id):
        pred = self.find_predecessor(id)
        if pred == self.port:
            return self.get_successor()                                 # Local call
        return self.invokeRPC(pred, "successor")                        # this returns a node

    """
    This method is used to find the predecessor for the given key. It also calls get_successor 
    method to find the successor of a given key
    """
    def find_predecessor(self, id):
        start = self.port
        end = self.get_successor()

        if start == end:
            return start
        node = self.port
        while id not in ModRange(start + 1, end + 1, NODES):
            node = self.invokeRPC(start, "closest_preceding_finger", id)
            start = node
            end = self.invokeRPC(node, "successor")
        return node
    
    """
    This method is used to find the closest preceding finger as per the given input key
    """
    def closest_preceding_finger(self, id):
        for i in range(M, 0, -1):
            if self.finger[i].node in ModRange(self.port + 1 , id, NODES):
                return self.finger[i].node
        return self.port

    """
    This method invokes the RPC calls to call diffrent methods like init_finger_table, 
    set_predecessor, closest_preceding_finger
    """
    def invokeRPC(self, node, method, *args) :
        if node == self.port:
            if method == "update_finger_table":
               return self.update_finger_table(*args)
            if method == "init_finger_table":
                self.init_finger_table(*args)
                return 
            if method == "closest_preceding_finger":
                # print("received closest_preceding_finger")
                return self.closest_preceding_finger(*args)
            if method == "successor":
                return self.get_successor()
            if method == "find_successor":
                return self.find_successor(*args)
            if method == "set_predecessor":
                print(f"[LOCAL] updateing predecessor of {self.port} to {args[0]} ")
                self.predecessor = args[0]
                return 
            if method == "predecessor":
                return self.predecessor
            if method == "find_predecessor":
                return self.find_predecessor(*args)
            if method == "closest_preceding_finger":
                return self.closest_preceding_finger(*args)
        for _ in range(1, 4):
            try:
                client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                client_socket.connect((LOCAL_HOST, TEST_BASE_PORT + node))
                client_socket.sendall(pickle.dumps((method, *args)))
                data =  pickle.loads(client_socket.recv(BUF_SZ))
                client_socket.close()
                return data
            except OSError as error :
                print("sleeping for sometime")
                time.sleep(0.5)
        return 
            
    """
    This method takes the node and add it into the chord network. Thats how the nodes can join the network
    """
    def join_network(self):
        if self.port == 0:
            # this is the only node in the network right now. Update its stuff
            print("Starting new network")
            for i in range(1, M + 1):
                self.finger[i].node = self.port # save the referece to node's port. this will help in deciding what calls to make
            self.predecessor = self.port
            return 
        else :
            # invoke find_successor on zero
            self.init_finger_table(0) # we assume we start with zero
            self.update_others()
            print("finger table after joining the network is ")
            for entry in self.finger:
                print(entry)

    """
    This method is used to update the finger tables as and when new node joins the network
    """
    def update_others(self):
        """ Update all other node that should have this node in their finger tables """
        for i in range(1, M+1):  # find last node p whiose i-th fnger might be this node
            # FIXME: bug in paper, have to add the 1 +
            p = self.find_predecessor(((self.port - 2**(i)) + 1 + NODES) % NODES)
            self.invokeRPC(p, 'update_finger_table', self.port, i) 
            return 

    """
    This method updates the finger table by finding predecessor by invoking RPCs
    """
    def update_finger_table(self, s, i):
        """ if s is i-th finger of n, update this node's finger table with s """
        # FIXME: don't want e.g. [1, 1) which is the whole circle
        if (self.finger[i].start != self.finger[i].node
                 # FIXME: bug in paper, [.start
                 and s in ModRange(self.finger[i].start, self.finger[i].node, NODES)):
            print('update_finger_table({},{}): {}[{}] = {} since {} in [{},{})'.format(
                     s, i, self.port, i, s, s, self.finger[i].start, self.finger[i].node))
            self.finger[i].node = s
            print('#', self)
            p = self.predecessor  # get first node preceding myself
            self.invokeRPC(p, 'update_finger_table', s, i)
            return str(self)
        else:
            return 'did nothing {}'.format(self)

    """
    This method is used to initialize the finger table when the node joins the network
    """
    def init_finger_table(self,remote_port):
        self.finger[1].node = self.invokeRPC(remote_port, "find_successor", self.finger[1].start) # find my successor using node zero mostly
        print(f"successor of {self.finger[1].start} is {self.finger[1].node} ")
        # now update my predecessor to my success's predecessor. Should be a remote call but update my local predecessor value
        self.predecessor = self.invokeRPC(self.finger[1].node, "predecessor") # finding predecessor of my successor
        self.invokeRPC(self.finger[1].node, "set_predecessor", self.port) # update my successor's predecessor to my value
        for i in range(1, M ):
            if self.finger[i + 1].start  in range(self.port, self.finger[i].node):
                self.finger[i + 1].node = self.finger[i].node
            else :
                self.finger[i + 1].node = self.invokeRPC(remote_port,  "find_successor", self.finger[i + 1].start)
    
    """
    This method is used to manage the threads to handle multiple RPC calls
    """
    def runLoop(self):
        while True:
            print("Listening...")
            client, client_addr = node.socket.accept()
            threading.Thread(target=node.handle_rpc, args=(client,)).start()

    """
    This method is used handle the RPC calls to differnt methods of the network
    """
    def handle_rpc(self, client):
        rpc = client.recv(BUF_SZ)
        method, *args = pickle.loads(rpc)
        result = None
        if method == "populate_data":
            result = self.populate_data(*args)
        if method == "get_data":
            result = self.get_data(*args)
        if method == "update_finger_table":
            result = self.update_finger_table(*args)
        if method == "init_finger_table":
            self.init_finger_table(*args)
        if method == "closest_preceding_finger":
            result = self.closest_preceding_finger(*args)
        if method == "successor":
            result = self.get_successor()
        if method == "find_successor":
            result = self.find_successor(*args)
        if method == "set_predecessor":
            self.predecessor = args[0]
        if method == "predecessor":
            result = self.predecessor
        if method == "find_predecessor":
            result = self.find_predecessor(*args)
        client.sendall(pickle.dumps(result))

"""
Entry point of the program
"""
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("argument with port number must be provided")
    port = int(sys.argv[1])
    if port != 0:
            node_name = f"{LOCAL_HOST}:{TEST_BASE_PORT + port}"
            digest, hexDigest = get_sha1(node_name.encode('utf-8'))
            network_node_id = int.from_bytes(digest, byteorder=sys.byteorder) % constants.NODES
            port = network_node_id
    print(f"id in network is {port}")
    hasJoined = False
    node = ChordNode(port)
    node.create_listening_socket()
    t1  = threading.Thread(target = node.runLoop)
    t1.start()
    node.join_network()