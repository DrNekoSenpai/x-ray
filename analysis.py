import os, re, datetime, argparse, subprocess, pickle
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

if not os.path.exists("./logs/"): os.mkdir("./logs/")
if not os.path.exists("./inputs/"): os.mkdir("./inputs/")

logs = [file[:-4] for file in os.listdir("./logs/") if not "_input" in file]

parser = argparse.ArgumentParser(description="Analyze war logs for generating strikes.")
parser.add_argument("--bypass", "-b", action="store_true", help="If set to true, program also outputs bypass messages. Default: False")
parser.add_argument("--snipe", "-s", action="store_true", help="If set to true, program outputs snipe messages when bypass is also true. Default: False")
parser.add_argument("--debug", "-d", action="store_true", help="If set to true, program outputs log messages for immune players. Default: False")
parser.add_argument("--log", "-l", action="store_true", help="If set to true, program also outputs log messages. Default: False")
parser.add_argument("--mirrors", "-m", action="store_true", help="If set to true, program also outputs invalid mirror messages. Default: False")
parser.add_argument("--war", "-w", type=str, default="", help="If specified, only analyze the war log with the given name. Default: ''")
parser.add_argument("--update", "-u", action="store_true", help="If set to true, only update player activity logs and exit without analyzing wars. Default: False")
args = parser.parse_args()

# Permanent immunities are players who are members of Leadership as well as known alts; they cannot be kicked. 
permanent_immunities = [ 
    "Sned",
    "Sned 2.0",
    "Sned 3.0",
    "Sned 4.0",
    "BumblinMumbler",
    "BumblinMumbler2",
    "BumblinMumbler3",
    "katsu", 
    "K.L.A.U.S v2",
    "Ascended", 
    "Smitty™", 
    "Ligma", 
    "Sugma", 
    "CrazyWaveIT", 
    "LOGAN911", 
    "skyeshade", 
    "Golden Unicorn✨"
]

# Timed immunities involve players who will be immune until a given date
timed_immunities = [
    
]

# War-specific immunities are for one war only. 
one_war_immunities = [
    ("Im Rushed", "2025-01-24")
]

with open("xray-claims.txt", "r", encoding="utf-8") as file: 
    xray_claims = file.readlines()

with open("xray-minion.txt", "r", encoding="utf-8") as file:
    xray_data = file.readlines()

class Dump:
    def __init__(self, user_id, nickname, username): 
        self.user_id = user_id
        self.nickname = nickname
        self.username = username

# /stats dump role: @Reddit X-ray query: -f %i;%n;%u
with open("dump.txt", "r", encoding="utf-8") as file:
    dump_data = [Dump(user_id, nickname, username) for user_id, nickname, username in [line.split(";") for line in file.readlines()]]

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

    claim_th = int(claim_th)
    claim_tag = claim_tag.strip()
    claim_name = claim_name.strip()
    claimer = claimer.strip()

    # Check if the claimer follows a format of <@321138998414409729>
    # In this case, we need to replace this with the actual username as specified in the Dump.
     
    if re.match(r"<@.*>", claimer): 
        user_id = claimer[2:-1]
        for user in dump_data: 
            if user.user_id == user_id: 
                claimer = user.nickname
                break

    if "\\" in claim_name: claim_name = claim_name.replace("\\", "")

    # Remove @ from claimer name 
    if "@" in claimer: claimer = claimer.replace("@", "")
    if "\\" in claimer: claimer = claimer.replace("\\", "")

    for account in xray_data: 
        account_tag, account_name = re.search(full_account_name_pattern, account).groups()

        account_tag = account_tag.strip()
        account_name = account_name.strip()
        
        if "’" in account_name: account_name = account_name.replace("’", "'")
        if "\\" in account_name: account_name = account_name.replace("\\", "")

        if account_tag == claim_tag: 
            if claimer not in claims_dictionary: claims_dictionary[claimer] = []
            claims_dictionary[claimer].append(Claim(claim_th, claim_tag, account_name, False, "Reddit X-ray"))
            break

known_mains = ["Marlec", "Plantos"]

num_alts_xray = 0

for claimer in claims_dictionary: 
    for claim in claims_dictionary[claimer]:
        accounts_xray = [claim for claim in claims_dictionary[claimer] if claim.clan == "Reddit X-ray"]
        num_accounts_xray = len(accounts_xray)

        known_main = False
        if num_accounts_xray > 1:
            for account in accounts_xray:
                if account.name in known_mains: 
                    account.is_main = True
                    known_main = True
                    break

        if known_main:
            claims_dictionary[claimer] = [account for account in accounts_xray if account.is_main] + [account for account in accounts_xray if not account.is_main]

        elif num_accounts_xray == 1: 
            main_account = accounts_xray[0]
            main_account.is_main = True

            claims_dictionary[claimer] = [main_account] + [claim for claim in claims_dictionary[claimer] if claim.tag != main_account.tag]

        else: 
            for account in accounts_xray:
                if account.name in known_mains: 
                    account.is_main = True
                    break

            if len([account for account in accounts_xray if account.is_main]) == 0:
                # At this point, we have still not identified a main account. 
                # Set the account with the highest town hall level as the main account.
                main_account = max(accounts_xray, key=lambda account: account.town_hall)
                main_account.is_main = True

                claims_dictionary[claimer] = [main_account] + [account for account in accounts_xray if account.tag != main_account.tag]

            else: 
                claims_dictionary[claimer] = [account for account in accounts_xray if account.is_main] + [account for account in accounts_xray if not account.is_main]

