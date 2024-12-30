import socket
import select
import pickle
from bidict import bidict

HEADER_LENGTH = 10
IP = '127.0.0.1'
PORT = 1234 

serverSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serverSock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

serverSock.bind((IP, PORT))
#serverSock.listen(5)
serverSock.listen()

socketList = [serverSock]

clients = bidict()



###########

def ReceiveMessage(clientSocket):
    try:
        messageHeader = clientSocket.recv(HEADER_LENGTH)

        if not len(messageHeader):
            return False
        
        messageLength = int(messageHeader.decode('utf-8').strip())

        pickledCommunication = clientSocket.recv(messageLength)

        communication = pickle.loads(pickledCommunication)

        return {'header': messageHeader, 
                'communicationObject':communication,
                'pickledCommunication': pickledCommunication}
    
    except:
        return False
    
#############

from messageClass import Communication

def SendMessage(incomingDict, usernames):
    global clients
    for username in usernames:
        print(f'This is the username {username}')
        try:
            clients[username].send(incomingDict['header'] + incomingDict['pickledCommunication'])
        except:
            continue

def SendClientList(clientSocket):

    global clients

    usernameList = list(clients.keys())
    myCommunication = Communication('clientList', usernameList, 'Server', clients.inv[clientSocket])
    pickedCommunication = pickle.dumps(myCommunication)
    CommunicationHeader = f"{len(pickedCommunication):<{HEADER_LENGTH}}".encode('utf-8')

    clientSocket.send(CommunicationHeader + pickedCommunication)



def RemoveClient(notifiedSocket):
    global clients

    #This stores the username ({clients[notifiedSocket]['data'].data})
    print(f"Closed connection from {clients.inv[notifiedSocket]}")
    socketList.remove(notifiedSocket)

    leftUsername = clients.inv[notifiedSocket]
    del clients[leftUsername]

    myCommunication = Communication('removeUser', leftUsername, 'Server', list(clients.keys()))
    pickedCommunication = pickle.dumps(myCommunication)
    outgoingDict = {'header': f"{len(pickedCommunication):<{HEADER_LENGTH}}".encode('utf-8'), 
    'communicationObject':myCommunication,
    'pickledCommunication': pickedCommunication}

                
    #Send everyone a message that the user has left.
    SendMessage(outgoingDict, list(clients.keys()))



##################



while True:

    readSockets, _, exceptionSockets = select.select(socketList, [], socketList)

    for notifiedSocket in readSockets:
        
        #This is the first message that informs the joining of users
        if notifiedSocket == serverSock:
            clientSocket, clientAddress = serverSock.accept()
            incomingDict = ReceiveMessage(clientSocket)
            if incomingDict is False:
                continue


            print(f"Your message is: {incomingDict['communicationObject'].message}")

            #Key is the username and value is the socket
            try:
                clients[incomingDict['communicationObject'].message]
                #If not error occurs it mean that key exists meaning the username is already taken.
                #A message must be sent back to the client to choose another username.
                #errorMessage = f'Username, {incomingDict["communicationObject"].message}, is already taken. Please enter another.'.encode('utf-8')
                
                usernameSet = 'False'.encode('utf-8')
                setHeader = f"{len(usernameSet):<{HEADER_LENGTH}}".encode('utf-8')
                clientSocket.send(setHeader + usernameSet)
                clientSocket.close()
                #print(errorMessage)


            except:
                #If we can't call clients with that key, it means the key doesn't exist so its a valid username
                
                #We send a message to all clients that there is a new client
                SendMessage(incomingDict, list(clients.keys()))

                usernameSet = 'True'.encode('utf-8')
                setHeader = f"{len(usernameSet):<{HEADER_LENGTH}}".encode('utf-8')
                clientSocket.send(setHeader + usernameSet)

                #Add the new client to the dictionary
                clients[incomingDict['communicationObject'].message] = clientSocket
                print(f"Accepted new connection from {clientAddress[0]}:{clientAddress[1]} username: {incomingDict['communicationObject'].message}")
                
                #Now that the message has been sent, we can update the socket list
                socketList.append(clientSocket)

                SendClientList(clientSocket)

                


        #This is for all other communications from that user
        else:
            message = ReceiveMessage(notifiedSocket)

            if message is False:
                RemoveClient(notifiedSocket)
                continue
            
            currentCommunication = message['communicationObject']
            SendMessage(message, [currentCommunication.recipient])


    for notifiedSocket in exceptionSockets:
        RemoveClient(notifiedSocket)