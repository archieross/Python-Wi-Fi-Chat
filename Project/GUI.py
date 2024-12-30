
if __name__ == "__main__":
    from tkinter import *
    from PIL import Image, ImageTk
    from tkinter import messagebox
    import threading
    from tkinter import LabelFrame

    

    #Importing external functions
    from Functionality import SendUsername, MessageHandler, SendText, OpenPhotoSelect, ChangeRecipient, NpToTkImage

##############################
#Login Screen

def CreateLoginPage(BuildChat):
    loginFrame = LabelFrame(shared.root, text="Join")

    #Image
    imagePath = "/Users/archieross/Desktop/Portfolio/Python Chat App/Chat Room Project/bubble.png"
    image = Image.open(imagePath)
    photo = ImageTk.PhotoImage(image)
    iconLabel = Label(shared.root, image=photo, bg='white')
    iconLabel.photo = photo


    #Entry Widgets
    usernameLabel = Label(loginFrame, text='Please enter a username.', bg='grey')
    usernameEntry = Entry(loginFrame, bg='white')
    usernameButton = Button(loginFrame, text='Submit', command=lambda: SendUsername(usernameEntry, loginFrame, iconLabel, BuildChat))

    # Place widgets in the grid
    iconLabel.grid(column=1, row=1, rowspan=3)
    loginFrame.grid(column=2, row=2)

    usernameLabel.grid(column=2, row=1, sticky='ew', padx=10, pady=10)
    usernameEntry.grid(column=2, row=2, sticky='ew', padx=10, pady=10)
    usernameButton.grid(column=2, row=3, sticky='ew', padx=10, pady=10)

    #Set column weights so that they expand evenly
    shared.root.grid_columnconfigure(0, weight=1)
    shared.root.grid_columnconfigure(1, weight=1)
    shared.root.grid_columnconfigure(2, weight=1)
    shared.root.grid_columnconfigure(4, weight=1)

    #Row weight for vertical expansion
    shared.root.grid_rowconfigure(0, weight=4)
    shared.root.grid_rowconfigure(1, weight=1)
    shared.root.grid_rowconfigure(2, weight=1)
    shared.root.grid_rowconfigure(3, weight=1)
    shared.root.grid_rowconfigure(4, weight=4)


###############################

#Reset the weights of rows and column in the root grid
def ResetGridConfig():

    import sharedVariables as shared

    for i in range(shared.root.grid_size()[0]):
        shared.root.grid_columnconfigure(i, weight=0, minsize=0)
    
    for i in range(shared.root.grid_size()[1]):
        shared.root.grid_rowconfigure(i, weight=0, minsize=0)







def BuildChat():
    
    import sharedVariables as shared

    #Root Configuration
    ResetGridConfig()
    shared.root.grid_columnconfigure(0, weight=1, uniform="equal")
    shared.root.grid_columnconfigure(1, weight=6, uniform="equal")
    shared.root.grid_rowconfigure(0, weight=1, uniform="equal")
    shared.root.pack_propagate(False)
    shared.root.config(bg='navy')

    

    #Contact Window
    shared.ContactWindow = LabelFrame(shared.root, text="Connections")
    shared.ContactWindow.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

    shared.ContactWindow.grid_columnconfigure(1, weight=1, uniform="equal")
    

    #Get active server connections so the client can interact with them
    usernameButtonDict = {}
    contactUsernames = list(shared.myClient.clients.keys())
    for i in range(len(contactUsernames)):
        usernameButtonDict[contactUsernames[i]] = Button(shared.ContactWindow, text=contactUsernames[i], command=lambda username=contactUsernames[i]: ChangeRecipient(username))
        usernameButtonDict[contactUsernames[i]].grid(row=i, column=1)

    shared.userButtonDict = usernameButtonDict


    ######################### Message Box ############################################
    #Message Window
    shared.MessageWindow = LabelFrame(shared.root)
    shared.MessageWindow.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
    shared.MessageWindow.grid_rowconfigure(0, weight=5, uniform="equal")
    shared.MessageWindow.grid_rowconfigure(1, weight=1, uniform="equal")
    shared.MessageWindow.grid_columnconfigure(0, weight=1, uniform="equal")

    ########## Receive ##########
    #Here we see the message dialogue
    shared.ReceiveFrame = LabelFrame(shared.MessageWindow, text="Receiving", padx=20, pady=20)


    ########Formate/Send Message Frame##############
    ### Visuals ####
    shared.SendingFrame = LabelFrame(shared.MessageWindow, text="Sending")
    shared.SendingFrame.grid_rowconfigure(0, weight=1, uniform="equal")
    shared.SendingFrame.grid_columnconfigure(0, weight=6, uniform="equal")
    shared.SendingFrame.grid_columnconfigure(1, weight=1, uniform="equal")
    shared.SendingFrame.grid_columnconfigure(2, weight=1, uniform="equal")

    clientMessage = Text(shared.SendingFrame, wrap=WORD, bg ="white", fg="black", bd = 1, highlightcolor='blue')
    sendButton = Button(shared.SendingFrame, text='Send', bd=1, relief='sunken', command=lambda: SendText(sendButton, clientMessage))
    photoButton = Button(shared.SendingFrame, text = 'Attach\nPhoto', command = lambda: OpenPhotoSelect(photoButton))

    clientMessage.grid(row=0, column=0, sticky='nsew')
    sendButton.grid(row=0,column=1, sticky='nsew')
    photoButton.grid(row=0,column=2, sticky='nsew')

    shared.ReceiveFrame.grid(row=0, column=0, padx=10, pady=10, sticky = 'nsew')
    shared.SendingFrame.grid(row=1, column=0, padx=10, pady=10, sticky='nsew')

    if shared.currentRecipient == "":

        shared.selectConnectionMessage= Label(shared.MessageWindow, text="Please select a connection to begin a conversation.",font=('Century Schoolbook', 20, 'italic bold'))
        shared.selectConnectionMessage.grid(row=0, column=0, rowspan=2, sticky='nsew')
    

    #Starting Background Thread
    threading.Thread(target=lambda : MessageHandler()).start()