for claimer in claims_dictionary:
    for claim in claims_dictionary[claimer]: 
        if not claim.is_main and claim.clan == "Reddit X-ray": num_alts_xray += 1

# Sort the claims dictionary, first by the town hall of the main account descending, then by the number of known alts ascending.
claims_dictionary = {claimer: claims_dictionary[claimer] for claimer in sorted(claims_dictionary, key=lambda claimer: (max([account.town_hall for account in claims_dictionary[claimer] if account.is_main]), len([account for account in claims_dictionary[claimer] if not account.is_main])), reverse=True)}

with open("num_alts.txt", "w", encoding="utf-8") as file:
    unix_time = int(datetime.datetime.now().timestamp())
    file.write(f"As of <t:{unix_time}:F> (<t:{unix_time}:R>):\n\n")
    file.write(f"Number of alts in Reddit X-ray: {num_alts_xray}\n")
    for claimer in claims_dictionary: 
        for claim in claims_dictionary[claimer]: 
            if not claim.is_main and claim.clan == "Reddit X-ray": 
                main = [account for account in claims_dictionary[claimer] if account.is_main][0]
                alt_name = claim.name.replace('_', '\_')
                main_name = main.name.replace('_', '\_')

                file.write(f"  \- {alt_name} ({claim.town_hall}) -- main: {main_name}\n")

with open("claims_output.txt", "w", encoding="utf-8") as file:
    for claimer in claims_dictionary: 
        accounts_xray = [claim for claim in claims_dictionary[claimer] if claim.clan == "Reddit X-ray"]
        num_accounts_xray = len(accounts_xray)

        if num_accounts_xray == 1: file.write(f"{claimer}: {num_accounts_xray} account in Reddit X-ray")
        else: file.write(f"{claimer}: {num_accounts_xray} accounts in Reddit X-ray")

        file.write("\n")
        
        for account in accounts_xray: 
            file.write(f"  - {account.name} ({account.town_hall})")
            if account.is_main: file.write(" -- (main)")
            file.write("\n")

        file.write("\n")

class player_activity: 
    # We need; player name, player tag, total number of hits missed, and an array of which wars were missed.
    # We also need a value that says the last time this player was found in our roster. 
    def __init__(self, name:str, tag:str): 
        self.name = name
        self.tag = tag
        self.base_value = 0
        self.wars_missed = []
        # Set last seen to 14 days before today, so that we can catch any players who haven't been seen in a while.
        self.last_seen = f"{datetime.datetime.now() - datetime.timedelta(days=14):%Y-%m-%d}"
        self.banked_counter = []
        self.wars_logged = [] # Same as banked counter, but is not wiped when the reset hits. 

try: 
    with open("player_activity.pickle", "rb") as file: 
        player_activity_dict = pickle.load(file)

except:
    # Assume no such file exists, create a new one. 
    print(f"Error: no such file 'player_activity.pickle' was found. Creating a new one.")
    player_activity_dict = {}

for claim in xray_data: 
    account_tag, account_name = re.search(full_account_name_pattern, claim).groups()

    account_tag = account_tag.strip()
    account_name = account_name.strip()

    if "’" in account_name: account_name = account_name.replace("’", "'")
    if "\\" in account_name: account_name = account_name.replace("\\", "")

    if account_tag not in player_activity_dict: 
        player_activity_dict[account_tag] = player_activity(account_name, account_tag)
        print(f"Player {account_name} #{account_tag} added to player_activity_dict.")

# Set ALL player base values to zero. 
for player in player_activity_dict:
    player_activity_dict[player].base_value = 0

with open("strikes.txt", "r", encoding="utf-8") as strikes_file: 
    strikes = strikes_file.readlines()

    # Capture number of strikes, player name, player tag
    # [1] Baleus #GYV8Q0U80:

    strikes_pattern = re.compile(r"\[(\d+)\]\s+(.*)\s+#([A-Z0-9]{5,9})")
    # Find the corresponding player in the player_activity_dict, and set the base value to the number of strikes.

    for strike in strikes:
        # Not every line is going to match this pattern. Skip those that don't. 
        if not re.match(strikes_pattern, strike): continue
        num_strikes, player_name, player_tag = re.search(strikes_pattern, strike).groups()

        if player_tag in player_activity_dict: 
            player_activity_dict[player_tag].base_value = int(num_strikes)
            print(f"Player {player_name} #{player_tag} has {num_strikes} strikes.")
        else: 
            print(f"Error: player {player_name} #{player_tag} not found in player_activity_dict.")

