import pyautogui, pytesseract, time, numpy as np
from PIL import Image

left, right, up, down = 148, 389, 50, 94

name = pyautogui.screenshot().crop((left, up, right, down))

def black_and_white(image, threshold=225):
    image = np.array(image)
    mask = (image > threshold).all(axis=-1)
    image[mask] = [0, 0, 0]
    image[~mask] = [255, 255, 255]
    return Image.fromarray(image, 'RGB')

name = black_and_white(name)
name.show()

name = pytesseract.image_to_string(name)
print(name)