import socket,thread,time,pickle,copy
from collections import deque
#global vars

serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
ALLOWED_COMMUNICATION = {}
MY_IP = ''
MY_SERVER_PORT = ''
MY_NODE_NAME = ''
#endGlobal
def init_clientServer(MY_IP,MY_SERVER_PORT):
	serversocket.bind((socket.gethostname(), MY_SERVER_PORT))
	serversocket.listen(5)


#Class structure for logical File
class TokenFile:
	def __init__(self,fvalue,fname,fholder,use):
		self.holder = fholder
		self.name = fname
		self.inUse = use
		self.value = fvalue #contents of the file
		self.OPERATIONS_QUEUE = deque() #each program instance maintains its own objects thus own OP-Q
		self.REQUEST_Q = deque()
fileList = []
#end of class decl
#returns if node has records of a file
def fileRecordExists(filename):
	for file in fileList:
		if(file.name == filename):
			return True
	return False

#broadcast file info (not token) to all nodes
def propogate(file):
	originalHolder = file.holder
	file.holder=MY_NODE_NAME
	file.inUse = False
	file = pickle.dumps(file)
	for key,value in ALLOWED_COMMUNICATION.iteritems():
		if key != MY_NODE_NAME and key != originalHolder:
			writeToServer(file, value[0], int(value[1]))

#find fileInfo in a list of files
def findFileIndex(fileName):
	i = 0
	for file in fileList:
		if file.name == fileName:
			return i
		i = i+1

#execute a command on the file
def executeCommand(findex,operation):
	print "Executing Command on this node"
	if operation[0] == "append":
		fileList[findex].value = fileList[findex].value + operation[1]
		print "append success"
	if operation[0] == "read":
		print "READ on " + fileList[findex].name + " : " + fileList[findex].value
	if operation [0] == "delete":
		del fileList[-findex]
		print "Deletion success, do not use this file name again"
		#message = "delete,"+str(findex)
		# for key,value in ALLOWED_COMMUNICATION.iteritems():
		# 	if key != MY_NODE_NAME:
		# 		writeToServer(message, value[0], int(value[1]))

#send token to a node
def sendResponse(node,fileName):
	fileName=pickle.dumps(fileName)
	for key,value in ALLOWED_COMMUNICATION.iteritems():
		if(key == node):
			writeToServer(fileName,value[0], int(value[1]))
#function for sending message to specified node
def writeToServer(message,server,port):
	clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	clientSocket.connect((server,port))
	clientSocket.send(message)
	clientSocket.close()
#function to send token request to specified node
def sendRequest(name,fname, holder):
	#get ip/port
	address = ALLOWED_COMMUNICATION.get(holder)
	message = fname + "," + MY_NODE_NAME
	writeToServer(pickle.dumps(message),address[0],int(address[1]))
#thread to continuously listen to CLI commands
def listenOnCLI():
	while 1:
		command = raw_input("Enter command \n")
		fileName = raw_input("Enter File Name \n")
		if command == "create":
			fileValue = raw_input("Enter file Contents \n")
			f1 = TokenFile(fileValue,fileName,MY_NODE_NAME,False)
			fileList.append(f1)
			print "Token for file " + fileName + " is with me"
			print "Propogating file information to neighbours"
			propogate(f1)
		else:
			fileIndex = findFileIndex(fileName)
			fileList[fileIndex].REQUEST_Q.append(MY_NODE_NAME)
			if command == "append":
				value = raw_input("Enter append value \n")
				fileList[fileIndex].OPERATIONS_QUEUE.append([command,value])
			if command == "delete" or command == "read":
				fileList[fileIndex].OPERATIONS_QUEUE.append([command,' '])
			print "holder is " + str(fileList[fileIndex].holder)
			sendRequest(MY_NODE_NAME,fileList[fileIndex].name,fileList[fileIndex].holder)

