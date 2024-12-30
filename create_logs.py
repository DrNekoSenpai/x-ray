wars = [
    ("Chatrapati...", "loss", "2024/12/12"), 
    ("Four and Twenty", "win", "2024/12/14"), 
    ("Eternal Flame", "win", "2024/12/16"),
    ("WAR unlimited15", "loss", "2024/12/21"), 
    (".CLAN BROTHERS", "loss", "2024/12/23"), 
    (".trueno farm 07", "loss", "2024/12/25"), 
    ("PNAYUNDRGROUND3", "loss", "2024/12/27"),
]

import os
    
for war in wars: 
    # Check if the corresponding file exists. 
    # If so, skip; we only want to create new logs. 
    if os.path.exists(f"./logs/{war[2].replace('/', '_')}_{war[0].replace(' ', '_').lower()}.txt"): 
        print(f"Log for {war[2].replace('/', '_')}_{war[0].replace(' ', '_')} already exists. Skipping...")
        continue

    with open(f"./logs/{war[2].replace('/', '_')}_{war[0].replace(' ', '_').lower()}.txt", "w") as f: 
        f.write(f"Win/loss: {war[1]}\nWar end date: {war[2].replace('/', '-')}\n\n")