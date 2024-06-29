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

assert len(roster) == 50, "roster is not 50 players"
list = [9,12,16,29,30,34,37,38,39,45,49]

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