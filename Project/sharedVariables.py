currentRecipient = ""
userButtonDict = None

#Tkinter Frames
root = None
ContactWindow = None #Shows all the contacts/connections
MessageWindow = None #Contains the chat window and the send area
ReceiveFrame = None #Shows the message dialogue
SendingFrame = None

secondConvoFrame = None

ImageFrame = None

#Important labels
selectConnectionMessage = None #Message telling user to select a contact.


#Client/Server
myClient = None
socketList = None