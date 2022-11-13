from chord_node import ChordNode
import sys
class Lab4(object):

    def __init__(self, port):
        self.port = port
    def start_server(self):
        self.node = ChordNode(port=int(self.port))
        self.node.start_listening()
        print("Creating another node")
        self.node2 = ChordNode(port = 9)
        self.node2.start_listening()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("argument with port number must be provided")
    port = sys.argv[1]
    Lab4(port).start_server()



