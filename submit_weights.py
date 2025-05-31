import pyautogui, time

with open("./outputs/weights.txt", "r") as f:
    weights = [line.strip() for line in f.readlines()]

# for w in weights: 
#     if int(w) < 50000: 
#         w = str(int(w) * 5)

weights = [str(int(w) * 5) if int(w) < 50000 else w for w in weights]

with open("./outputs/weights.txt", "w") as f:
    for w in weights: 
        f.write(w + "\n")

time.sleep(2)
pyautogui.hotkey("alt", "tab")
pyautogui.hotkey("ctrl", "a")
pyautogui.press("delete")

for w in weights: 
    pyautogui.typewrite(w)
    time.sleep(0.1)
    pyautogui.hotkey('tab')
    time.sleep(0.1)