with open("war_bases.txt", "r", encoding="utf-8") as war_bases_file: 
    war_bases = war_bases_file.readlines()
    with open(f"./inputs/war_bases.txt", "w", encoding="utf-8") as file:
        for ind,val in enumerate(war_bases):
            if ind == 0: continue # Header row
            # Split the line using semicolon, and remove spaces
            player_name, enemy_clan, war_type, conditional, war_end_date = [x.strip() for x in val.split(";")]

            player_immune = False

            if player_name in permanent_immunities or "Unicorn" in player_name: 
                player_immune = True

            for immune, date in timed_immunities:
                if player_name == immune:
                    if datetime.datetime.strptime(date, "%Y-%m-%d") >= datetime.datetime.strptime(war_end_date, "%Y-%m-%d").replace(year = datetime.datetime.now().year): 
                        player_immune = True

            for immune, date in one_war_immunities: 
                if player_name == immune: 
                    immunity_date = datetime.datetime.strptime(date, "%Y-%m-%d")
                    war_end = datetime.datetime.strptime(war_end_date, "%Y-%m-%d").replace(year = datetime.datetime.now().year)
                    if war_end == immunity_date: 
                        player_immune = True
                
            is_main = True
            for claimer in claims_dictionary: 
                for account in claims_dictionary[claimer]: 
                    if account.name == player_name: 
                        if not account.is_main: 
                            is_main = False

            if player_immune or not is_main: 
                print(f"Bypass: {player_name} is immune or not a main account")
                continue

            if war_type == "blacklist" and conditional == "true": 
                file.write(f"3\n{player_name}\ny\n2\n{war_end_date}\n{enemy_clan}\ny\n")
                print(f"Warning: {player_name} failed to put up a war base during a blacklist war against {enemy_clan}, but we met the conditional.")

            elif war_type == "blacklist" and conditional == "false":
                file.write(f"3\n{player_name}\ny\n2\n{war_end_date}\n{enemy_clan}\nn\n")
                print(f"Warning: {player_name} failed to put up a war base during a blacklist war against {enemy_clan}")

            elif war_type == "FWA" and conditional == "true":
                file.write(f"3\n{player_name}\ny\n2\n{war_end_date}\n{enemy_clan}\ny\n")
                print(f"Warning: {player_name} failed to put up a war base during an FWA war against {enemy_clan}, and sanctions occurred from it.")

            elif war_type == "FWA" and conditional == "false":
                file.write(f"3\n{player_name}\ny\n2\n{war_end_date}\n{enemy_clan}\nn\n")
                print(f"Warning: {player_name} failed to put up a war base during an FWA war against {enemy_clan}")

if args.update: 
    with open("player_activity.pickle", "wb") as file: 
        pickle.dump(player_activity_dict, file)
    exit()

