import os, datetime, json
with open("./inputs/war-log.json", "r", encoding="utf-8") as file: 
    wars = json.load(file)

for war in wars:  
    print(war, wars[war])
    war_date = war
    win_loss, enemy_clan = wars[war] 

    if os.path.exists(f"./strikes/logs/{war_date.replace('/', '_')}_{enemy_clan.replace(' ', '_').lower()}.txt"): 
        print(f"Log for {war_date.replace('/', '_')}_{enemy_clan.replace(' ', '_')} already exists. Skipping...")
        continue

    # Check if the war end date is in the future. 
    # If so, skip it. 
    if datetime.datetime.strptime(war_date, "%Y-%m-%d") > datetime.datetime.now(): 
        print(f"War {enemy_clan} ends in the future. Skipping...")
        continue

    with open(f"./strikes/logs/{war_date.replace('/', '_')}_{enemy_clan.replace(' ', '_').lower()}.txt", "w") as f: 
        if "blacklist" in win_loss: 
            f.write(f"Win/loss: {win_loss.split('/')[0]}\nWar end date: {war_date.replace('/', '-')}\nBlacklist conditional: {win_loss.split('/')[1]}\nEnemy clan: {enemy_clan}\n\n")
        else: 
            f.write(f"Win/loss: {win_loss}\nWar end date: {war_date.replace('/', '-')}\nEnemy clan: {enemy_clan}\n\n")