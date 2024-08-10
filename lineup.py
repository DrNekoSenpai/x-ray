import re, subprocess
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

with open("claims_output.txt", "r", encoding="utf-8") as file: 
    claims = file.read().split("\n\n")

with open("lineup.txt", "r", encoding="utf-8") as file: 
    lineup = file.read().splitlines()

with open("dump.txt", "r", encoding="utf-8") as file:
    dump = [f.split(";") for f in file.read().splitlines()]

# :16: :EmptySword: :95: :95: :70: :45: ‭⁦Satan⁩‬
name_pattern = re.compile(r":.*:\s:.*:\s:.*:\s:.*:\s:.*:\s:.*:\s‭⁦(.*)⁩‬")
roster = {}

for ind,line in enumerate(lineup):
    name = name_pattern.search(line).group(1)
    roster[name] = ind+1

if len(roster) == 30 or len(roster) == 15: 
    # Clan War Leagues
    war_number = 1
    # War 1: 1 3 4 8 9 12 13 16 18 19 23 24 25 29 
    list = [1,3,4,8,9,12,13,16,18,19,23,24,25,29]
    # For each player in the roster, if their number is in list, print FALSE
    # Otherwise, print a new line
    
    for player,num in roster.items():
        if num in list: 
            print(f"FALSE")
        else:
            print(f"")

    # If this is war 1, then we should save the roster order in a file. 
    if war_number == 1:
        with open("war1.txt", "w", encoding="utf-8") as file: 
            for player,num in roster.items(): 
                file.write(f"{num}. {player}\n")

    # If not, we should open war1 roster and compare the ordering with the current roster. 
    # If there are any differences, we should sort the current roster in the same order as war1 roster.
    # Example: Sned was #3 in war 1, but he is #2 in war 2. Move Sned in the #3 position in war 2.

    else: 
        with open("war1.txt", "r", encoding="utf-8") as file: 
            war1 = file.read().splitlines()

        war1 = {player: num for num,player in (f.split(". ") for f in war1)}
        for player,num in war1.items():
            if player not in roster: 
                print(f"{player} not found in the current roster")
            elif roster[player] != int(num): 
                print(f"{player} is not in the correct position. Move {player} to position {num}")

if len(roster) == 50: 
    # List: 2 11 21 23 27 28 35 39 41 45 48
    list = [2,11,21,23,27,28,35,39,41,45,48]
    roster = {player: num for player,num in roster.items() if num in list}

    class Claim: 
        def __init__(self, name, discord_id): 
            self.name = name
            self.discord_id = discord_id

    # Unicorn✨ | AST: 1 account in Reddit X-ray, 0 accounts in Faint Outlaws
    # Account for plural forms
    discord_name_pattern = re.compile(r"(.*): \d+ account(s)? in Reddit X-ray, \d+ account(s)? in Faint Outlaws")

    def find_discord_id(name, output): 
        for claim in output:
            if name in claim: 
                discord_name = discord_name_pattern.search(claim).group(1) if discord_name_pattern.search(claim) else None
                if discord_name is None: print(f"{name} not found in claims")

                # Find the discord ID in the dump file with the matching discord name
                discord_id = None
                for line in dump: 
                    if discord_name in line[1] or discord_name in line[2]: 
                        discord_id = line[0]
                        break

                if discord_id is None: print(f"{discord_name} not found in dump")
                return discord_id

    for player,num in roster.items():
        print(f"{num}. {player} <@{find_discord_id(player, claims)}>")

    print("")

    count = 0
    for player,num in roster.items(): 
        count += 1
        if count == 5: 
            print(f"@{player}")
            count = 0
        else: 
            print(f"@{player}", end=" ")