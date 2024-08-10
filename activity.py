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

if not os.path.exists("./logs/"): os.mkdir("./logs/")
if not os.path.exists("./inputs/"): os.mkdir("./inputs/")

logs = [file[:-4] for file in os.listdir("./logs/") if not "_input" in file]

parser = argparse.ArgumentParser(description="Analyze war logs for generating strikes.")
parser.add_argument("--bypass", "-b", action="store_true", help="If set to true, program also outputs bypass messages. Default: False")
parser.add_argument("--log", "-l", action="store_true", help="If set to true, program also outputs log messages. Default: False")
parser.add_argument("--mirrors", "-m", action="store_true", help="If set to true, program also outputs invalid mirror messages. Default: False")
parser.add_argument("--war", "-w", type=str, default="", help="If specified, only analyze the war log with the given name. Default: ''")
args = parser.parse_args()

# Permanent immunities are players who are members of Leadership; they cannot be kicked. 
permanent_immunities = [ 
    "Sned",
    "BumblinMumbler",
    "Anas", 
    "Arcohol",
    "Bran6", 
    "katsu", 
    "Golden Unicorn✨", 
    "Marlec"
]

with open("xray-claims.txt", "r", encoding="utf-8") as file: 
    xray_claims = file.readlines()

with open("xray-minion.txt", "r", encoding="utf-8") as file:
    xray_data = file.readlines()

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
        self.inactivity = 0

claims_dictionary = {}

for claim in xray_claims: 
    claim_th, claim_tag, claim_name, claimer = re.search(claims_pattern, claim).groups()

    claim_th = int(claim_th)
    claim_tag = claim_tag.strip()
    claim_name = claim_name.strip()
    claimer = claimer.strip()

    for account in xray_data: 
        account_tag, account_name = re.search(full_account_name_pattern, account).groups()

        account_tag = account_tag.strip()
        account_name = account_name.strip()
        
        if "’" in account_name: account_name = account_name.replace("’", "'")
        if "\_" in account_name: account_name = account_name.replace("\_", "_")
        if "\~" in account_name: account_name = account_name.replace("\~", "~")

        if account_tag == claim_tag: 
            if claimer not in claims_dictionary: claims_dictionary[claimer] = []
            claims_dictionary[claimer].append(Claim(claim_th, claim_tag, account_name, False, "Reddit X-ray"))
            break

known_mains = []

num_alts_xray = 0
num_alts_outlaws = 0

for claimer in claims_dictionary: 
    for claim in claims_dictionary[claimer]:
        accounts = [claim for claim in claims_dictionary[claimer] if claim.clan == "Reddit X-ray"]
        num_accounts = len(accounts)

        known_main = False
        if num_accounts > 1:
            for account in accounts:
                if account.name in known_mains: 
                    account.is_main = True
                    known_main = True
                    break

        if known_main:
            claims_dictionary[claimer] = [account for account in accounts if account.is_main] + [account for account in accounts if not account.is_main]

        elif num_accounts == 1: 
            main_account = accounts[0]
            main_account.is_main = True

            claims_dictionary[claimer] = [main_account] + [claim for claim in claims_dictionary[claimer] if claim.tag != main_account.tag]

        else: 
            for account in accounts:
                if account.name in known_mains: 
                    account.is_main = True
                    break

            if len([account for account in accounts if account.is_main]) == 0:
                # At this point, we have still not identified a main account. 
                # Set the account with the highest town hall level as the main account.
                main_account = max(accounts, key=lambda account: account.town_hall)
                main_account.is_main = True

                claims_dictionary[claimer] = [main_account] + [account for account in accounts if account.tag != main_account.tag]

            else: 
                claims_dictionary[claimer] = [account for account in accounts if account.is_main] + [account for account in accounts if not account.is_main]

for claimer in claims_dictionary:
    for claim in claims_dictionary[claimer]: 
        if not claim.is_main and claim.clan == "Reddit X-ray": num_alts_xray += 1

# Sort the claims dictionary, first by the town hall of the main account descending, then by the number of known alts ascending.
claims_dictionary = {claimer: claims_dictionary[claimer] for claimer in sorted(claims_dictionary, key=lambda claimer: (max([account.town_hall for account in claims_dictionary[claimer] if account.is_main]), len([account for account in claims_dictionary[claimer] if not account.is_main])), reverse=True)}

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

