wars = [
    ("Christ Farm War", "win", "2025/01/13"), 
    ("Mad Serbian's", "blacklist win/true", "2025/01/15"), 
    ("BACARRA KigToT", "blacklist win/true", "2025/01/17"),
    ("MALAYA ALL PRO3", "win", "2025/01/21"), 
    ("Gabbar", "win", "2025/01/24"),
    ("MALAYA ALL FARM", "win", "2025/01/26"),
    ("sidoarjo winner", "win", "2025/01/28"),
    ("Viminal Hill", "win", "2025/02/01")
]

import os
    
for war in wars: 
    # Check if the corresponding file exists. 
    # If so, skip; we only want to create new logs. 
    if os.path.exists(f"./logs/{war[2].replace('/', '_')}_{war[0].replace(' ', '_').lower()}.txt"): 
        print(f"Log for {war[2].replace('/', '_')}_{war[0].replace(' ', '_')} already exists. Skipping...")
        continue

    with open(f"./logs/{war[2].replace('/', '_')}_{war[0].replace(' ', '_').lower()}.txt", "w") as f: 
        if "blacklist" in war[1]: 
            f.write(f"Win/loss: {war[1].split('/')[0]}\nWar end date: {war[2].replace('/', '-')}\nBlacklist conditional: {war[1].split('/')[1]}\n\n")
        else: 
            f.write(f"Win/loss: {war[1]}\nWar end date: {war[2].replace('/', '-')}\n\n")