for log_file in logs: 
    if args.war and log_file != args.war: continue
    if log_file == "arch": continue # This is a folder
    if log_file == "sanct": continue # This is a folder

    with open(f"./logs/{log_file}.txt", "r", encoding="utf-8") as file: 
        lines = file.readlines()

    hit_pattern = re.compile(r":(\d{2})::\d{2}::Sword::(\d{2})::\d{2}:(:Star:|:FadedStar:|:Blank:)(:Star:|:FadedStar:|:Blank:)(:Star:|:FadedStar:|:Blank:):\d{2,3}:[💥]? .{2}(.*).{2}")

    win_loss_pattern = re.compile(r"Win/loss: (win|loss|blacklist win|blacklist loss)")
    conditional_pattern = re.compile(r"Blacklist conditional: (true|false)")
    war_end_date_pattern = re.compile(r"War end date: (\d{4}-\d{2}-\d{2})")

    time_pattern = re.compile(r"(\d{4}-\d{2}-\d{2}) (\d{1,2}:\d{2}) ([AP]M)")
    enemy_clan_pattern = re.compile(r"War with #[A-Z0-9]{5,9} ‭⁦(.*)⁩‬ starts in \d+ minutes.")

    try: 
        win_loss = re.search(win_loss_pattern, lines[0]).group(1)
        war_end_date = re.search(war_end_date_pattern, lines[1]).group(1)

        if "blacklist" in win_loss: conditional = re.search(conditional_pattern, lines[2]).group(1)
        else: conditional = None # Not applicable

    except: 
        print(f"Error: {log_file} is not formatted correctly. Please check the log file and try again.")
        print(f"Usage: {log_file} should have the following format: ")
        print("Win/loss: (win|loss|blacklist win|blacklist loss)")
        print("War end date: (yyyy-mm-dd)")
        print("Blacklist conditional: (true|false) -- only if the war is a blacklist war")
        continue

    if conditional is None: 
        war_start_date = re.search(time_pattern, lines[5]).group(1)
        war_start_time = re.search(time_pattern, lines[5]).group(2)
        war_start_ampm = re.search(time_pattern, lines[5]).group(3)
        war_start_datetime_str = f"{war_start_date} {war_start_time} {war_start_ampm}"
        war_start = datetime.datetime.strptime(war_start_datetime_str, "%Y-%m-%d %I:%M %p") + datetime.timedelta(minutes=59)

        print(f"War start: {war_start}")
        enemy_clan = re.search(enemy_clan_pattern, lines[6]).group(1)

    else: 
        war_start_date = re.search(time_pattern, lines[6]).group(1)
        war_start_time = re.search(time_pattern, lines[6]).group(2)
        war_start_ampm = re.search(time_pattern, lines[6]).group(3)
        war_start_datetime_str = f"{war_start_date} {war_start_time} {war_start_ampm}"
        war_start = datetime.datetime.strptime(war_start_datetime_str, "%Y-%m-%d %I:%M %p") + datetime.timedelta(minutes=59)

        print(f"War start: {war_start}")
        enemy_clan = re.search(enemy_clan_pattern, lines[7]).group(1)

    if enemy_clan: 
        print(f"Enemy clan: {enemy_clan}")
    else:
        print("Error: enemy clan not found")
        exit()

    attack_list = None

    time_elapsed = 0

    log = []

    invalid_mirror = []

    one_missed_hit = []
    two_missed_hits = []

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

            timestamp = datetime.datetime.strptime(timestamp_str, "%Y-%m-%d %I:%M %p")

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
            
            if "’" in player_name: player_name = player_name.replace("’", "'")
            if "\_" in player_name: player_name = player_name.replace("\_", "_")
            if "\~" in player_name: player_name = player_name.replace("\~", "~")
            
            log.append((player_name, attacker, defender, stars, time_remaining))

        if "2 Missed Attacks" in line.strip(): 
            attack_list = 2
            continue
        
        if "1 Missed Attack" in line.strip():
            attack_list = 1
            continue

        if attack_list == 2: 
            number, player_name = line[1:].strip().split(" ", 1)
            number = int(number.replace(":", ""))
            
            if "’" in player_name: player_name = player_name.replace("’", "'")
            if "\_" in player_name: player_name = player_name.replace("\_", "_")
            if "\~" in player_name: player_name = player_name.replace("\~", "~")

            log.append((player_name, number, None, None, None))
            log.append((player_name, number, None, None, None))
            two_missed_hits.append(player_name)

        if attack_list == 1:
            number, player_name = line[1:].strip().split(" ", 1)
            number = int(number.replace(":", ""))

            if "’" in player_name: player_name = player_name.replace("’", "'")
            if "\_" in player_name: player_name = player_name.replace("\_", "_")
            if "\~" in player_name: player_name = player_name.replace("\~", "~")

            log.append((player_name, number, None, None, None))
            one_missed_hit.append(player_name)

    with open(f"./inputs/{log_file}.txt", "w", encoding="utf-8") as file: 
        if win_loss == "win" or win_loss == "loss": 
            snipe_count = {}
            rules_broken = {player_name: False for player_name in [entry[0] for entry in log]}

            # FWA war
            for entry in log: 
                player_name, attacker, defender, stars, time_remaining = entry

                if defender is None: # Missed hit, skip for now 
                    continue

                if args.log: print(f"Player: {player_name}, Attacker: {attacker}, Defender: {defender}, Stars: {stars}, Time Remaining: {time_remaining:.2f}")
                if args.mirrors: print(f"Invalid Mirrors: {invalid_mirror}")

                player_immune = False

                if player_name in permanent_immunities: 
                    player_immune = True

                for immune, date in timed_immunities:
                    if player_name == immune:
                        if datetime.datetime.strptime(date, "%Y-%m-%d") >= datetime.datetime.strptime(war_end_date, "%Y-%m-%d").replace(year = datetime.datetime.now().year): 
                            player_immune = True

                for immune, date in one_war_immunities: 
                    if player_name == immune: 
                        immunity_date = datetime.datetime.strptime(date, "%Y-%m-%d")
                        war_end = datetime.datetime.strptime(war_end_date, "%Y-%m-%d").replace(year = datetime.datetime.now().year)
                        if war_end == immunity_date: 
                            player_immune = True
                    
                is_main = True
                for claimer in claims_dictionary: 
                    for account in claims_dictionary[claimer]: 
                        if account.name == player_name: 
                            if not account.is_main: 
                                is_main = False

                if player_immune and not args.debug: 
                    invalid_mirror.append(defender)
                    continue 
                if not is_main and not args.debug: 
                    invalid_mirror.append(defender)
                    continue

                mirror = attacker == defender
                if mirror: 
                    # Check if the player three-starred their mirror on a loss.
                    if win_loss == "loss" and stars > 2:
                        print(f"Warning: {player_name} three-starred their mirror on a loss.")
                        file.write(f"3\n{player_name}\ny\n5\n{war_end_date}\n1\n{enemy_clan}\n")
                        rules_broken[player_name] = True

                    # Add this base to the invalid_mirror list, since it was taken by a mirror.
                    invalid_mirror.append(defender)

                    continue

                # If this is NOT a mirror, we do still need to check if they three-starred during a loss. 
                elif win_loss == "loss" and stars == 3: 
                    # Check if this player already hit their mirror. 
                    # If so, only penalize them for three-starring during a loss. 
                    # If not, check if they hit another base because their mirror was already taken. 
                    # If not, check if they hit another base because less than four hours remain in the war.
                    # If none of these are true, additionally penalize them for hitting a base not their mirror.

                    if (player_immune or not is_main) and args.debug: 
                        if attacker in [entry[2] for entry in log if entry[1] == attacker]:
                            print(f"Debug: {player_name} three-starred a base not their mirror #{defender} on a loss, but they already hit their mirror")

                        elif attacker in invalid_mirror:
                            print(f"Debug: {player_name} three-starred a base not their mirror #{defender} on a loss, but their mirror was already taken")

                        elif time_remaining < 6:
                            print(f"Debug: {player_name} three-starred a base not their mirror #{defender} on a loss, but there are {round(time_remaining, 2)} hours remaining")

                        else: 
                            print(f"Debug: {player_name} three-starred on a loss")
                            print(f"Debug: {player_name} hit a base not their own mirror #{defender}")

                    else: 
                        if attacker in [entry[2] for entry in log if entry[1] == attacker]:
                            print(f"Warning: {player_name} three-starred a base not their mirror #{defender} on a loss, but they already hit their mirror")
                            file.write(f"3\n{player_name}\ny\n5\n{war_end_date}\n1\n{enemy_clan}\n")
                            rules_broken[player_name] = True

                        elif attacker in invalid_mirror:
                            print(f"Warning: {player_name} three-starred a base not their mirror #{defender} on a loss, but their mirror was already taken")
                            file.write(f"3\n{player_name}\ny\n5\n{war_end_date}\n1\n{enemy_clan}\n")
                            rules_broken[player_name] = True

                        elif time_remaining < 6: 
                            print(f"Warning: {player_name} three-starred a base not their mirror #{defender} on a loss, but there are {round(time_remaining, 2)} hours remaining")
                            file.write(f"3\n{player_name}\ny\n5\n{war_end_date}\n1\n{enemy_clan}\n")
                            rules_broken[player_name] = True

                        else: 
                            print(f"Warning: {player_name} three-starred on a loss")
                            file.write(f"3\n{player_name}\ny\n5\n{war_end_date}\n1\n{enemy_clan}\n")
                            print(f"Warning: {player_name} hit a base not their own mirror #{defender}")
                            file.write(f"3\n{player_name}\ny\n5\n{war_end_date}\n2\n{enemy_clan}\n")
                            rules_broken[player_name] = True
                    
                # First, check if this looks to be a snipe. 

                if win_loss == "loss" and stars < 2 and int(defender) <= 5 and int(attacker) > 5: 
                    if args.bypass and args.snipe: 
                        print(f"Bypass: #{attacker} {player_name} hit someone not their own mirror #{defender}, but this appears to be a snipe")

                    if player_name in snipe_count: 
                        snipe_count[player_name] += 1
                    else:
                        snipe_count[player_name] = 1

                    # Check if they have sniped twice.
                    if snipe_count[player_name] >= 2:
                        if (player_immune or not is_main) and args.debug: 
                            print(f"Debug: {player_name} appears to have sniped twice.")
                            
                        else: 
                            print(f"Warning: {player_name} appears to have sniped twice.")
                            file.write(f"3\n{player_name}\ny\n5\n{war_end_date}\n3\n{enemy_clan}\n")
                            rules_broken[player_name] = True

                    continue

                elif win_loss == "win" and stars < 3 and int(defender) <= 5 and int(attacker) > 5:
                    if args.bypass and args.snipe: 
                        print(f"Bypass: #{attacker} {player_name} hit someone not their own mirror #{defender}, but this appears to be a snipe")

                    if player_name in snipe_count: 
                        snipe_count[player_name] += 1
                    else:
                        snipe_count[player_name] = 1

                    if snipe_count[player_name] >= 2:
                        if (player_immune or not is_main) and args.debug: 
                            print(f"Debug: {player_name} appears to have sniped twice.")

                        else:
                            print(f"Warning: {player_name} appears to have sniped twice.")
                            file.write(f"3\n{player_name}\ny\n5\n{war_end_date}\n3\n{enemy_clan}\n")
                            rules_broken[player_name] = True

                    continue

                # Check their other hit to see if they hit their mirror. 
                elif attacker in [entry[2] for entry in log if entry[1] == attacker]:
                    if int(defender) <= 5:
                        if args.bypass and args.snipe: print(f"Bypass: #{attacker} {player_name} hit someone not their own mirror #{defender}, but this appears to be a snipe")
                        invalid_mirror.append(defender)

                    else: 
                        # In this case, they hit their mirror as well as another base that's not their mirror nor a snipe. 
                        # Check if they did this when there's less than four hours remaining in the war.

                        if time_remaining < 6:
                            if args.bypass: print(f"Bypass: {player_name} hit their mirror #{defender} as well as another base not their mirror #{attacker}, but there are {round(time_remaining, 2)} hours remaining")

                        else:  
                            if (player_immune or not is_main) and args.debug: 
                                print(f"Debug: {player_name} hit their mirror #{defender} as well as another base not their mirror #{attacker}, with time remaining {round(time_remaining, 2)} hours")

                            else:
                                print(f"Warning: {player_name} hit their mirror #{defender} as well as another base not their mirror #{attacker}, with time remaining {round(time_remaining, 2)} hours")
                                file.write(f"3\n{player_name}\ny\n5\n{war_end_date}\n2\n{enemy_clan}\n")
                                rules_broken[player_name] = True

                        invalid_mirror.append(defender)

                else: 
                    # Debug; print the player's name, attacker, defender, stars, and time remaining.
                    # print(f"Unhandled case: {player_name}, Attacker: {attacker}, Defender: {defender}, Stars: {stars}, Time Remaining: {time_remaining:.2f}")

                    # Check if the defender's number is already in invalid_mirror. 
                    # If so, that means someone else took their mirror first, and therefore this is allowed. 
                    if attacker in invalid_mirror:
                        mirror_entry = [entry for entry in log if entry[2] == attacker][0]
                        if args.bypass: print(f"Bypass: {player_name} hit someone not their own mirror #{defender}, but their mirror was already taken by #{mirror_entry[1]} {mirror_entry[0]}")
                        continue

                    # Check if the defender's number is less than or equal to 5.
                    # If so, this still counts as a snipe, and we should not penalize.
                    if int(defender) <= 5:
                        if args.bypass and args.snipe: print(f"Bypass: {player_name} hit someone not their own mirror #{defender}, but this appears to be a snipe")
                        continue

                    # Check if there are less than four hours remaining in the war.
                    if time_remaining < 6:
                        if args.bypass: print(f"Bypass: {player_name} hit someone not their own mirror #{defender}, but there are {round(time_remaining, 2)} hours remaining")
                        invalid_mirror.append(defender)

                    else:
                        if (player_immune or not is_main) and args.debug: 
                            print(f"Debug: {player_name} hit someone not their own mirror #{defender}")

                        else:
                            print(f"Warning: {player_name} hit someone not their own mirror #{defender}")
                            file.write(f"3\n{player_name}\ny\n5\n{war_end_date}\n2\n{enemy_clan}\n")
                            rules_broken[player_name] = True

                        invalid_mirror.append(defender)

            for entry in one_missed_hit: 
                for log_entry in log:
                    if log_entry[0] == entry and log_entry[2] is None: continue

                    if log_entry[0] == entry: 
                        mirror = log_entry[1] == log_entry[2]
                        if not mirror and int(log_entry[2]) < 6: 
                            if args.bypass: print(f"Bypass: #{log_entry[1]} {entry} missed one hit, and used the other to snipe")
                            continue

                        print(f"Warning: {entry} missed one hit, and used the other to snipe")
                        
                        # Find the player in the player_activity_dict. If they don't exist, throw an error and exit. 
                        # However, player_activity_dict is a dictionary categorized by player tag, not player name.
                        # We need to find the player tag of the player name in the log.

                        player_exists = False 
                        for player_tag in player_activity_dict:
                            if player_activity_dict[player_tag].name == entry: 
                                player_exists = True
                                break

                        if not player_exists:
                            # If the player doesn't exist, assume they were removed from the roster.
                            print(f"Error: {entry} not found in player_activity_dict. Continuing.") 
                            continue
                        
                        # Format: Date of war end, enemy clan, win/loss
                        war_data = (war_end_date, enemy_clan, win_loss)

                        # Check if we already added this war. If so, ignore it.
                        if not war_data in player_activity_dict[player_tag].wars_missed:
                            player_activity_dict[player_tag].wars_missed.append(war_data)

                        rules_broken[entry] = True

            for entry in two_missed_hits:
                for log_entry in log:
                    if log_entry[0] == entry:
                        player_exists = False
                        for player_tag in player_activity_dict:
                            if player_activity_dict[player_tag].name == entry: 
                                player_exists = True
                                break

                        if not player_exists:
                            print(f"Error: {entry} not found in player_activity_dict. Continuing.")
                            continue

                        war_data = (war_end_date, enemy_clan, win_loss)
                        print(f"Warning: {entry} missed two hits")

                        if not war_data in player_activity_dict[player_tag].wars_missed:
                            player_activity_dict[player_tag].wars_missed.append(war_data)

                        rules_broken[entry] = True

        elif win_loss == "blacklist win" or win_loss == "blacklist loss":
            victory = "y" if win_loss.split(" ")[1] == "win" else "n"
            one_missed_hit = []
            two_missed_hits = []

            rules_broken = {player_name: False for player_name in [entry[0] for entry in log]}

            for entry in log: 
                player_name, attacker, defender, stars, time_remaining = entry
                # If there is ONE instance of a given player in the log with None as defender, they missed one hit. 
                # If there are TWO instances of a given player in the log with None as defender, they missed two hits.

                if defender is None:
                    if player_name in one_missed_hit: 
                        two_missed_hits.append(player_name)
                        one_missed_hit.remove(player_name)
                    else: 
                        one_missed_hit.append(player_name)
            
            for entry in one_missed_hit: 
                if entry in permanent_immunities or "Unicorn" in entry: 
                    if args.bypass: print(f"Bypass: {entry} missed one hit on a blacklist war, but they are immune")
                    continue

                for immune, date in timed_immunities:
                    if player_name == immune:
                        if datetime.datetime.strptime(date, "%Y-%m-%d") >= datetime.datetime.strptime(war_end_date, "%Y-%m-%d").replace(year = datetime.datetime.now().year): 
                            if args.bypass: print(f"Bypass: {player_name} is immune until {date}") 
                            player_immune = True

                for immune, date in one_war_immunities: 
                    if player_name == immune: 
                        immunity_date = datetime.datetime.strptime(date, "%Y-%m-%d")
                        war_end = datetime.datetime.strptime(war_end_date, "%Y-%m-%d").replace(year = datetime.datetime.now().year)
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
                    if args.bypass: print(f"Bypass: {entry} missed one hit on a blacklist war, but they are not a main account")
                    continue

                if victory == "y": 
                    if args.bypass: print(f"Bypass: {entry} missed one hit on a blacklist war, but we won anyway")
                else: 
                    if conditional == "true": 
                        print(f"Warning: {entry} missed one hit on a blacklist war, which cost us the win but we met the conditional")
                        file.write(f"3\n{entry}\ny\n1\n{war_end_date}\n{enemy_clan}\ny\nn\n1\n")
                        rules_broken[entry] = True
                    else: 
                        print(f"Warning: {entry} missed one hit on a blacklist war, which cost us the win")
                        file.write(f"3\n{entry}\ny\n1\n{war_end_date}\n{enemy_clan}\nn\nn\n1\n")
                        rules_broken[entry] = True

            for entry in two_missed_hits: 
                if entry in permanent_immunities or "Unicorn" in entry: 
                    if args.bypass: print(f"Bypass: {entry} missed two hits on a blacklist war, but they are immune")
                    continue

                for immune, date in timed_immunities:
                    if player_name == immune:
                        if datetime.datetime.strptime(date, "%Y-%m-%d") >= datetime.datetime.strptime(war_end_date, "%Y-%m-%d").replace(year = datetime.datetime.now().year): 
                            if args.bypass: print(f"Bypass: {player_name} is immune until {date}") 
                            player_immune = True

                for immune, date in one_war_immunities: 
                    if player_name == immune: 
                        immunity_date = datetime.datetime.strptime(date, "%Y-%m-%d")
                        war_end = datetime.datetime.strptime(war_end_date, "%Y-%m-%d").replace(year = datetime.datetime.now().year)
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
                    if args.bypass: print(f"Bypass: {entry} missed two hits on a blacklist war, but they are not a main account")
                    continue

                if victory == "y": 
                    if conditional == "true": 
                        print(f"Warning: {entry} missed two hits on a blacklist war, but we still won and met the conditional")
                        file.write(f"3\n{entry}\ny\n1\n{war_end_date}\n{enemy_clan}\ny\ny\n2\n")
                        rules_broken[entry] = True
                    else:
                        print(f"Warning: {entry} missed two hits on a blacklist war, but we still won")
                        file.write(f"3\n{entry}\ny\n1\n{war_end_date}\n{enemy_clan}\nn\ny\n2\n")
                        rules_broken[entry] = True
                else:
                    if conditional == "true": 
                        print(f"Warning: {entry} missed two hits on a blacklist war, which cost us the win but we met the conditional")
                        file.write(f"3\n{entry}\ny\n1\n{war_end_date}\n{enemy_clan}\ny\nn\n2\n")
                        rules_broken[entry] = True
                    else:
                        print(f"Warning: {entry} missed two hits on a blacklist war, which cost us the win")
                        file.write(f"3\n{entry}\ny\n1\n{war_end_date}\n{enemy_clan}\nn\nn\n2\n")
                        rules_broken[entry] = True

        # Update each player's last seen date to the date of this war, if it is before this date. 
        for player in player_activity_dict:
            # First, we do need to check if this player was seen this war; if they were in the clan. 
            if player_activity_dict[player].name in [entry[0] for entry in log]:
                # Update date with format yyyy-mm-dd
                player_activity_dict[player].last_seen = f"{datetime.datetime.strptime(war_end_date, '%Y-%m-%d').strftime('%Y-%m-%d')}"

        # If player didn't break rules this war, check if they have any wars missed. If so, remove the oldest one. 
        for player in rules_broken: 
            if not rules_broken[player]: 
                # Find the corresponding player in the player_activity_dict. however, as it's categorized by player tag, we will need to do a search. 
                for player_tag in player_activity_dict:
                    if player_activity_dict[player_tag].name == player: 
                        # First, check the banked counter. If it's not three, add one. 
                        # If it is, remove a war if possible. If not, do nothing; we can't go into negative. 

                        if len(player_activity_dict[player_tag].banked_counter) < 3: 
                            # Check if this player already has this war banked. 
                            if not war_end_date in player_activity_dict[player_tag].wars_logged: 
                                player_activity_dict[player_tag].banked_counter.append(war_end_date)
                                player_activity_dict[player_tag].wars_logged.append(war_end_date)

                        if len(player_activity_dict[player_tag].banked_counter) >= 3:
                            # Check if they have any wars missed. If not, skip. 
                            if len(player_activity_dict[player_tag].wars_missed) == 0: 
                                continue 

                            print(f"Bank: {player} did not break any rules this war, and has inactivity value of {len(player_activity_dict[player_tag].wars_missed)}. Removing oldest war missed.")
                            player_activity_dict[player_tag].wars_missed.pop(0)
                            player_activity_dict[player_tag].banked_counter = []

    # press any key to continue 
    input("Press any key to continue...\n")

