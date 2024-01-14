import os, pyautogui
from PIL import Image

if not os.path.exists("./screenshots/war"): os.makedirs("./screenshots/war")
if not os.path.exists("./screenshots/fwa"): os.makedirs("./screenshots/fwa")

war_base = False

if war_base: path = "./screenshots/war/"
else: path = "./screenshots/fwa/"
num = len(os.listdir(path))+1

pyautogui.moveTo(1920/2, 1080/2)
pyautogui.click()
pyautogui.click()

# Scroll down
for _ in range(10): pyautogui.scroll(-1000)

pyautogui.mouseDown() 
pyautogui.moveRel(500, 500)
pyautogui.mouseUp()

pyautogui.screenshot(f"{path}{num}a.png")

pyautogui.mouseDown() 
pyautogui.moveRel(0, -1000)
pyautogui.mouseUp()

pyautogui.screenshot(f"{path}{num}b.png")

left, right = 250, 1920
top_a, bottom_a = 155, 715
top_b, bottom_b = 175, 735

image_a = Image.open(f"{path}{num}a.png")
image_a = image_a.crop((left, top_a, right, bottom_a))

image_b = Image.open(f"{path}{num}b.png")
image_b = image_b.crop((left, top_b, right, bottom_b))

image = Image.new("RGB", (image_a.width, image_a.height + image_b.height))
image.paste(image_a, (0, 0))
image.paste(image_b, (0, image_a.height))
image.save(f"{path}{num}.png")

os.remove(f"{path}{num}a.png")
os.remove(f"{path}{num}b.png")