def ChangeChat():

    import sharedVariables as shared
    from tkinter import BOTH, Frame, LabelFrame, Label, Canvas, LEFT, RIGHT, VERTICAL, Y
    from tkinter import ttk

    

    if shared.selectConnectionMessage:
        shared.selectConnectionMessage.grid_forget()
    


    shared.ReceiveFrame.grid_forget()

    
    shared.ReceiveFrame = LabelFrame(shared.MessageWindow, text="Receiving", padx=20, pady=20)
    shared.ReceiveFrame.grid(row=0, column=0, padx=10, pady=10, sticky = 'nsew')

    ##########

    
    mainFrame = Frame(shared.ReceiveFrame)  # mainFrame must be inside the root window
    mainFrame.pack(fill=BOTH, expand=1)

    #Create a canvas
    myCanvas = Canvas(mainFrame, bg='black')
    myCanvas.pack(side=LEFT, fill=BOTH, expand=1)

    #add a scrollbar to the canvas.
    myScrollbar = ttk.Scrollbar(mainFrame, orient=VERTICAL, command=myCanvas.yview)
    myScrollbar.pack(side=RIGHT, fill=Y)

    #Configure the canvas
    myCanvas.configure(yscrollcommand=myScrollbar.set)
    myCanvas.bind('<Configure>', lambda e: myCanvas.configure(scrollregion=myCanvas.bbox('all')))

    #Create another frame inside the canvas.
    secondFrame = Frame(myCanvas, bg='black')

    #secondFrame.pack(fill=BOTH)


    secondFrame.grid_columnconfigure(0, weight=1, uniform="equal")
    secondFrame.grid_columnconfigure(1, weight=2, uniform="equal")
    secondFrame.grid_columnconfigure(2, weight=1, uniform="equal" )

    initialWidth = myCanvas.winfo_width() + myScrollbar.winfo_width()

    # Add the new frame to a window in the canvas
    window_id = myCanvas.create_window((0, 0), window=secondFrame, anchor='nw', width=initialWidth)

    # Dynamically adjust the width of secondFrame based on the canvas
    def update_second_frame_width(event):
        myCanvas.itemconfig(window_id, width=event.width)
        myCanvas.yview_moveto(1.0)

    myCanvas.bind('<Configure>', update_second_frame_width, add=True)



    prevPerson = ""
    curentRow = -1
    #Here we need to rebuild with the dialogue
    for i in range(len(shared.myClient.dialogue[shared.currentRecipient])):

        print("Scrollbar position:", myScrollbar.get())

    
        message = shared.myClient.dialogue[shared.currentRecipient][i]

        if message.sender != prevPerson:
            curentRow += 1
            Label(secondFrame, bg ='black').grid(row=curentRow, column= 1, sticky='nsew')


        prevPerson = message.sender

        if message.sender == shared.myClient.myUsername:
            columnIndex = 2
            backgroundColor = 'blue'
            foreground = 'white'
        else:
            columnIndex = 0
            backgroundColor = 'white'
            foreground = 'black'
        

        curentRow += 1

        if message.messageType == 'text':
                item = Label(secondFrame, text=message.message, bg=backgroundColor, fg =foreground, wraplength=200,  # Set the wrap length in pixels
                    justify="left")
        else:
                from Functionality import  NpToTkImage
                tkImage, defaultImageWidth = NpToTkImage(message.message)
                item = Label(secondFrame, image=tkImage, width=defaultImageWidth)
                item.image = tkImage
        
        
        item.grid(row = curentRow, column=columnIndex)
    
    
                

    