# Check for players who have not been seen in one month. That is, 30 days. 
to_be_deleted = []
for player in player_activity_dict:
    last_seen = datetime.datetime.strptime(player_activity_dict[player].last_seen, "%Y-%m-%d")
    if (datetime.datetime.now() - last_seen).days >= 30: 
        print(f"Warning: {player_activity_dict[player].name} has not been seen in a month. Removing from player activity.")
        to_be_deleted.append(player)

for player in to_be_deleted:
    del player_activity_dict[player]

with open("player_activity.pickle", "wb") as file:
    pickle.dump(player_activity_dict, file)

# Sort the player_activity_dict by the number of wars missed. 
player_activity_dict = {player: player_activity_dict[player] for player in sorted(player_activity_dict, key=lambda player: len(player_activity_dict[player].wars_missed) + player_activity_dict[player].base_value, reverse=True)}

# For each player in the player activity dict, sort their wars missed by date descending. 
for player in player_activity_dict:
    player_activity_dict[player].wars_missed = sorted(player_activity_dict[player].wars_missed, key=lambda war: datetime.datetime.strptime(war[0], "%Y-%m-%d"), reverse=True)

# Manual backup dump. 
with open("player_activity.txt", "w", encoding="utf-8") as file:
    # Format: player name, player tag
    for player in player_activity_dict:
        file.write(f"{player_activity_dict[player].name}: #{player_activity_dict[player].tag}\n")
        file.write(f"  - Wars missed: {len(player_activity_dict[player].wars_missed)}\n")
        for war in player_activity_dict[player].wars_missed: 
            file.write(f"    - {war}\n")
        file.write(f"  - Last seen in clan: {player_activity_dict[player].last_seen}\n")
        file.write(f"  - Banked counter: {player_activity_dict[player].banked_counter}\n")
        file.write(f"  - Wars logged: {player_activity_dict[player].wars_logged}\n\n")

