from tkinter import filedialog
import io
import pickle
from PIL import Image, ImageTk
import numpy as np

def OpenImage():

    file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.bmp;*.gif")])
    if not file_path:
        return None

    img = Image.open(file_path)
    #Serialising image
    imgPickle = PickleImage(img)
    
    return img, imgPickle


def PickleImage(img):
    #Save the image to a byte buffer (to pickle it)
    imgByteArr = io.BytesIO()
    img.save(imgByteArr, format='PNG')
    imgByteArr.seek(0)  #Go to the beginning of the byte buffer
    return pickle.dumps(imgByteArr.getvalue())

#Unpickled the sent image so that it can be used in recipient chat
def UnpickleImage(pickled_data):
    #Unpickle the image from the byte data
    imgByteData = pickle.loads(pickled_data)
    imgByteArray = io.BytesIO(imgByteData)
    img = Image.open(imgByteArray)
    return img

#Convert an image to ImageTk format so it can be displayed in the chat
def ConvertImagePIL(img):
    imgNP = np.array(img)
    imgTk = ImageTk.PhotoImage(img)
    return imgNP, imgTk

def ConvertImageNP(imgNP):
    imagePIL = Image.fromarray(imgNP)
    imageTk = ImageTk.PhotoImage(imagePIL)
    return imagePIL, imageTk