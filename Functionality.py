#############
#important cross script variables
HEADER_LENGTH = 10
defaultImageWidth = 200

###############
#Import libraries
from tkinter import *
from tkinter import messagebox
import select
import pickle
from PIL import Image, ImageTk
from tkinter import filedialog
import numpy as np

################
#Importing Functions/Classes

from client import Client


################
#Login Functions

def SendUsername(usernameEntry, loginFrame, iconLabel, BuildChat):

    import sharedVariables as shared

    chosenUsername = usernameEntry.get()

    if chosenUsername != '':

        try:
            shared.myClient = Client(chosenUsername)
            shared.socketList = [shared.myClient.clientSocket]
            usernameSet = True
            iconLabel.grid_forget()
            loginFrame.grid_forget()
            BuildChat()
        
        except:
            usernameEntry.grid_forget()
            usernameEntry = Entry(loginFrame, bg='white')
            usernameEntry.grid(column=2, row=2, sticky='ew', padx=10, pady=10)
            displayMessage = f"Username '{chosenUsername}' is already taken. Please choose another."
            messagebox.showwarning("Invalid Username", displayMessage)
            print('warning')
      

########################
#Main Program Functions

def ChangeRecipient(contact):

    import sharedVariables as shared

    try:
        gridInfo = shared.userButtonDict[shared.currentRecipient].grid_info()
        currentRow, currentColumn = gridInfo['row'], gridInfo['column']
        shared.userButtonDict[shared.currentRecipient] = Button(shared.ContactWindow, text=shared.currentRecipient, command=lambda username=shared.currentRecipient: ChangeRecipient(username))
        shared.userButtonDict[shared.currentRecipient].grid(row=currentRow, column=currentColumn)
        print("TRYYYY CATCGGHG")
    except:
         pass
    
    from GUI import ChangeChat
    import sharedVariables as shared
    shared.currentRecipient = contact
    shared.userButtonDict[contact].config(highlightbackground='navy')
    print(f'New recipient: {shared.currentRecipient, contact}')
    ChangeChat()
    

def BuildContactList():

    import sharedVariables as shared

    for contactButton in shared.ContactWindow.winfo_children():
        contactButton.destroy()

    usernameButtonDict = {}
    contactUsernames = list(shared.myClient.clients.keys())

    for i in range(len(contactUsernames)):
        usernameButtonDict[contactUsernames[i]] = Button(shared.ContactWindow, text=contactUsernames[i], command=lambda username=contactUsernames[i]: ChangeRecipient(username)) #Must do username = or it will use the last i. must be within new scope.
        usernameButtonDict[contactUsernames[i]].grid(row=i, column=1)
    
    shared.userButtonDict = usernameButtonDict
    
    return usernameButtonDict


#Accepts the message from the server and functions accordingly to message type.
def Update(myCommunication):
        
        from GUI import ChangeChat
        import sharedVariables as shared



        
        print(vars(myCommunication))

        if myCommunication.messageType == 'removeUser':
            del shared.myClient.clients[myCommunication.message]
            #Potentially delete the chat
            BuildContactList()
    
        if myCommunication.messageType == 'joinRequest':
            shared.myClient.clients[myCommunication.message] = 1
            shared.myClient.dialogue[myCommunication.message] = []
            BuildContactList()
        
        elif myCommunication.messageType in ['text', 'photo', 'image']:
            from GUI import ChangeChat
            #We must build our conversation
            shared.myClient.dialogue[myCommunication.sender].append(myCommunication)

            if myCommunication.sender == shared.currentRecipient:
                ChangeChat()


def MessageHandler():

    import sharedVariables as shared

    while True:
            #Wait for the complete message to arrive
            readable, _, _ = select.select(shared.socketList, [], [])
            if readable:
                communicationHeader = shared.myClient.clientSocket.recv(HEADER_LENGTH)
                communicationHeader = int(communicationHeader.decode('utf-8').strip())

                serialisedCommunication = shared.myClient.clientSocket.recv(communicationHeader)
                myCommunication = pickle.loads(serialisedCommunication)
                Update(myCommunication)


def RevertSendButton(sendButton, clientMessage):
    from GUI import ChangeChat
    import sharedVariables as shared
    ChangeChat()
    #Change the button back
    sendButton.grid_forget()
    sendButton = Button(shared.SendingFrame, text='Send', bd=1, relief='sunken', command=lambda: SendText(sendButton,  clientMessage))
    sendButton.grid(row=0,column=1, sticky='nsew')


def SendText(sendButton, clientMessage):
        
        import sharedVariables as shared

        #Temp disable button
        sendButton.grid_forget()

        sendButton = Label(shared.SendingFrame, text='Send', bd=1, relief='sunken', bg='blue')
        sendButton.grid(row=0,column=1, sticky='nsew')
        
        #####


        submittedMessage = clientMessage.get("1.0", END).strip() # Get content from the beginning to the end
        print(submittedMessage)
        print(type(submittedMessage))
        clientMessage.delete("1.0", END)

        import sharedVariables as shared
        shared.myClient.SendMessage(messageType='text', message=submittedMessage, recipient=shared.currentRecipient)
        RevertSendButton(sendButton, clientMessage)

def ResizeImage(desiredWidth, image):
    originalWidth, originalHeight = image.size
    aspectRatio = originalHeight / originalWidth
    new_height = int(desiredWidth * aspectRatio)
    #Resize the image while keeping the aspect ratio
    resized_image = image.resize((desiredWidth, new_height), Image.Resampling.LANCZOS)
    #Convert the image to a NumPy array
    npArray = np.array(resized_image)

    return npArray


def RevertAttachButton(photoButton):

    import sharedVariables as shared
     
    #Change the button back
    photoButton.grid_forget()
    photoButton = Button(shared.SendingFrame, text = 'Attach\nPhoto', command=lambda: OpenPhotoSelect(photoButton))
    photoButton.grid(row=0,column=2, sticky='nsew')

     


def SendImage(imageArray, photoButton):
        
        import sharedVariables as shared
        from GUI import ChangeChat
        
        shared.ImageFrame.destroy()

        #Temp disable button
        photoButton.grid_forget()
        photoButton = Label(shared.SendingFrame, text = 'Attach\nPhoto', bg='blue')
        photoButton.grid(row=0,column=2, sticky='nsew')
        #####
        shared.myClient.SendMessage(messageType='image', message=imageArray, recipient=shared.currentRecipient)
        
        ChangeChat()

        RevertAttachButton(photoButton)

        


def OpenPhotoSelect(photoButton):
        
        import sharedVariables as shared
        from GUI import ShowImageVariants
        from imageFilters import GetPencilSketch, GetSepia

        #myImg = ImageTk.PhotoImage(Image.open(ImgPath))
        #myClient.SendMessage(messageType='image', message=myImg, recipient=shared.currentRecipient)

        filePath = filedialog.askopenfilename(
        filetypes=[("Image Files", "*.png *.gif *.jpg")]  #Restrict to PNG, GIF or JPG
    )

        image = Image.open(filePath).convert("RGB")
        resizedImage = ResizeImage(200, image)
        npArray = np.array(resizedImage)


        #HERE WE MUST CALL THE OTHER FUNCTION TO CHOOSE WHICH FILTER
        images = {
             'normal': npArray
        }
        images['pencil'], images['sketch'] = GetPencilSketch(npArray)
        images['sepia'] = GetSepia(npArray)

        
        ShowImageVariants(images, photoButton)
        
        


###############

def NpToTkImage(NpArray):
     
    image = Image.fromarray(NpArray)
    tkImage = ImageTk.PhotoImage(image)

    return tkImage, defaultImageWidth