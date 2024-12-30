import socket
import select
import errno
import sys
import pickle
from PIL import Image, ImageTk

from messageClass import Communication

HEADER_LENGTH = 10

IP = '127.0.0.1'
PORT = 1234

booleanDict = {
     'True': True,
     'False': False
}

class Client:
    def __init__(self, enteredUsername):
        self.myUsername = enteredUsername
        self.clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.clientSocket.connect((IP, PORT))
        self.clientSocket.setblocking(False)

        #Send join request
        myCommunication = Communication(messageType='joinRequest', message=self.myUsername)
        serialisedCommunication = pickle.dumps(myCommunication)
        communicationHeader = f"{len(serialisedCommunication):<{HEADER_LENGTH}}".encode('utf-8')
        self.clientSocket.send(communicationHeader + serialisedCommunication)

        #Wait for the header with select
        while True:
            #Use select to check if the socket is ready for reading
            readable, _, _ = select.select([self.clientSocket], [], [], 0.1)
            if readable:
                receivedHeader = self.clientSocket.recv(HEADER_LENGTH)
                if len(receivedHeader) == 0:
                    raise Exception('Connection closed by the server.')
                break
        
        #Process the received header
        receivedLength = int(receivedHeader.decode('utf-8').strip())
        while True:
            #Wait for the complete message to arrive
            readable, _, _ = select.select([self.clientSocket], [], [], 0.1)
            if readable:
                response = self.clientSocket.recv(receivedLength).decode('utf-8')
                if response:
                    self.success = booleanDict[response]
                    break
        
        self.dialogue = {}
        self.clients = {}


        #This next part is for the client list
        #Wait for the header with select
        while True:
            #Use select to check if the socket is ready for reading
            readable, _, _ = select.select([self.clientSocket], [], [], 0.1)
            if readable:
                receivedHeader = self.clientSocket.recv(HEADER_LENGTH)
                if len(receivedHeader) == 0:
                    raise Exception('Connection closed by the server.')
                break
        
        #Process the received header
        receivedLength = int(receivedHeader.decode('utf-8').strip())
        while True:
            #Wait for the complete message to arrive
            readable, _, _ = select.select([self.clientSocket], [], [], 0.1)
            if readable:
                response = pickle.loads(self.clientSocket.recv(receivedLength)).message
                if response:
                    for user in response:
                        self.clients[user] = 1
                    break
        

        del self.clients[self.myUsername]

        for user in self.clients.keys():

            self.dialogue[user] = []

        

    def SendMessage(self, messageType, message, recipient):

        myCommunication = Communication(messageType=messageType, message=message, recipient=recipient, sender= self.myUsername)
        serialisedCommunication = pickle.dumps(myCommunication)
        communicationHeader = f"{len(serialisedCommunication):<{HEADER_LENGTH}}".encode('utf-8')
        self.clientSocket.send(communicationHeader + serialisedCommunication)

        try:
            self.dialogue[recipient].append(myCommunication)
        except:
            self.dialogue[recipient] = []
            self.dialogue[recipient].append(myCommunication)

    def ProcessMessage(self, myCommunication):

        if myCommunication.messageType == 'removeUser':
             oldUser = myCommunication.message
             del self.clients[oldUser]
             del self.dialogue[oldUser]

        elif myCommunication.messageType == 'joinRequest':
             newUser = myCommunication.message
             self.clients[oldUser] = 1
             self.dialogue[oldUser] = []
        

        elif myCommunication.messageType in ['text', 'photo', 'image']:
             receivedMessage = myCommunication.message
             sender = myCommunication.sender
             self.dialogue[sender].append(myCommunication)
        
        return myCommunication


    def ReceiveMessage(self):
            try:
                receivedHeader = self.clientSocket.recv(HEADER_LENGTH)
                if not len(receivedHeader):
                        raise 'connection closed by the server.'
                
                receivedLength = int(receivedHeader.decode('utf-8').strip())
                serialisedCommunication = self.clientSocket.recv(receivedLength)
                myCommunication = pickle.loads(serialisedCommunication)

                self.ProcessMessage(myCommunication)

                return myCommunication


            except IOError as e:
                if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
                    print(f"Reading error: {str(e)}")
                    sys.exit()

            except Exception as e:
                print(f"General Error: {str(e)}")
                sys.exit()