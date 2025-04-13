wars = [
    ("sidoarjo winner", "win", "2025/04/13"), 
]

import os, datetime
    
for war in wars: 
    # Check if the corresponding file exists. 
    # If so, skip; we only want to create new logs. 
    if os.path.exists(f"./logs/{war[2].replace('/', '_')}_{war[0].replace(' ', '_').lower()}.txt"): 
        print(f"Log for {war[2].replace('/', '_')}_{war[0].replace(' ', '_')} already exists. Skipping...")
        continue

    # Check if the war end date is in the future. 
    # If so, skip it. 
    if datetime.datetime.strptime(war[2], "%Y/%m/%d") > datetime.datetime.now(): 
        print(f"War {war[0]} ends in the future. Skipping...")
        continue

    with open(f"./logs/{war[2].replace('/', '_')}_{war[0].replace(' ', '_').lower()}.txt", "w") as f: 
        if "blacklist" in war[1]: 
            f.write(f"Win/loss: {war[1].split('/')[0]}\nWar end date: {war[2].replace('/', '-')}\nBlacklist conditional: {war[1].split('/')[1]}\n\n")
        else: 
            f.write(f"Win/loss: {war[1]}\nWar end date: {war[2].replace('/', '-')}\n\n")