#############################
#Show Image Variants

def CancelImageSelection():
    import sharedVariables as shared
    shared.ImageFrame.destroy()


def ShowImageVariants(images, photoButton):

    from tkinter import Frame, StringVar, Radiobutton, Button, Label
    import sharedVariables as shared

    shared.ImageFrame = Frame(shared.root, bg='navy', bd=2, padx=20, pady=20)
    shared.ImageFrame.place(relx=0, rely=0, relwidth=1, relheight=1)
    shared.ImageFrame.grid_rowconfigure(1, weight=1) #Please select your preferred variant
    shared.ImageFrame.grid_rowconfigure(2, weight=1) #Gap
    shared.ImageFrame.grid_rowconfigure(3, weight=1) #Image 1 and 2
    shared.ImageFrame.grid_rowconfigure(4, weight=1) #Gap
    shared.ImageFrame.grid_rowconfigure(5, weight=1) #Image 3 and 4
    shared.ImageFrame.grid_rowconfigure(6, weight=1) #Gap
    shared.ImageFrame.grid_rowconfigure(7, weight=1) #Cancel and Send Buttons

    shared.ImageFrame.grid_columnconfigure(1, weight=1) #image 1 and 3, cancel
    shared.ImageFrame.grid_columnconfigure(2, weight=1) #gap
    shared.ImageFrame.grid_columnconfigure(3, weight=1) #image 2 and 4, send

    title = Label(shared.ImageFrame, text = "Please select which image you would like to send.")

    title.grid(row=1, column=1, columnspan=3, sticky='nsew')


    from Functionality import NpToTkImage
    tkImage1 = images['normal']
    tkImage1, defaultImageWidth = NpToTkImage(tkImage1)

    tkImage2 = images['sepia']
    tkImage2, defaultImageWidth = NpToTkImage(tkImage2)

    tkImage3 = images['sketch']
    tkImage3, defaultImageWidth = NpToTkImage(tkImage3)

    tkImage4 = images['pencil']
    tkImage4, defaultImageWidth = NpToTkImage(tkImage4)


    selectedImage = StringVar(value="normal")


    frame1 = Frame(shared.ImageFrame)
    frame1.grid(row = 3, column=1)
    imageLabel1 = Label(frame1, image=tkImage1, width=defaultImageWidth)
    radio1 = Radiobutton(frame1, variable=selectedImage, value="normal")
    imageLabel1.image = tkImage1
    imageLabel1.pack()
    radio1.pack()


    frame2 = Frame(shared.ImageFrame)
    frame2.grid(row = 3, column=3)
    imageLabel2 = Label(frame2, image=tkImage2, width=defaultImageWidth)
    radio2 = Radiobutton(frame2, variable=selectedImage, value="sepia")
    imageLabel2.image = tkImage2
    imageLabel2.pack()
    radio2.pack()


    

    frame3 = Frame(shared.ImageFrame)
    frame3.grid(row = 5, column=1)
    imageLabel3 = Label(frame3, image=tkImage3, width=defaultImageWidth)
    radio3 = Radiobutton(frame3, variable=selectedImage, value="sketch")
    imageLabel3.image = tkImage3
    imageLabel3.pack()
    radio3.pack()


    frame4 = Frame(shared.ImageFrame)
    frame4.grid(row = 5, column=3)
    imageLabel4 = Label(frame4, image=tkImage4, width=defaultImageWidth)
    radio4 = Radiobutton(frame4, variable=selectedImage, value="pencil")
    imageLabel4.image = tkImage4
    imageLabel4.pack()
    radio4.pack()


    from Functionality import RevertAttachButton, SendImage
    cancelButton = Button(shared.ImageFrame, text='Cancel', command= lambda: RevertAttachButton(photoButton))
    sendButton = Button(shared.ImageFrame, text='Send', command=lambda: SendImage(images[selectedImage.get()], photoButton))


    cancelButton.grid(row=7, column=1, sticky='nsew')
    sendButton.grid(row=7, column=3, sticky='nsew')



#############################

def onClosing():
        # Display a confirmation dialog
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            # Perform any cleanup or save work here
            print("Closing the application...")
            shared.root.destroy()  # Close the application
            from sys import exit
            exit()

if __name__ == "__main__":

    import sharedVariables as shared
    #Initialising
    shared.root = Tk()
    shared.root.config(bg='white')
    shared.root.protocol("WM_DELETE_WINDOW", onClosing)
    screen_width = shared.root.winfo_screenwidth()
    screen_height = shared.root.winfo_screenheight()
    #Set the window size to fill the screen
    shared.root.geometry(f"{screen_width}x{screen_height}")

    defaultImageWidth = 400

    #Initialising Login Screen
    CreateLoginPage(BuildChat)


    ###################################


    shared.root.mainloop()