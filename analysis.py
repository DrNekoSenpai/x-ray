with open("raw.txt", "r", encoding="utf-8") as file: 
    lines = file.readlines()

import os, re
hit_pattern = re.compile(r":(\d{2})::\d{2}::Sword::(\d{2})::\d{2}:(:Star:|:FadedStar:|:Blank:)(:Star:|:FadedStar:|:Blank:)(:Star:|:FadedStar:|:Blank:):\d{2,3}:[💥]? .{2}(.*).{2}")

def regular_keyboard(input_string): 
    pattern = r"^[A-Za-z0-9 !@#$%^&*()\-=\[\]{}|;:'\",.<>/?\\_+]*$"
    return re.match(pattern, input_string) is not None 

win_loss_pattern = re.compile(r"Win/loss: (win|loss)")
enemy_clan_pattern = re.compile(r"Enemy clan: (.*)")
war_end_date_pattern = re.compile(r"War end date: (\d{4})")

win_loss = re.search(win_loss_pattern, lines[0]).group(1)
enemy_clan = re.search(enemy_clan_pattern, lines[1]).group(1)
war_end_date = re.search(war_end_date_pattern, lines[2]).group(1)

attack_list = None

log = []
two_missed_hits = []
one_missed_hit = []

skip = [
    "Tenth Situation", 
    "Dark Hell Mutt", 
    "Hostile Doctor", 
    "Kami", 
    "I Sofa King",
    "BumblinMumbler",
    "Bran6",
    "Senpai",
]

for line in lines:
    match = hit_pattern.search(line)
    if match:
        attacker = match.group(1)
        defender = match.group(2)
        star1 = match.group(3)
        star2 = match.group(4)
        star3 = match.group(5)
        stars = len([star for star in [star1, star2, star3] if star != ":Blank:"])
        player_name = match.group(6)

        if player_name == "JALVIN ø": player_name = "JALVIN"
        if player_name == "★ıċєʏקѧṅṭś★": player_name = "IceyPants"
        if "™" in player_name: player_name = player_name.replace("™", "")
        if "✨" in player_name: player_name = player_name.replace("✨", "")

        if not regular_keyboard(player_name):
            print(f"Player name {player_name} is not valid. Please input the name manually.")
            player_name = input("Name: ")
        
        log.append((player_name, attacker, defender, stars))

    if "2 Remaining Attacks" in line.strip(): 
        attack_list = 2
        continue
    
    if "1 Remaining Attack" in line.strip():
        attack_list = 1
        continue

    if attack_list == 2: 
        player_name = line.strip()[8:]
        print(f"{player_name} missed two hits")

        if player_name == "JALVIN ø": player_name = "JALVIN"
        if player_name == "★ıċєʏקѧṅṭś★": player_name = "IceyPants"
        if "™" in player_name: player_name = player_name.replace("™", "")
        if "✨" in player_name: player_name = player_name.replace("✨", "")

        if not regular_keyboard(player_name):
            print(f"Player name {player_name} is not valid. Please input the name manually.")
            player_name = input("Name: ")

        two_missed_hits.append(player_name)

    if attack_list == 1:
        player_name = line.strip()[8:]
        print(f"{player_name} missed one hit")

        if player_name == "JALVIN ø": player_name = "JALVIN"
        if player_name == "★ıċєʏקѧṅṭś★": player_name = "IceyPants"
        if "™" in player_name: player_name = player_name.replace("™", "")
        if "✨" in player_name: player_name = player_name.replace("✨", "")

        if not regular_keyboard(player_name):
            print(f"Player name {player_name} is not valid. Please input the name manually.")
            player_name = input("Name: ")

        one_missed_hit.append(player_name)

with open("strikes-input.txt", "w", encoding="utf-8") as file: 
    for entry in log: 
        player_name, attacker, defender, stars = entry
        if player_name in skip or "Unicorn" in player_name: continue
        if win_loss == "l": 
            mirror = attacker == defender 
            if mirror and stars > 2: 
                print(f"Warning: {player_name} three-starred on a loss")
                file.write(f"3\n{player_name}\ny\n7\n1\n{enemy_clan}\n")
            elif not mirror and not int(attacker) < 6 and int(defender) < 6 and stars > 1: 
                print(f"Warning: {player_name} sniped for more than one star on a loss")
                file.write(f"3\n{player_name}\ny\n7\n3\n{enemy_clan}\n")
        if win_loss == "w": 
            mirror = attacker == defender 
            if not mirror and not int(attacker) < 6 and int(defender) < 6 and stars > 2: 
                print(f"Warning: {player_name} sniped for more than two stars on a win")
                file.write(f"3\n{player_name}\ny\n7\n2\n{enemy_clan}\n")

    for entry in one_missed_hit: 
        # Find the corresponding entry in the log; find their other hit 
        if entry in skip or "Unicorn" in entry: continue
        for log_entry in log: 
            if log_entry[0] == entry: 
                mirror = log_entry[1] == log_entry[2]
                if not mirror and int(log_entry[2]) < 6: 
                    print(f"Warning: {entry} missed one hit, and used the other to snipe")
                    file.write(f"3\n{entry}\ny\n1\n{enemy_clan}\n{war_end_date}\n")

    for entry in two_missed_hits: 
        if entry in skip or "Unicorn" in entry: continue
        print(f"Warning: {entry} missed two hits")
        file.write(f"3\n{entry}\ny\n1\n{enemy_clan}\n{war_end_date}\n")