for log_file in logs: 
    with open(f"./logs/{log_file}.txt", "r", encoding="utf-8") as file: 
        lines = file.readlines()

    for line in lines: 
        if "2 Remaining Attacks" in line.strip(): 
            attack_list = 2
            continue

        if attack_list == 2: 
            player_name = line.strip()[8:]
            
            if "’" in player_name: player_name = player_name.replace("’", "'")
            if "\_" in player_name: player_name = player_name.replace("\_", "_")
            if "\~" in player_name: player_name = player_name.replace("\~", "~")

            # Find the player in the claims dictionary, and add 2 to their inactivity counter.
            # Skip this if they're flagged as an alt, or immune. 

            for claimer in claims_dictionary:
                for claim in claims_dictionary[claimer]:
                    if claim.name == player_name: 
                        if claim.name in permanent_immunities: 
                            break
                        claim.inactivity += 2
                        break

        if "1 Remaining Attack" in line.strip():
            attack_list = 1
            continue

        if attack_list == 1:
            player_name = line.strip()[8:]

            if "’" in player_name: player_name = player_name.replace("’", "'")
            if "\_" in player_name: player_name = player_name.replace("\_", "_")
            if "\~" in player_name: player_name = player_name.replace("\~", "~")

            for claimer in claims_dictionary:
                for claim in claims_dictionary[claimer]:
                    if claim.name == player_name: 
                        if claim.name in permanent_immunities: 
                            break
                        claim.inactivity += 1
                        break

# Remove players with no inactivity, alts, and immunities.
for claimer in list(claims_dictionary.keys()): 
    # If one of the accounts linked to this player is in the permanent immunities list, delete only that account.
    if any([claim.name in permanent_immunities for claim in claims_dictionary[claimer]]):
        claims_dictionary[claimer] = [claim for claim in claims_dictionary[claimer] if claim.name not in permanent_immunities]
        continue

    # If one of the accounts linked to this player has no inactivity, delete only that account. 
    claims_dictionary[claimer] = [claim for claim in claims_dictionary[claimer] if claim.inactivity > 0]

# Inactivity dictionary is defined as account name as key, and value as a tuple of inactivity and whether this account is an alt. 
# In this dictionary, we don't care about who the player is linked to.
inactivity_dictionary = {}

for claimer in claims_dictionary:
    for claim in claims_dictionary[claimer]: 
        if claim.name not in inactivity_dictionary: inactivity_dictionary[claim.name] = (0, claim.is_main)
        inactivity_dictionary[claim.name] = (inactivity_dictionary[claim.name][0] + claim.inactivity, inactivity_dictionary[claim.name][1])

# Sort the inactivity dictionary by inactivity descending.
inactivity_dictionary = {account: inactivity_dictionary[account] for account in sorted(inactivity_dictionary, key=lambda account: inactivity_dictionary[account][0], reverse=True)}

# Max claim name length is the number of characters in the longest player's name. 
max_claim_name_length = max([len(claim.name) for claimer in claims_dictionary for claim in claims_dictionary[claimer]])

# Max player name length is the number of characters in the longest player's name.
max_player_name_length = max([len(claimer) for claimer in claims_dictionary])

with open("activity_output.txt", "w", encoding="utf-8") as file:
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
     
    file.write("\n")
    file.write("Inactivity scores as of <t:" + str(int(datetime.datetime.now().timestamp())) + ":F> (<t:" + str(int(datetime.datetime.now().timestamp())) + ":R>):\n")

    # First, we want to print all the alts. 
    file.write("Alts:\n```\n")

    for account in inactivity_dictionary:
        if inactivity_dictionary[account] == 0: continue
        elif inactivity_dictionary[account][1]: continue
        
        file.write(f"{account}{' '*(max_claim_name_length-len(account))} -- {inactivity_dictionary[account]}\n")

    file.write("```\n")

    # Next, we want to print all the mains.
    file.write("Mains:\n```\n")

    for account in inactivity_dictionary:
        if inactivity_dictionary[account] == 0: continue
        elif not inactivity_dictionary[account][1]: continue

        file.write(f"{account}{' '*(max_claim_name_length-len(account))} -- {inactivity_dictionary[account]}\n")

    file.write("```\n")

    file.write("```")