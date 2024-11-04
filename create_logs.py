wars = [
    ("SPJBMX Collab 2", "win", "10/15"), 
    ("PHOENIX 2", "loss", "10/17"), 
    ("Nattens Ninjaer", "loss", "10/19"), 
    ("MALAYA ALL FARM", "win", "10/21"), 
    ("CLAN BROTHERS", "win", "10/23"), 
    ("The Kingsmen", "loss", "10/26"), 
    ("tsp warrior", "loss", "10/28"), 
    ("MALAYA ALL FARM", "loss", "10/31"), 
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