import pytesseract, pyautogui

left, right, top, bottom = 1427, 1687, 232, 271
cropped = pyautogui.screenshot(region=(left, top, right - left, bottom - top))
weight = pytesseract.image_to_string(cropped)[:5]

if weight == "i2ioo": weight = "21000"

with open("weights.txt", "r", encoding="utf-8") as f:
    num_lines = sum(1 for line in f)

print(f"{num_lines + 1}. {weight}")

with open("weights.txt", "a", encoding="utf-8") as f:
    f.write(weight + "\n")