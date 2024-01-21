with open("raw.txt", "r", encoding="utf-8") as file: 
    lines = file.readlines()

import re, datetime
hit_pattern = re.compile(r":(\d{2})::\d{2}::Sword::(\d{2})::\d{2}:(:Star:|:FadedStar:|:Blank:)(:Star:|:FadedStar:|:Blank:)(:Star:|:FadedStar:|:Blank:):\d{2,3}:[💥]? .{2}(.*).{2}")

def regular_keyboard(input_string): 
    pattern = r"^[A-Za-z0-9 !@#$%^&*()\-=\[\]{}|;:'\",.<>/?\\_+]*$"
    return re.match(pattern, input_string) is not None 

win_loss_pattern = re.compile(r"Win/loss: (win|loss)")
enemy_clan_pattern = re.compile(r"Enemy clan: (.*)")
war_end_date_pattern = re.compile(r"War end date: (\d{4})")

# 01/16/2024 12:03 PM
time_pattern = re.compile(r"(\d{2}/\d{2}/\d{4}) (\d{1,2}:\d{2}) ([AP]M)")

win_loss = re.search(win_loss_pattern, lines[0]).group(1)
enemy_clan = re.search(enemy_clan_pattern, lines[1]).group(1)
war_end_date = re.search(war_end_date_pattern, lines[2]).group(1)

war_start_date = re.search(time_pattern, lines[6]).group(1)
war_start_time = re.search(time_pattern, lines[6]).group(2)
war_start_ampm = re.search(time_pattern, lines[6]).group(3)
war_start_datetime_str = f"{war_start_date} {war_start_time} {war_start_ampm}"
war_start = datetime.datetime.strptime(war_start_datetime_str, "%m/%d/%Y %I:%M %p") + datetime.timedelta(minutes=59)

print(f"War start: {war_start}")

attack_list = None

time_elapsed = 0

log = []
two_missed_hits = []
one_missed_hit = []

invalid_mirror = []

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

war_start_announcement = True
 
for line in lines:
    # Check for timestamp using pattern
    match = time_pattern.search(line)
    if match: 
        if war_start_announcement: 
            war_start_announcement = False
            continue

        timestamp_date = match.group(1)
        timestamp_time = match.group(2)
        timestamp_ampm = match.group(3)
        timestamp_str = f"{timestamp_date} {timestamp_time} {timestamp_ampm}"

        timestamp = datetime.datetime.strptime(timestamp_str, "%m/%d/%Y %I:%M %p")

        time_remaining = 24 - (timestamp - war_start).total_seconds() / 3600

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
        
        log.append((player_name, attacker, defender, stars, time_remaining))

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
        player_name, attacker, defender, stars, time_remaining = entry
        print(f"Player: {player_name}, Attacker: {attacker}, Defender: {defender}, Stars: {stars}, Time Remaining: {time_remaining:.2f}")
        if player_name in skip or "Unicorn" in player_name: continue
        if int(defender) > 5: 
            # Check if this hit was not a mirror 
            mirror = attacker == defender
            if not mirror: 
                # First, check if this looks to be a snipe. 
                # Snipes are defined as 1 star on a loss, or 1-2 stars on a win. 
                if win_loss == "loss" and stars < 1: 
                    print(f"Bypass: {player_name} hit someone not their own mirror, but this appears to be a snipe")
                
                elif win_loss == "win" and stars < 3:
                    print(f"Bypass: {player_name} hit someone not their own mirror, but this appears to be a snipe")
                
                # If not, first check if the defender's number is in the invalid_mirror list. 
                # This means that their own mirror was already taken, and thus we should not penalize. 
                elif attacker in invalid_mirror:
                    print(f"Bypass: {player_name} hit someone not their own mirror, but their mirror was already taken")
                    
                # If the defender's number is not in the invalid_mirror list, then we should add it.
                # This means that their own mirror was not taken, and thus we should penalize.
                else:
                    # First, we should check if there are less than four hours remaining in the war.
                    if time_remaining < 4: 
                        print(f"Bypass: {player_name} hit someone not their own mirror, but there are less than four hours remaining")

                    else: 
                        invalid_mirror.append(defender)
                        print(f"Warning: {player_name} hit someone not their own mirror")
                        file.write(f"3\n{player_name}\ny\n7\n4\n{enemy_clan}\n")
            else: 
                # Add this base to the invalid_mirror list, since it was taken by a mirror.
                invalid_mirror.append(defender)

        if win_loss == "loss": 
            mirror = attacker == defender 
            if mirror and stars > 2: 
                print(f"Warning: {player_name} three-starred on a loss")
                file.write(f"3\n{player_name}\ny\n7\n1\n{enemy_clan}\n")
            elif not mirror and not int(attacker) < 6 and int(defender) < 6 and stars > 1: 
                print(f"Warning: {player_name} sniped for more than one star on a loss")
                file.write(f"3\n{player_name}\ny\n7\n3\n{enemy_clan}\n")
        if win_loss == "win": 
            mirror = attacker == defender 
            if not mirror and not int(attacker) < 6 and int(defender) < 6 and stars > 2: 
                print(f"Warning: {player_name} sniped for more than two stars on a win")
                file.write(f"3\n{player_name}\ny\n7\n2\n{enemy_clan}\n")

    for entry in one_missed_hit: 
        # First, check if there are TWO entries in the log with the same name.
        # If so, Minion Bot made an error; ignore this entry. 
        if len([log_entry for log_entry in log if log_entry[0] == entry]) > 1: 
            print(f"Bypass: {entry} missed one hit, but Minion Bot made an error")
            continue

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