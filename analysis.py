import os, re, datetime
logs = [file[:-4] for file in os.listdir("./logs/") if not "_input" in file]

immune = [ 
    "Sned",
    "BumblinMumbler",
    "Glowy Gore"
]

with open("claims-xray.txt", "r", encoding="utf-8") as file: 
    xray_claims = file.readlines()

with open("claims-outlaws.txt", "r", encoding="utf-8") as file:
    outlaws_claims = file.readlines()

with open("minion-xray.txt", "r", encoding="utf-8") as file:
    xray_data = file.readlines()

with open("minion-outlaws.txt", "r", encoding="utf-8") as file:
    outlaws_data = file.readlines()

def regular_keyboard(input_string): 
    pattern = r"^[A-Za-z0-9 \~!@#$%^&*()\-=\[\]{}|;:'\",.<>/?\\_+]*$"
    return re.match(pattern, input_string) is not None 

# 15 #P2UPPVYL    ‭⁦Sned      ⁩‬ Sned | PST
claims_pattern = re.compile(r"(\d{1,2})\s+#([A-Z0-9]{5,9})\s+‭⁦(.*)⁩‬(.*)")

# #P2UPPVYL    15 Sned
full_account_name_pattern = re.compile(r"([A-Z0-9]{5,9})\s+\d{1,2}\s+(.*)")

class Claim: 
    def __init__(self, town_hall:int, tag:str, name:str, is_main:bool, clan:str): 
        self.tag = tag
        self.town_hall = town_hall
        self.name = name
        self.is_main = is_main
        self.clan = clan

claims_dictionary = {}

for claim in xray_claims: 
    claim_th, claim_tag, claim_name, claimer = re.search(claims_pattern, claim).groups()

    claim_tag = claim_tag.strip()
    claim_name = claim_name.strip()
    claimer = claimer.strip()

    for account in xray_data: 
        account_tag, account_name = re.search(full_account_name_pattern, account).groups()

        account_tag = account_tag.strip()
        account_name = account_name.strip()

        if account_name == "JALVIN ø": account_name = "JALVIN"
        if account_name == "★ıċєʏקѧṅṭś★": account_name = "IceyPants"
        if account_name == "General⚡️Mc0⚡️": account_name = "General Mc0"
        if account_name == "༺༃༼SEV༽༃༻": account_name = "SEV"
        if account_name == "「 NightEye 」": account_name = "NightEye"
        if account_name == "Mini @ñ@$": account_name = "Mini Anas"
        if account_name == "❤️lav❤️": account_name = "lav"
        if account_name == "$õckÕ": account_name = "Socko"
        if account_name == "Stunted Nazgûl": account_name = "Stunted Nazgul"
        
        if "’" in account_name: account_name = account_name.replace("’", "'")
        if "™" in account_name: account_name = account_name.replace("™", "")
        if "✨" in account_name: account_name = account_name.replace("✨", "")
        if "\_" in account_name: account_name = account_name.replace("\_", "_")
        if "\~" in account_name: account_name = account_name.replace("\~", "~")

        if not regular_keyboard(account_name):
            print(f"Player name '{account_name}' is not valid. Please input the name manually.")
            account_name = input("Name: ")

        if account_tag == claim_tag: 
            if claimer not in claims_dictionary: claims_dictionary[claimer] = []
            claims_dictionary[claimer].append(Claim(claim_th, claim_tag, account_name, False, "Reddit X-Ray"))
            break

for claim in outlaws_claims:
    claim_th, claim_tag, claim_name, claimer = re.search(claims_pattern, claim).groups()

    claim_tag = claim_tag.strip()
    claim_name = claim_name.strip()
    claimer = claimer.strip()

    for account in outlaws_data: 
        account_tag, account_name = re.search(full_account_name_pattern, account).groups()

        account_tag = account_tag.strip()
        account_name = account_name.strip()

        if account_name == "JALVIN ø": account_name = "JALVIN"
        if account_name == "★ıċєʏקѧṅṭś★": account_name = "IceyPants"
        if account_name == "General⚡️Mc0⚡️": account_name = "General Mc0"
        if account_name == "༺༃༼SEV༽༃༻": account_name = "SEV"
        if account_name == "「 NightEye 」": account_name = "NightEye"
        if account_name == "Mini @ñ@$": account_name = "Mini Anas"
        if account_name == "❤️lav❤️": account_name = "lav"
        if account_name == "$õckÕ": account_name = "Socko"
        if account_name == "Stunted Nazgûl": account_name = "Stunted Nazgul"
        
        if "’" in account_name: account_name = account_name.replace("’", "'")
        if "™" in account_name: account_name = account_name.replace("™", "")
        if "✨" in account_name: account_name = account_name.replace("✨", "")
        if "\_" in account_name: account_name = account_name.replace("\_", "_")
        if "\~" in account_name: account_name = account_name.replace("\~", "~")

        if not regular_keyboard(account_name):
            print(f"Player name '{account_name}' is not valid. Please input the name manually.")
            account_name = input("Name: ")

        if account_tag == claim_tag: 
            if claimer not in claims_dictionary: claims_dictionary[claimer] = []
            claims_dictionary[claimer].append(Claim(claim_th, claim_tag, account_name, False, "Faint Outlaws"))
            break