# Dump to be posted in a Discord channel.
with open("activity_output.txt", "w", encoding="utf-8") as file:
    file.write(f"As of <t:{unix_time}:F> (<t:{unix_time}:R>):\n\n")
    for player in player_activity_dict: 
        # First, print out all the players that are in the clan; that is, are in xray-data. 
        player_found = False 
        for item in xray_data:
            if player_activity_dict[player].name in item: 
                player_found = True
                break

        if player_found: 
            wars_missed = len(player_activity_dict[player].wars_missed)

            if wars_missed == 0: continue
            if player_activity_dict[player].name in permanent_immunities: continue

            if player_activity_dict[player].base_value != 0: 
                file.write(f"{player_activity_dict[player].name}: {player_activity_dict[player].base_value + wars_missed} ({player_activity_dict[player].base_value} strikes, {wars_missed} wars missed)\n")

            else: 
                if wars_missed == 1: file.write(f"{player_activity_dict[player].name}: 1 war missed\n")
                else: file.write(f"{player_activity_dict[player].name}: {wars_missed} wars missed\n")

    file.write("\n")
    for player in player_activity_dict: 
        # Next, print out all the players that are not in the clan; that is, are not in xray-data. 
        player_found = False 
        for item in xray_data:
            if player_activity_dict[player].name in item: 
                player_found = True
                break

        if not player_found: 
            wars_missed = len(player_activity_dict[player].wars_missed)
            # Skip this player if they have not missed any wars.

            if wars_missed == 0: continue

            if wars_missed == 1: file.write(f"{player_activity_dict[player].name}: 1 war missed\n")
            else: file.write(f"{player_activity_dict[player].name}: {wars_missed} wars missed\n")

            file.write(f"  \- Last seen in clan: {player_activity_dict[player].last_seen}\n\n")