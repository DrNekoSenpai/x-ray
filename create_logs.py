wars = [
    ("SPJBMX Collab 2", "win", "11/13"), 
    ("Altar of Royals", "loss", "11/15"), 
    ("Anti Funlord", "loss", "11/17")
]

import os
    
for war in wars: 
    # Check if the corresponding file exists. 
    # If so, skip; we only want to create new logs. 
    if os.path.exists(f"./logs/{war[2].replace('/', '')}_{war[0].replace(' ', '_').lower()}.txt"): 
        print(f"Log for {war[0]} already exists. Skipping...")
        continue

    with open(f"./logs/{war[2].replace('/', '')}_{war[0].replace(' ', '_').lower()}.txt", "w") as f: 
        f.write(f"Win/loss: {war[1]}\nWar end date: {war[2].replace('/', '')}\n\n")