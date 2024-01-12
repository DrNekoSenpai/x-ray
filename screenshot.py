import os, pyautogui

if not os.path.exists("./screenshots/war"): os.makedirs("./screenshots/war")
if not os.path.exists("./screenshots/fwa"): os.makedirs("./screenshots/fwa")

war_base = False

if war_base: 
    # Find the number of items in the war folder. 
    num_items = len([name for name in os.listdir('./screenshots/war') if os.path.isfile(os.path.join('./screenshots/war', name))])
    pyautogui.screenshot(f"./screenshots/war/{num_items}.png")

else:
    # Find the number of items in the fwa folder. 
    num_items = len([name for name in os.listdir('./screenshots/fwa') if os.path.isfile(os.path.join('./screenshots/fwa', name))])
    pyautogui.screenshot(f"./screenshots/fwa/{num_items}.png")