known_mains = ["Glowy Gore", "Lil Ank"]

with open("claims_output.txt", "w", encoding="utf-8") as file:
    for claimer in claims_dictionary: 
        for claim in claims_dictionary[claimer]:
            accounts_xray = [claim for claim in claims_dictionary[claimer] if claim.clan == "Reddit X-Ray"]
            accounts_outlaws = [claim for claim in claims_dictionary[claimer] if claim.clan == "Faint Outlaws"]
            accounts_total = accounts_xray + accounts_outlaws

            num_accounts_xray = len(accounts_xray)
            num_accounts_outlaws = len(accounts_outlaws)
            num_accounts_total = len(accounts_total)

            if num_accounts_total == 1: 
                main_account = accounts_total[0]
                main_account.is_main = True

                claims_dictionary[claimer] = [main_account] + [claim for claim in claims_dictionary[claimer] if claim.tag != main_account.tag]

            # Otherwise, if they have one account in Reddit X-ray, set that one as main. 
            elif num_accounts_xray == 1:
                main_account = accounts_xray[0]
                main_account.is_main = True

                claims_dictionary[claimer] = [main_account] + [claim for claim in claims_dictionary[claimer] if claim.tag != main_account.tag]

            # If they have multiple accounts in Reddit X-ray, set the one with the highest town hall level as main.
            elif num_accounts_xray > 1:
                main_account = max(accounts_xray, key=lambda account: account.town_hall)
                main_account.is_main = True

                claims_dictionary[claimer] = [main_account] + [claim for claim in claims_dictionary[claimer] if claim.tag != main_account.tag]

            else: 
                for account in accounts_total:
                    if account.name in known_mains: 
                        account.is_main = True
                        break

                if len([account for account in accounts_total if account.is_main]) == 0:
                    # At this point, we have still not identified a main account. 
                    # Set the account with the highest town hall level as the main account.
                    main_account = max(accounts_total, key=lambda account: account.town_hall)
                    main_account.is_main = True

                    claims_dictionary[claimer] = [main_account] + [account for account in accounts_total if account.tag != main_account.tag]

                else: 
                    claims_dictionary[claimer] = [account for account in accounts_total if account.is_main] + [account for account in accounts_total if not account.is_main]

    for claimer in claims_dictionary: 
        accounts_xray = [claim for claim in claims_dictionary[claimer] if claim.clan == "Reddit X-Ray"]
        accounts_outlaws = [claim for claim in claims_dictionary[claimer] if claim.clan == "Faint Outlaws"]
        accounts_total = accounts_xray + accounts_outlaws

        num_accounts_xray = len(accounts_xray)
        num_accounts_outlaws = len(accounts_outlaws)
        num_accounts_total = len(accounts_total)

        file.write(f"{claimer}: {num_accounts_xray} accounts in Reddit X-Ray, {num_accounts_outlaws} accounts in Faint Outlaws\n")
        for account in accounts_total: 
            file.write(f"  - {account.name} ({account.town_hall}) -- {account.clan}")
            if account.is_main: file.write(" (main)")
            file.write("\n")

        file.write("\n")

