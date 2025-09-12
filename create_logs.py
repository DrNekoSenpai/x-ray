wars = [
    ("3ASTARDOS FARM", "win", "2025/06/13"), 
    ("MARVELS", "loss", "2025/06/15"),
    ("Red Alert", "loss", "2025/06/17"), 
    ("BD LORD$", "loss", "2025/06/19"),
    ("trueno farm 07", "win", "2025/06/21"),
    ("BEST WAR CLAN", "loss", "2025/06/23"),
    ("The Deadlands", "win", "2025/06/25"),
    ("Deathstar +++", "win", "2025/06/27"),
    ("RSCM Warriors", "blacklist win/true", "2025/06/30"),
    ("clasher_clan", "win", "2025/07/02"),
    (".CLAN BROTHERS", "win", "2025/07/17"), 
    ("IMPERIO ROMANO", "blacklist loss/true", "2025/07/19"),
    ("Phantoms", "win", "2025/07/21"),
    ("Elite Power", "win", "2025/07/23"),
    ("Web Rage Farm 7", "win", "2025/07/26"),
    ("trueno farm 07", "loss", "2025/07/28"),
    ("sidoarjo winner", "win", "2025/07/30"),
    ("BItukOnZ", "loss", "2025/08/01"),
    ("TE-warriors", "win", "2025/08/13"),
    ("Farmwars", "loss", "2025/08/17"),
]

import os, datetime

for war in wars: 
    # Check if the corresponding file exists. 
    # If so, skip; we only want to create new logs. 
    if os.path.exists(f"./strikes/logs/{war[2].replace('/', '_')}_{war[0].replace(' ', '_').lower()}.txt"): 
        print(f"Log for {war[2].replace('/', '_')}_{war[0].replace(' ', '_')} already exists. Skipping...")
        continue

    # Check if the war end date is in the future. 
    # If so, skip it. 
    if datetime.datetime.strptime(war[2], "%Y/%m/%d") > datetime.datetime.now(): 
        print(f"War {war[0]} ends in the future. Skipping...")
        continue

    with open(f"./strikes/logs/{war[2].replace('/', '_')}_{war[0].replace(' ', '_').lower()}.txt", "w") as f: 
        if "blacklist" in war[1]: 
            f.write(f"Win/loss: {war[1].split('/')[0]}\nWar end date: {war[2].replace('/', '-')}\nBlacklist conditional: {war[1].split('/')[1]}\n\n")
        else: 
            f.write(f"Win/loss: {war[1]}\nWar end date: {war[2].replace('/', '-')}\n\n")