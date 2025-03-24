import pyautogui, time

with open("weights.txt", "r") as f:
    weights = [line.strip() for line in f.readlines()]

time.sleep(2)
pyautogui.hotkey("alt", "tab")
pyautogui.hotkey("ctrl", "a")
pyautogui.press("delete")

for w in weights: 
    pyautogui.typewrite(w)
    time.sleep(0.1)
    pyautogui.hotkey('tab')
    time.sleep(0.1)