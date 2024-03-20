import os, re, datetime, argparse, subprocess

from contextlib import redirect_stdout as redirect
from io import StringIO

def up_to_date(): 
    # Return FALSE if there is a new version available.
    # Return TRUE if the version is up to date.
    try:
        # Fetch the latest changes from the remote repository without merging or pulling
        # Redirect output, because we don't want to see it.
        with redirect(StringIO()):
            subprocess.check_output("git fetch", shell=True)

        # Compare the local HEAD with the remote HEAD
        local_head = subprocess.check_output("git rev-parse HEAD", shell=True).decode().strip()
        remote_head = subprocess.check_output("git rev-parse @{u}", shell=True).decode().strip()

        return local_head == remote_head

    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        return None

if up_to_date() is False:
    print("Error: the local repository is not up to date. Please pull the latest changes before running this script.")
    print("To pull the latest changes, simply run the command 'git pull' in this terminal.")
    exit(1)

logs = [file[:-4] for file in os.listdir("./logs/") if not "_input" in file]

parser = argparse.ArgumentParser(description="Analyze war logs for generating strikes.")
parser.add_argument("--bypass", "-b", action="store_true", help="If set to true, program also outputs bypass messages. Default: False")
parser.add_argument("--log", "-l", action="store_true", help="If set to true, program also outputs log messages. Default: False")
parser.add_argument("--mirrors", "-m", action="store_true", help="If set to true, program also outputs invalid mirror messages. Default: False")

args = parser.parse_args()

# Permanent immunities are players who are members of Leadership; they cannot be kicked. 
permanent_immunities = [ 
    "Sned",
    "BumblinMumbler",
    "Glowy Gore", 
    "Anas", 
    "Arcohol",
    "Bran6"
]

# Timed immunities involve players who will be out until a given date
timed_immunities = [

]

