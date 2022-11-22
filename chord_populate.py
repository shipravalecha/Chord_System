"""
This file has the logic to populate the data from csv file to the finger tables of the chord network. 
We need to pass the filename that has the data and any active node of the chord network.
Author: Fnu Shipra
Version: 1.0
"""
import csv
import sys
import constants
import utility
import time 

"""
Start of the class ChordPopulate
"""
class ChordPopulate:
    """
    Init method that initializes the file name and chord node and other dictionaries
    """
    def __init__(self, file_name, chord_node):
        self.file_name = file_name
        self.chord_node = chord_node
        self.data = {}

    """
    This method read and parse the data from the csv file passed and retrieves the data columnwise
    """
    def read_and_parse_data(self):
        file = open(self.file_name)
        reader = csv.reader(file)
        print("reading data...")
        count = 0
        for row in reader:
            if count == 0:
                count+=1
                continue
            _ , hexDigest = utility.get_sha1(row[0].encode('utf-8') + str(row[3]).encode('utf-8'))
            d = {
                "Key" : hexDigest,
                "PlayerId": row[0],
                "Name": row[1],
                "Position" : row[2],
                "Year" : row[3],
                "Team": row[4],
                "Games Played" : row[5],
                "Attempted" : row[6],
                "Passes Completed" : row[7],
                "Completion Percentage" : row[8],
                "Pass Attempts Per Game" : row[9],
                "Passing Yards" : row[10],
                "Passing Yards Per Attempt" : row[11],
                "Passing Yards Per Game" : row[12],
                "TD Passes" : row[13],
                "Percentage of TDs per Attempts" : row[14],
                "Ints" : row[15],
                "Int Rate" : row[16],
                "Longest Pass" : row[17],
                "Passes Longer than 20 Yards" : row[18],
                "Passes Longer than 40 Yards" : row[19],
                "Sacks" : row[20],
                "Sacked Yards Lost" : row[21],
                "Passer Rating" : row[22],
            }   
            self.data[hexDigest] = d
        print("Done parsing file")
    
    """
    This method is used to populate the data into the finger tables of the chord network
    """
    def populate_data_to_network(self):
        count = 0
        for d in self.data:
            digest, _ = utility.get_sha1(self.data[d]["PlayerId"].encode('utf-8') + str(self.data[d]["Year"]).encode('utf-8'))
            id = int.from_bytes(digest, byteorder=sys.byteorder) % constants.NODES
            network_node = utility.invokeRPC(0, "find_successor", id)
            print(utility.invokeRPC(network_node, "populate_data", self.data[d]))
            count+=1

"""
Entry point of the network that takes file name and network node parameters
"""
if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("argument with port number must be provided")
    else:
        file_name = sys.argv[1]
        network_node = int(sys.argv[2])
        node_name = f"{constants.LOCAL_HOST}:{constants.TEST_BASE_PORT + network_node}"   
        digest, hexDigest = utility.get_sha1(node_name.encode('utf-8'))
        network_node_id_sha1 = int.from_bytes(digest, byteorder=sys.byteorder) % constants.NODES
        port = network_node_id_sha1
        populator = ChordPopulate(file_name, port)
        populator.read_and_parse_data()
        populator.populate_data_to_network()
    print("data populated")