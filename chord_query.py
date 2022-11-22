"""
This file has the logic where we can query for a particular key and it will retrieve data 
from the finger tables of the chord network.
We need to pass the key and node id to invoke chord_query.py
Author: Fnu Shipra
Version: 1.0
"""
import sys
import hashlib
import constants 
import utility

"""
Start of the class ChordQuery
"""
class ChordQuery:
    """
    Init method that initialize the key and network node
    """
    def __init__(self, key, network_node):
        self.key = key
        self.network_node = network_node

    """
    This method is used to take the key and do the key lookup to retrieve the results from the finger table
    """
    def query(self):
        digest, hexDigest = utility.get_sha1(self.key.encode('utf-8'))
        node_id = int.from_bytes(digest, byteorder=sys.byteorder) % constants.NODES
        print(f"found id of key as {node_id}")
        successor = utility.invokeRPC(self.network_node, "find_successor", node_id)
        print(f"data should be present on {successor}")
        data = utility.invokeRPC(successor, "get_data", self.key) 
        return data

"""
Entry point of the program. It takes key and network node parameters
"""
if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("argument required are key to be searched and node id in the network")
    else:
        key = sys.argv[1]
        network_node = int(sys.argv[2]) 
        if network_node!=0:        
            node_name = f"{constants.LOCAL_HOST}:{constants.TEST_BASE_PORT + network_node}"   
            digest, hexDigest = utility.get_sha1(node_name.encode('utf-8'))
            network_node_id_sha1 = int.from_bytes(digest, byteorder=sys.byteorder) % constants.NODES
            port = network_node_id_sha1
        else:
            port = 0
        _, hex_digest_key = utility.get_sha1(key.encode('utf-8'))
        node_query = ChordQuery(hex_digest_key, port)
        data = node_query.query()
    print("Received data ")
    print(data)