# War-specific immunities are for one war only. 
one_war_immunities = [
    ("Zaheer", "03/13/2024"),
    ("Nobody", "03/13/2024"),
    ("Arietem", "03/13/2024"),
    ("Monkey D. Luffy", "03/15/2024"),
    ("Monkey D. Luffy", "03/17/2024"), 
    ("Shomeer", "03/19/2024"),
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
    pattern = r"^[A-Za-z0-9 \~!@#$%^&*()\-=\[\]{}|;:'\",\.<>/?\\_+]*$"
    return re.match(pattern, input_string) is not None 

with open("war_bases.txt", "r", encoding="utf-8") as war_bases_file: 
    war_bases = war_bases_file.readlines()
    with open(f"./inputs/war_bases.txt", "w", encoding="utf-8") as file:
        for i in range(len(war_bases)): 
            player_name, enemy_clan, sanction = war_bases[i].strip().split(";")
            file.write(f"3\n{player_name}\ny\n5\n{enemy_clan}\n{sanction}\n")
            print(f"Warning: {player_name} had war base during battle day against {enemy_clan}", end = "")
            if sanction == "y": print(", and sanctions occurred from it.")
            else: print(".")

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

corrected_names = {
    "JALVIN ø": "JALVIN",
    "★ıċєʏקѧṅṭś★": "IceyPants",
    "General⚡️Mc0⚡️": "General Mc0",
    "༺༃༼SEV༽༃༻": "SEV",
    "「 NightEye 」": "NightEye",
    "Mini @ñ@$": "Mini Anas",
    "❤️lav❤️": "lav",
    "$õckÕ": "Socko",
    "Stunted Nazgûl": "Stunted Nazgul",
    "ᴍᴏɴᴋᴇʏ ᴅ. ʟᴜꜰꜰʏ": "Monkey D. Luffy"
}

for claim in xray_claims: 
    claim_th, claim_tag, claim_name, claimer = re.search(claims_pattern, claim).groups()

    claim_tag = claim_tag.strip()
    claim_name = claim_name.strip()
    claimer = claimer.strip()

    for account in xray_data: 
        account_tag, account_name = re.search(full_account_name_pattern, account).groups()

        account_tag = account_tag.strip()
        account_name = account_name.strip()

        if account_name in corrected_names.keys(): account_name = corrected_names[account_name]
        
        if "’" in account_name: account_name = account_name.replace("’", "'")
        if "™" in account_name: account_name = account_name.replace("™", "")
        if "✨" in account_name: account_name = account_name.replace("✨", "")
        if "\_" in account_name: account_name = account_name.replace("\_", "_")
        if "\~" in account_name: account_name = account_name.replace("\~", "~")

        if not regular_keyboard(account_name):
            print(f"X-ray: Player name '{account_name}' is not valid. Please input the name manually.")
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

        if account_name in corrected_names.keys(): account_name = corrected_names[account_name]
        
        if "’" in account_name: account_name = account_name.replace("’", "'")
        if "™" in account_name: account_name = account_name.replace("™", "")
        if "✨" in account_name: account_name = account_name.replace("✨", "")
        if "\_" in account_name: account_name = account_name.replace("\_", "_")
        if "\~" in account_name: account_name = account_name.replace("\~", "~")

        if not regular_keyboard(account_name):
            print(f"Outlaws: Player name '{account_name}' is not valid. Please input the name manually.")
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

    try: 
        win_loss = re.search(win_loss_pattern, lines[0]).group(1)
        enemy_clan = re.search(enemy_clan_pattern, lines[1]).group(1)
        war_end_date = re.search(war_end_date_pattern, lines[2]).group(1)

    except: 
        print(f"Error: {log_file} is not formatted correctly. Please check the log file and try again.")
        print(f"Usage: {log_file} should have the following format: ")
        print("Win/loss: (win|loss|blacklist win|blacklist loss)")
        print("Enemy clan: (clan name)")
        print("War end date: (mmdd)")
        continue

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

            if player_name in corrected_names.keys(): player_name = corrected_names[player_name]
            
            if "’" in player_name: player_name = player_name.replace("’", "'")
            if "™" in player_name: player_name = player_name.replace("™", "")
            if "✨" in player_name: player_name = player_name.replace("✨", "")
            if "\_" in player_name: player_name = player_name.replace("\_", "_")
            if "\~" in player_name: player_name = player_name.replace("\~", "~")

            if not regular_keyboard(player_name):
                print(f"Logging: Player name '{player_name}' is not valid. Please input the name manually.")
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

            if player_name in corrected_names.keys(): player_name = corrected_names[player_name]
            
            if "’" in player_name: player_name = player_name.replace("’", "'")
            if "™" in player_name: player_name = player_name.replace("™", "")
            if "✨" in player_name: player_name = player_name.replace("✨", "")
            if "\_" in player_name: player_name = player_name.replace("\_", "_")
            if "\~" in player_name: player_name = player_name.replace("\~", "~")

            if not regular_keyboard(player_name):
                print(f"Two hits: Player name {player_name} is not valid. Please input the name manually.")
                player_name = input("Name: ")

            two_missed_hits.append(player_name)

        if attack_list == 1:
            player_name = line.strip()[8:]

            if player_name in corrected_names.keys(): player_name = corrected_names[player_name]
            
            if "’" in player_name: player_name = player_name.replace("’", "'")
            if "™" in player_name: player_name = player_name.replace("™", "")
            if "✨" in player_name: player_name = player_name.replace("✨", "")
            if "\_" in player_name: player_name = player_name.replace("\_", "_")
            if "\~" in player_name: player_name = player_name.replace("\~", "~")

            if not regular_keyboard(player_name):
                print(f"One hit: Player name {player_name} is not valid. Please input the name manually.")
                player_name = input("Name: ")

            one_missed_hit.append(player_name)

    with open(f"./inputs/{log_file}.txt", "w", encoding="utf-8") as file: 
        if win_loss == "win" or win_loss == "loss": 
            # FWA war
            for entry in log: 
                player_name, attacker, defender, stars, time_remaining = entry
                if args.log: print(f"Player: {player_name}, Attacker: {attacker}, Defender: {defender}, Stars: {stars}, Time Remaining: {time_remaining:.2f}")
                if args.mirrors: print(f"Invalid Mirrors: {invalid_mirror}")

                player_immune = False

                if player_name in permanent_immunities or "Unicorn" in player_name: 
                    player_immune = True

                for immune, date in timed_immunities:
                    if player_name == immune:
                        if datetime.datetime.strptime(date, "%m/%d/%Y") >= datetime.datetime.strptime(war_end_date, "%m%d").replace(year = datetime.datetime.now().year): 
                            player_immune = True

                for immune, date in one_war_immunities: 
                    if player_name == immune: 
                        immunity_date = datetime.datetime.strptime(date, "%m/%d/%Y")
                        war_end = datetime.datetime.strptime(war_end_date, "%m%d").replace(year = datetime.datetime.now().year)
                        if war_end == immunity_date: 
                            player_immune = True
                    
                is_main = True
                for claimer in claims_dictionary: 
                    for account in claims_dictionary[claimer]: 
                        if account.name == player_name: 
                            if not account.is_main: 
                                is_main = False
                                
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
                #     if args.bypass: print(f"Bypass: {player_name} appears to have left")
                #     continue

                # Check if this hit was not a mirror 
                mirror = attacker == defender
                if not mirror: 
                    # First, check if this looks to be a snipe. 
                    # Snipes are defined as 1 star on a loss, or 1-2 stars on a win. 
                    if win_loss == "loss" and stars < 2 and int(defender) < 5: 
                        if args.bypass: 
                            print(f"Bypass: #{attacker} {player_name} hit someone not their own mirror #{defender}, but this appears to be a snipe")
                    
                    elif win_loss == "win" and stars < 3 and int(defender) < 5:
                        if args.bypass: 
                            print(f"Bypass: #{attacker} {player_name} hit someone not their own mirror #{defender}, but this appears to be a snipe")
                    
                    # Next, check if they already hit their mirror, but the defender's number is not in the invalid_mirror list.
                    # This can occur if they hit their mirror second; and thus we should not penalize.
                    elif attacker in [entry[2] for entry in log if entry[1] == attacker]: 
                        # We should check if they hit for the right number of stars. 
                        if win_loss == "loss" and stars > 2:
                            # Check if they're immune. 
                            if player_immune:
                                if args.bypass: print(f"Bypass: {player_name} three-starred their mirror on a loss, but they are immune")
                                invalid_mirror.append(defender)

                            elif not is_main: 
                                if args.bypass: print(f"Bypass: {player_name} three-starred their mirror on a loss, but they are not a main account")
                                invalid_mirror.append(defender)

                            else:
                                print(f"Warning: #{attacker} {player_name} three-starred #{defender} on a loss")
                                file.write(f"3\n{player_name}\ny\n7\n1\n{enemy_clan}\n")
                                invalid_mirror.append(defender)

                        elif int(defender) > 5: 
                            if args.bypass: print(f"Bypass: #{attacker} {player_name} hit someone not their own mirror #{defender}, but they already hit their mirror")
                            invalid_mirror.append(defender)
                        
                    # If not, first check if the defender's number is in the invalid_mirror list. 
                    # This means that their own mirror was already taken, and thus we should not penalize. 
                    elif attacker in invalid_mirror:
                        if args.bypass: print(f"Bypass: #{attacker} {player_name} hit someone not their own mirror #{defender}, but their mirror was already taken")
                        invalid_mirror.append(defender)

                    # If the defender's number is not in the invalid_mirror list, then we should add it.
                    # This means that their own mirror was not taken, and thus we should penalize.
                    else:
                        # First, we should check if there are less than four hours remaining in the war.
                        if time_remaining < 4: 
                            if args.bypass: print(f"Bypass: #{attacker} {player_name} hit someone not their own mirror #{defender}, but there are less than four hours remaining")
                            invalid_mirror.append(defender)

                        # Then, we should check if this base is a snipe. 
                        elif win_loss == "loss" and not int(attacker) < 5 and int(defender) < 5:
                            continue

                        elif win_loss == "win" and not int(attacker) < 5 and int(defender) < 5:
                            continue

                        elif player_immune: 
                            if args.bypass: print(f"Bypass: {player_name} hit someone not their own mirror #{defender}, but they are immune")
                            invalid_mirror.append(defender)

                        elif not is_main:
                            if args.bypass: print(f"Bypass: {player_name} hit someone not their own mirror #{defender}, but they are not a main account")
                            invalid_mirror.append(defender)

                        else: 
                            invalid_mirror.append(defender)
                            print(f"Warning: #{attacker} {player_name} hit someone not their own mirror #{defender}")
                            file.write(f"3\n{player_name}\ny\n7\n4\n{enemy_clan}\n")
                else: 
                    # Add this base to the invalid_mirror list, since it was taken by a mirror.
                    invalid_mirror.append(defender)

                if win_loss == "loss": 
                    mirror = attacker == defender 
                    if mirror and stars > 2: 
                        if player_immune: 
                            if args.bypass: print(f"Bypass: {player_name} three-starred #{defender} on a loss, but they are immune")
                            invalid_mirror.append(defender)

                        elif not is_main:
                            if args.bypass: print(f"Bypass: {player_name} three-starred #{defender} on a loss, but they are not a main account")
                            invalid_mirror.append(defender)

                        else:
                            print(f"Warning: #{attacker} {player_name} three-starred #{defender} on a loss")
                            file.write(f"3\n{player_name}\ny\n7\n1\n{enemy_clan}\n")
                            invalid_mirror.append(defender)

                    elif not mirror and not int(attacker) < 6 and int(defender) < 6 and stars > 1: 
                        if defender in invalid_mirror: 
                            if args.bypass: print(f"Bypass: #{attacker} {player_name} sniped #{defender} for {stars} stars on a loss, but this base was already hit")
                            
                        elif player_immune:
                            if args.bypass: print(f"Bypass: {player_name} sniped #{defender} for {stars} stars on a loss, but they are immune")
                            invalid_mirror.append(defender)

                        elif not is_main:
                            if args.bypass: print(f"Bypass: {player_name} sniped #{defender} for {stars} stars on a loss, but they are not a main account")
                            invalid_mirror.append(defender)

                        else: 
                            print(f"Warning: #{attacker} {player_name} sniped #{defender} for {stars} stars on a loss")
                            file.write(f"3\n{player_name}\ny\n7\n3\n{enemy_clan}\n")
                            invalid_mirror.append(defender)

                if win_loss == "win": 
                    mirror = attacker == defender 
                    if not mirror and not int(attacker) < 6 and int(defender) < 6 and stars > 2: 
                        if defender in invalid_mirror: 
                            if args.bypass: print(f"Bypass: #{attacker} {player_name} sniped #{defender} for {stars} stars on a win, but this base was already hit")

                        else:
                            print(f"Warning: #{attacker} {player_name} sniped #{defender} for {stars} stars on a win")
                            file.write(f"3\n{player_name}\ny\n7\n2\n{enemy_clan}\n")
                            invalid_mirror.append(defender)

                # Remove duplicates from the invalid_mirror list
                invalid_mirror = list(set(invalid_mirror))

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
                #     if args.bypass: print(f"Bypass: {entry} appears to have left")
                #     continue

                # First, check if there are TWO entries in the log with the same name.
                # If so, Minion Bot made an error; ignore this entry. 
                if len([log_entry for log_entry in log if log_entry[0] == entry]) > 1: 
                    if args.bypass: print(f"Bypass: #{attacker} {entry} missed one hit, but Minion Bot made an error")
                    continue

                # Find the corresponding entry in the log; find their other hit 
                if entry in permanent_immunities or "Unicorn" in entry: 
                    if args.bypass: print(f"Bypass: {entry} missed one hit, but they are immune")
                    continue

                for immune, date in timed_immunities:
                    if player_name == immune:
                        if datetime.datetime.strptime(date, "%m/%d/%Y") >= datetime.datetime.strptime(war_end_date, "%m%d").replace(year = datetime.datetime.now().year): 
                            if args.bypass: print(f"Bypass: {player_name} is immune until {date}") 
                            player_immune = True

                for immune, date in one_war_immunities: 
                    if player_name == immune: 
                        immunity_date = datetime.datetime.strptime(date, "%m/%d/%Y")
                        war_end = datetime.datetime.strptime(war_end_date, "%m%d").replace(year = datetime.datetime.now().year)
                        if war_end == immunity_date: 
                            if args.bypass: print(f"Bypass: {player_name} has a one-war immunity.") 
                            player_immune = True

                is_main = True
                for claimer in claims_dictionary:
                    for account in claims_dictionary[claimer]: 
                        if account.name == entry: 
                            if not account.is_main: 
                                is_main = False

                if not is_main: 
                    if args.bypass: print(f"Bypass: {entry} missed one hit, but they are not a main account")
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
                #     if args.bypass: print(f"Bypass: {entry} appears to have left")
                #     continue

                if entry in permanent_immunities or "Unicorn" in entry: 
                    if args.bypass: print(f"Bypass: {entry} missed two hits, but they are immune")
                    continue

                for immune, date in timed_immunities:
                    if player_name == immune:
                        if datetime.datetime.strptime(date, "%m/%d/%Y") >= datetime.datetime.strptime(war_end_date, "%m%d").replace(year = datetime.datetime.now().year): 
                            if args.bypass: print(f"Bypass: {player_name} is immune until {date}") 
                            player_immune = True

                for immune, date in one_war_immunities: 
                    if player_name == immune: 
                        immunity_date = datetime.datetime.strptime(date, "%m/%d/%Y")
                        war_end = datetime.datetime.strptime(war_end_date, "%m%d").replace(year = datetime.datetime.now().year)
                        if war_end == immunity_date: 
                            if args.bypass: print(f"Bypass: {player_name} has a one-war immunity.") 
                            player_immune = True

                is_main = True
                for claimer in claims_dictionary:
                    for account in claims_dictionary[claimer]: 
                        if account.name == entry: 
                            if not account.is_main: 
                                is_main = False
                if not is_main: 
                    if args.bypass: print(f"Bypass: {entry} missed two hits, but they are not a main account")
                    continue

                print(f"Warning: {entry} missed two hits")
                file.write(f"3\n{entry}\ny\n1\n{enemy_clan}\n{war_end_date}\n")

        elif win_loss == "blacklist win" or win_loss == "blacklist loss":
            victory = "y" if win_loss.split(" ")[1] == "win" else "n"
            for entry in one_missed_hit: 
                if entry in permanent_immunities or "Unicorn" in entry: 
                    if args.bypass: print(f"Bypass: {entry} missed one hit on a blacklist war, but they are immune")
                    continue

                for immune, date in timed_immunities:
                    if player_name == immune:
                        if datetime.datetime.strptime(date, "%m/%d/%Y") >= datetime.datetime.strptime(war_end_date, "%m%d").replace(year = datetime.datetime.now().year): 
                            if args.bypass: print(f"Bypass: {player_name} is immune until {date}") 
                            player_immune = True

                for immune, date in one_war_immunities: 
                    if player_name == immune: 
                        immunity_date = datetime.datetime.strptime(date, "%m/%d/%Y")
                        war_end = datetime.datetime.strptime(war_end_date, "%m%d").replace(year = datetime.datetime.now().year)
                        if war_end == immunity_date: 
                            if args.bypass: print(f"Bypass: {player_name} has a one-war immunity.") 
                            player_immune = True

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
                #     if args.bypass: print(f"Bypass: {entry} appears to have left")
                #     continue

                is_main = True
                for claimer in claims_dictionary:
                    for account in claims_dictionary[claimer]: 
                        if account.name == entry: 
                            if not account.is_main: 
                                is_main = False
                if not is_main: 
                    if args.bypass: print(f"Bypass: {entry} missed one hit on a blacklist war, but they are not a main account")
                    continue

                if victory == "y": 
                    if args.bypass: print(f"Bypass: {entry} missed one hit on a blacklist war, but we won anyway")
                else: 
                    print(f"Warning: {entry} missed one hit on a blacklist war")
                    file.write(f"3\n{entry}\ny\n3\n{enemy_clan}\nn\n1\n")

            for entry in two_missed_hits: 
                if entry in permanent_immunities or "Unicorn" in entry: 
                    if args.bypass: print(f"Bypass: {entry} missed two hits on a blacklist war, but they are immune")
                    continue

                for immune, date in timed_immunities:
                    if player_name == immune:
                        if datetime.datetime.strptime(date, "%m/%d/%Y") >= datetime.datetime.strptime(war_end_date, "%m%d").replace(year = datetime.datetime.now().year): 
                            if args.bypass: print(f"Bypass: {player_name} is immune until {date}") 
                            player_immune = True

                for immune, date in one_war_immunities: 
                    if player_name == immune: 
                        immunity_date = datetime.datetime.strptime(date, "%m/%d/%Y")
                        war_end = datetime.datetime.strptime(war_end_date, "%m%d").replace(year = datetime.datetime.now().year)
                        if war_end == immunity_date: 
                            if args.bypass: print(f"Bypass: {player_name} has a one-war immunity.") 
                            player_immune = True

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
                #     if args.bypass: print(f"Bypass: {entry} appears to have left")
                #     continue

                is_main = True
                for claimer in claims_dictionary:
                    for account in claims_dictionary[claimer]: 
                        if account.name == entry: 
                            if not account.is_main: 
                                is_main = False
                if not is_main: 
                    if args.bypass: print(f"Bypass: {entry} missed two hits on a blacklist war, but they are not a main account")
                    continue

                if victory == "y": 
                    print(f"Warning: {entry} missed two hits on a blacklist war, but we still won")
                    file.write(f"3\n{entry}\ny\n3\n{enemy_clan}\ny\n2\n")
                else:
                    print(f"Warning: {entry} missed two hits on a blacklist war, which cost us the win")
                    file.write(f"3\n{entry}\ny\n3\n{enemy_clan}\nn\n2\n")

    # press any key to continue 
    input("Press any key to continue...\n")