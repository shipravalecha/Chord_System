It has following files:
    chord_node.py- To create the nodes in the network
    chord_populate.py- To populate the data from csv file to finger tables
    chord_query.py- To query the data for a particular key
    constants.py- It contains some of the constant variables
    utility.py- It has some of the utility functions that are used in multiple files
    finger_entry.py - Represents an entry in the finger table
    mod_range.py - A helper class to find id ranges over a consistent hashing circular network

The approach I am using to figure out the port of the node is:
    Base port and offset: Base port I used is 17100 (added in constants.py file)

To start:

1. Create a network by executing below statements that will give node Ids in the network:

Invoke chord_node.py file by giving the node id, for example, to create nodes with port Offset 0, 1000, 3000, 5000
    python3 chord.node.py 0 # this has to be the first statement to execute as 0 id basically starts a new network
    python3 chord.node.py 1000 # arg 1000 is offset from the base port 
    python3 chord.node.py 3000
    python3 chord.node.py 5000
Once the above statements are executed, you will have a chord network of four nodes. Note here that the id
of nodes in the network is calculated by performing sha1 on ip address and port number. So for offset 1000, the id of the node is SHA_1((BASE_PORT + 1000) % Total Number of nodes). The actual id in the network can be seen when you run each of the above statements.

2. Then populate the data in the finger tables by running the below command:

Invoke chord_populate by giving the file name (csv file) and any active node Id, for example
    python3 chord_populate.py Career_Stats_Passing.csv 1000 

3. Then do the key lookup by running the below command:

Invoke chord.query by passing the key and node id, for example,
    python3 chord_query.py billanderson/25085341958  5000

If we give the wrong key, it says invalid key, for example,
    python3 chord_query.py billanderson/25085341950  5000 -> INVALID KEY
