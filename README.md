# Distributed Application for file synchronization

## Introduction
For this project, I implemented a distributed application for synchronizing access to small files. The system consists of N processes. Each process provide a user-interface (text-based is fine) that supports the following operations:
1. create <filename>: create an empty file named <filename>
2. delete <filename>: deletes file named <filename>
3. read <filename>: displays the contents of <filename>
4. append <filename><line>: appends a <line> to <filename>

My application used Raymond's tree-based algorithm for mutual exclusion to ensure one-at-a-time access. The network is connected in a logical tree, and communication can only take place between neighbors in the tree. Each file will serve as a token in its own instance of Raymond's algorithm.  

## Implementation Details

The program was coded in Python 2.7.6 [2]. We do not use traditional files to store data, this is in light of reducing the overhead of I/O operations. Each file is an object of class TokenFile. The object contains the following data structures:
    Value - The string contents of the file itself
    Request Queue - A queue of requests made by nodes for that file
    Operations Queue - A queue of operations the node would want to perform on the file Name ­ Name of the file
    InUse - Whether the file is in use or not. We wait for two seconds if the requested file is currently in use, in hopes that within two             seconds the operation will be done. Although more sophisticated ways can be applied.
    
These data structures are maintained individually for each node, for each object.
On creation of file, the file object is propagated to all nodes so that they know who the who the holder is. However, the node can access the file only if they are the holder. The files(tokens) requested propagate through the network through channels allowed by the tree.
We use the following python libraries socket [3], thread [4], time [5], pickle[6], copy[7], deque[8] to implement network connections, multi-threading, waiting, serializing, copying objects and maintaining queues respectively.
The program reads input from tree.txt and iplist.txt in which we store information about the connectivity between nodes and their IP addresses with port.

## Deployment Details:

The nodes are distributed over three EC2 t3 micro­instances [8] deployed in US­West, Ireland and Asia (Mumbai ­ India) regions to simulate network lags and comply with the project requirements [1]. Multiple nodes can run over the same EC2 instance. The deployment of a node over instance can be configured through the iplist.txt file. Two nodes on the same instance are differentiated by the port number they listen on.
