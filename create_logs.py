wars = [
    ("SPJBMX Collab 2", "win", "2024/11/13"), 
    ("Altar of Royals", "loss", "2024/11/15"), 
    ("Anti Funlord", "loss", "2024/11/17"), 
    ("Zanth Titans", "loss", "2024/11/21"), 
    ("Farming Only 2", "win", "2024/11/23"), 
    ("Christ Farm War", "loss", "2024/11/26"),
    ("Deadly Sinners", "win", "2024/11/30"),
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