#thread to continously listen to any messages sent on the network
def listenOnNetwork():
	while 1:
		(serverCon, address) = serversocket.accept()
		data = serverCon.recv(100 * 1024)
		data = pickle.loads(data)
		serverCon.close()
		try: 
			#THIS IS WHERE YOU RECEIVE FILES
			data.value 
			if not fileRecordExists(data.name):
				f1 = TokenFile (data.value,data.name,data.holder,data.inUse)
				fileList.append(f1)
				print "Received information that file " + f1.name + "has been created"
				print "propogating information to neighbour nodes"
				f2 = copy.deepcopy(f1)
				propogate(f2)
			else:
				print "Token is here"
				findex = findFileIndex(data.name)
				fileList[findex].holder = data.holder
				fileList[findex].value = data.value
				fileList[findex].inUse = True
				if fileList[findex].holder == MY_NODE_NAME:
					top = ''
					try:
						top = fileList[findex].REQUEST_Q.pop()
					except:
						pass
					if top == MY_NODE_NAME:
						try:
							operation = fileList[findex].OPERATIONS_QUEUE.pop()
							executeCommand(findex, operation)
						except:
							pass
						try:
							top = fileList[findex].REQUEST_Q.pop()
							fileList[findex].holder = top
							print "SENDING TOKEN"
							fileList[findex].inUse = False
							sendResponse(top,fileList[findex])
						except:
							pass
					else: #i am not the holder
						print "sending token"
						fileList[findex].holder = top
						fileList[findex].inUse = False
						sendResponse(top,fileList[findex])
						#sendRequest(MY_NODE_NAME,fileList[findex].name, fileList[fileIndex].holder)
				else:
					pass

		except:
		    #THIS IS WHERE YOU"ll RECV REQUESTS
		    data = data.split(',')
		    filename = data[0]
		    sender = data[1]
		    findex = findFileIndex(filename)


		    if fileList[findex].holder != MY_NODE_NAME:
		    	fileList[findex].REQUEST_Q.append(sender)
		    	print "requesting token"
		    	sendRequest(MY_NODE_NAME,fileList[findex].name,fileList[findex].holder)
		    else:
		    	if fileList[findex].inUse == True:
		    		time.sleep(2)
		    	fileList[findex].holder = sender
		    	print "Sending token"
		    	sendResponse(sender,fileList[findex])
#Create a structure to save IP:PORT corresponding to each nodeName that THIS node can speak to
def buildAllowedCommunication(whoami, communicationTree,iplist):
	comFile = open (communicationTree)
	for line in comFile:
		if(line[1] == whoami):
			ipFile = open (iplist)
			for address in ipFile:
				address=address.split()
				if(address[0] == line[3]):
					ALLOWED_COMMUNICATION[line[3]]=[address[1],address[2]]
		if(line[3] == whoami):
			if(line[3] == whoami):
				ipFile = open (iplist)
				for address in ipFile:
					address=address.split()
					if(address[0] == line[1]):
						ALLOWED_COMMUNICATION[line[1]]=[address[1],address[2]]
	
	#set route to self
	ipFile = open (iplist)
	for address in ipFile:
		address = address.split()
		if(address[0] == whoami):
			ALLOWED_COMMUNICATION[whoami]=[address[1],address[2]]
			myPublicIp = address[1]




#init data structures and information
MY_NODE_NAME = raw_input("What is my node name? \n")
f = open("iplist.txt")
for ips in f:
	ips = ips.split()
	if(ips[0]==MY_NODE_NAME):
		MY_IP = socket.gethostname()
		MY_SERVER_PORT = int(ips[2])

buildAllowedCommunication(MY_NODE_NAME,"tree.txt","iplist.txt")
init_clientServer(MY_IP,MY_SERVER_PORT)

try:
	thread.start_new_thread(listenOnCLI, ())
	thread.start_new_thread(listenOnNetwork, ())
except:
	print "Thread start error"
while 1:
   time.sleep(5)


