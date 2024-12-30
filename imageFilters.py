import cv2
import numpy as np

def GetPencilSketch(NpArray):
    pencil, sketch = cv2.pencilSketch(NpArray, sigma_s=40, sigma_r=0.06, shade_factor=0.05)
    return pencil, sketch

def GetSepia(NpArray):

    #Sepia filter
    sepia = np.array([[0.272, 0.534, 0.131],
                    [0.349, 0.686, 0.168],
                    [0.393, 0.769, 0.189]])
    sepiaImage = cv2.transform(NpArray, sepia)

    return sepiaImage