for log_file in logs: 
    with open(f"./logs/{log_file}.txt", "r", encoding="utf-8") as file: 
        lines = file.readlines()

    hit_pattern = re.compile(r":(\d{2})::\d{2}::Sword::(\d{2})::\d{2}:(:Star:|:FadedStar:|:Blank:)(:Star:|:FadedStar:|:Blank:)(:Star:|:FadedStar:|:Blank:):\d{2,3}:[💥]? .{2}(.*).{2}")

    win_loss_pattern = re.compile(r"Win/loss: (win|loss|blacklist win|blacklist loss)")
    enemy_clan_pattern = re.compile(r"Enemy clan: (.*)")
    war_end_date_pattern = re.compile(r"War end date: (\d{4})")

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
            if player_name == "General⚡️Mc0⚡️": player_name = "General Mc0"
            if player_name == "༺༃༼SEV༽༃༻": player_name = "SEV"
            if player_name == "「 NightEye 」": player_name = "NightEye"
            if player_name == "Mini @ñ@$": player_name = "Mini Anas"
            if player_name == "❤️lav❤️": player_name = "lav"
            if player_name == "$õckÕ": player_name = "Socko"
            if player_name == "Stunted Nazgûl": player_name = "Stunted Nazgul"
            
            if "’" in player_name: player_name = player_name.replace("’", "'")
            if "™" in player_name: player_name = player_name.replace("™", "")
            if "✨" in player_name: player_name = player_name.replace("✨", "")
            if "\_" in player_name: player_name = player_name.replace("\_", "_")
            if "\~" in player_name: player_name = player_name.replace("\~", "~")

            if not regular_keyboard(player_name):
                print(f"Player name '{player_name}' is not valid. Please input the name manually.")
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

            if player_name == "JALVIN ø": player_name = "JALVIN"
            if player_name == "★ıċєʏקѧṅṭś★": player_name = "IceyPants"
            if player_name == "General⚡️Mc0⚡️": player_name = "General Mc0"
            if player_name == "༺༃༼SEV༽༃༻": player_name = "SEV"
            if player_name == "「 NightEye 」": player_name = "NightEye"
            if player_name == "Mini @ñ@$": player_name = "Mini Anas"
            if player_name == "❤️lav❤️": player_name = "lav"
            if player_name == "$õckÕ": player_name = "Socko"
            if player_name == "Stunted Nazgûl": player_name = "Stunted Nazgul"
            
            if "’" in player_name: player_name = player_name.replace("’", "'")
            if "™" in player_name: player_name = player_name.replace("™", "")
            if "✨" in player_name: player_name = player_name.replace("✨", "")
            if "\_" in player_name: player_name = player_name.replace("\_", "_")
            if "\~" in player_name: player_name = player_name.replace("\~", "~")

            if not regular_keyboard(player_name):
                print(f"Player name {player_name} is not valid. Please input the name manually.")
                player_name = input("Name: ")

            two_missed_hits.append(player_name)

        if attack_list == 1:
            player_name = line.strip()[8:]

            if player_name == "JALVIN ø": player_name = "JALVIN"
            if player_name == "★ıċєʏקѧṅṭś★": player_name = "IceyPants"
            if player_name == "General⚡️Mc0⚡️": player_name = "General Mc0"
            if player_name == "༺༃༼SEV༽༃༻": player_name = "SEV"
            if player_name == "「 NightEye 」": player_name = "NightEye"
            if player_name == "Mini @ñ@$": player_name = "Mini Anas"
            if player_name == "❤️lav❤️": player_name = "lav"
            if player_name == "$õckÕ": player_name = "Socko"
            if player_name == "Stunted Nazgûl": player_name = "Stunted Nazgul"
            
            if "’" in player_name: player_name = player_name.replace("’", "'")
            if "™" in player_name: player_name = player_name.replace("™", "")
            if "✨" in player_name: player_name = player_name.replace("✨", "")
            if "\_" in player_name: player_name = player_name.replace("\_", "_")
            if "\~" in player_name: player_name = player_name.replace("\~", "~")

            if not regular_keyboard(player_name):
                print(f"Player name {player_name} is not valid. Please input the name manually.")
                player_name = input("Name: ")

            one_missed_hit.append(player_name)

    with open(f"./inputs/{log_file}.txt", "w", encoding="utf-8") as file: 
        if win_loss == "win" or win_loss == "loss": 
            # FWA war
            for entry in log: 
                player_name, attacker, defender, stars, time_remaining = entry
                # print(f"Player: {player_name}, Attacker: {attacker}, Defender: {defender}, Stars: {stars}, Time Remaining: {time_remaining:.2f}")
                if player_name in immune or "Unicorn" in player_name: 
                    continue

                is_main = True
                for claimer in claims_dictionary: 
                    for account in claims_dictionary[claimer]: 
                        if account.name == player_name: 
                            if not account.is_main: 
                                is_main = False
                                
                if not is_main: continue

                # Check if an account with the same name exists in the claims dictionary.
                # If not, they probably left the clan. 
                account_found = False
                for claimer in claims_dictionary:
                    for account in claims_dictionary[claimer]: 
                        if account.name == player_name: 
                            account_found = True
                            break
                    if account_found: break

                # if not account_found:
                #     print(f"Bypass: {player_name} appears to have left")
                #     continue

                if int(defender) > 5: 
                    # Check if this hit was not a mirror 
                    mirror = attacker == defender
                    if not mirror: 
                        # First, check if this looks to be a snipe. 
                        # Snipes are defined as 1 star on a loss, or 1-2 stars on a win. 
                        if win_loss == "loss" and stars < 2: 
                            print(f"Bypass: #{attacker} {player_name} hit someone not their own mirror, but this appears to be a snipe")
                        
                        elif win_loss == "win" and stars < 3:
                            print(f"Bypass: #{attacker} {player_name} hit someone not their own mirror, but this appears to be a snipe")
                        
                        # Next, check if they already hit their mirror, but the defender's number is not in the invalid_mirror list.
                        # This can occur if they hit their mirror second; and thus we should not penalize.
                        elif attacker in [entry[2] for entry in log if entry[1] == attacker]: 
                            print(f"Bypass: #{attacker} {player_name} hit someone not their own mirror, but they already hit their mirror")
                            
                        # If not, first check if the defender's number is in the invalid_mirror list. 
                        # This means that their own mirror was already taken, and thus we should not penalize. 
                        elif attacker in invalid_mirror:
                            print(f"Bypass: #{attacker} {player_name} hit someone not their own mirror, but their mirror was already taken")

                        # If the defender's number is not in the invalid_mirror list, then we should add it.
                        # This means that their own mirror was not taken, and thus we should penalize.
                        else:
                            # First, we should check if there are less than four hours remaining in the war.
                            if time_remaining < 4: 
                                print(f"Bypass: #{attacker} {player_name} hit someone not their own mirror, but there are less than four hours remaining")

                            else: 
                                invalid_mirror.append(defender)
                                print(f"Warning: #{attacker} {player_name} hit someone not their own mirror")
                                file.write(f"3\n{player_name}\ny\n7\n4\n{enemy_clan}\n")
                    else: 
                        # Add this base to the invalid_mirror list, since it was taken by a mirror.
                        if not defender in invalid_mirror: invalid_mirror.append(defender)

                if win_loss == "loss": 
                    mirror = attacker == defender 
                    if mirror and stars > 2: 
                        print(f"Warning: #{attacker} {player_name} three-starred on a loss")
                        file.write(f"3\n{player_name}\ny\n7\n1\n{enemy_clan}\n")
                    elif not mirror and not int(attacker) < 6 and int(defender) < 6 and stars > 1: 
                        if defender in invalid_mirror: 
                            print(f"Bypass: #{attacker} {player_name} sniped for more than one star on a loss, but this base was already hit")
                        else: 
                            print(f"Warning: #{attacker} {player_name} sniped for more than one star on a loss")
                            file.write(f"3\n{player_name}\ny\n7\n3\n{enemy_clan}\n")
                            invalid_mirror.append(defender)

                if win_loss == "win": 
                    mirror = attacker == defender 
                    if not mirror and not int(attacker) < 6 and int(defender) < 6 and stars > 2: 
                        if defender in invalid_mirror: 
                            print(f"Bypass: #{attacker} {player_name} sniped for more than two stars on a win, but this base was already hit")
                        else:
                            print(f"Warning: #{attacker} {player_name} sniped for more than two stars on a win")
                            file.write(f"3\n{player_name}\ny\n7\n2\n{enemy_clan}\n")
                            invalid_mirror.append(defender)

            for entry in one_missed_hit: 
                # Check if an account with the same name exists in the claims dictionary.
                # If not, they probably left the clan. 
                account_found = False
                for claimer in claims_dictionary:
                    for account in claims_dictionary[claimer]: 
                        if account.name == entry: 
                            account_found = True
                            break
                    if account_found: break

                # if not account_found:
                #     print(f"Bypass: {entry} appears to have left")
                #     continue

                # First, check if there are TWO entries in the log with the same name.
                # If so, Minion Bot made an error; ignore this entry. 
                if len([log_entry for log_entry in log if log_entry[0] == entry]) > 1: 
                    print(f"Bypass: #{attacker} {entry} missed one hit, but Minion Bot made an error")
                    continue

                # Find the corresponding entry in the log; find their other hit 
                if entry in immune or "Unicorn" in entry: 
                    print(f"Bypass: {entry} missed one hit, but they are immune")
                    continue

                is_main = True
                for claimer in claims_dictionary:
                    for account in claims_dictionary[claimer]: 
                        if account.name == entry: 
                            if not account.is_main: 
                                is_main = False

                if not is_main: 
                    print(f"Bypass: {entry} missed one hit, but they are not a main account")
                    continue

                for log_entry in log: 
                    if log_entry[0] == entry: 
                        mirror = log_entry[1] == log_entry[2]
                        if not mirror and int(log_entry[2]) < 6: 
                            print(f"Warning: #{log_entry[1]} {entry} missed one hit, and used the other to snipe")
                            file.write(f"3\n{entry}\ny\n1\n{enemy_clan}\n{war_end_date}\n")

            for entry in two_missed_hits: 
                # Check if an account with the same name exists in the claims dictionary.
                # If not, they probably left the clan. 
                account_found = False
                for claimer in claims_dictionary:
                    for account in claims_dictionary[claimer]: 
                        if account.name == entry: 
                            account_found = True
                            break
                    if account_found: break

                # if not account_found:
                #     print(f"Bypass: {entry} appears to have left")
                #     continue

                if entry in immune or "Unicorn" in entry: 
                    print(f"Bypass: {entry} missed two hits, but they are immune")
                    continue

                is_main = True
                for claimer in claims_dictionary:
                    for account in claims_dictionary[claimer]: 
                        if account.name == entry: 
                            if not account.is_main: 
                                is_main = False
                if not is_main: 
                    print(f"Bypass: {entry} missed two hits, but they are not a main account")
                    continue

                print(f"Warning: {entry} missed two hits")
                file.write(f"3\n{entry}\ny\n1\n{enemy_clan}\n{war_end_date}\n")

        elif win_loss == "blacklist win" or win_loss == "blacklist loss":
            victory = "y" if win_loss.split(" ")[1] == "win" else "n"
            for entry in one_missed_hit: 
                if entry in immune or "Unicorn" in entry: 
                    print(f"Bypass: {entry} missed one hit on a blacklist war, but they are immune")
                    continue

                # Check if an account with the same name exists in the claims dictionary.
                # If not, they probably left the clan. 
                account_found = False
                for claimer in claims_dictionary:
                    for account in claims_dictionary[claimer]: 
                        if account.name == entry: 
                            account_found = True
                            break
                    if account_found: break

                # if not account_found:
                #     print(f"Bypass: {entry} appears to have left")
                #     continue

                is_main = True
                for claimer in claims_dictionary:
                    for account in claims_dictionary[claimer]: 
                        if account.name == entry: 
                            if not account.is_main: 
                                is_main = False
                if not is_main: 
                    print(f"Bypass: {entry} missed one hit on a blacklist war, but they are not a main account")
                    continue

                if victory == "y": 
                    print(f"Bypass: {entry} missed one hit on a blacklist war, but we won anyway")
                else: 
                    print(f"Warning: {entry} missed one hit on a blacklist war")
                    file.write(f"3\n{entry}\ny\n3\n{enemy_clan}\nn\n1\n")

            for entry in two_missed_hits: 
                if entry in immune or "Unicorn" in entry: 
                    print(f"Bypass: {entry} missed two hits on a blacklist war, but they are immune")
                    continue

                # Check if an account with the same name exists in the claims dictionary.
                # If not, they probably left the clan. 
                account_found = False
                for claimer in claims_dictionary:
                    for account in claims_dictionary[claimer]: 
                        if account.name == entry: 
                            account_found = True
                            break
                    if account_found: break

                # if not account_found:
                #     print(f"Bypass: {entry} appears to have left")
                #     continue

                is_main = True
                for claimer in claims_dictionary:
                    for account in claims_dictionary[claimer]: 
                        if account.name == entry: 
                            if not account.is_main: 
                                is_main = False
                if not is_main: 
                    print(f"Bypass: {entry} missed two hits on a blacklist war, but they are not a main account")
                    continue

                if victory == "y": 
                    print(f"Warning: {entry} missed two hits on a blacklist war, but we still won")
                    file.write(f"3\n{entry}\ny\n3\n{enemy_clan}\ny\n2\n")
                else:
                    print(f"Warning: {entry} missed two hits on a blacklist war, which cost us the win")
                    file.write(f"3\n{entry}\ny\n3\n{enemy_clan}\nn\n2\n")

    # press any key to continue 
    input("Press any key to continue...")