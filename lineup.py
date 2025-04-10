import re, subprocess, argparse
from contextlib import redirect_stdout as redirect
from io import StringIO
from strikes import up_to_date

if up_to_date() is False:
    print("Error: the local repository is not up to date. Please pull the latest changes before running this script.")
    print("To pull the latest changes, simply run the command 'git pull' in this terminal.")
    exit(1)

parser = argparse.ArgumentParser(description="Generate a list of players from a war lineup.") 
parser.add_argument("--names", "-n", help="Print out the formatted list of players in the lineup without checking numbers.", action="store_true")
args = parser.parse_args()

with open("claims_output.txt", "r", encoding="utf-8") as file: 
    claims = file.read().split("\n\n")

with open("lineup.txt", "r", encoding="utf-8") as file: 
    lineup = file.read().splitlines()

    if lineup[0] == ":Blank: :Sword: :BarbarianKing: :ArcherQueen: :GrandWarden: :RoyalChampion:":
        lineup.pop(0)

# /stats dump role: @Reddit X-ray query: -f %i;%n;%u
with open("dump.txt", "r", encoding="utf-8") as file:
    dump = [f.split(";") for f in file.read().splitlines()]

# :16: :EmptySword: :95: :95: :70: :45: ‭⁦Satan⁩‬
name_pattern = re.compile(r":.*:\s:.*:\s:.*:\s:.*:\s:.*:\s:.*:\s‭⁦(.*)⁩‬")
roster = {}

for ind,line in enumerate(lineup):
    name = name_pattern.search(line).group(1)
    roster[name] = ind+1

if args.names: 
    for player in roster.keys():
        print(f"{player}")
    exit(0)

if len(roster) == 30 or len(roster) == 15: 
    # Clan War Leagues
    # War 1: 1 3 4 8 9 12 13 16 18 19 23 24 25 29 
    list = [1,3,4,8,9,12,13,16,18,19,23,24,25,29]
    # For each player in the roster, if their number is in list, print FALSE
    # Otherwise, print a new line
    
    for player,num in roster.items():
        if num in list: 
            print(f"FALSE")
        else:
            print(f"")

else: 
    # List: 17 28 32 38 45 47
    list = [17,28,32,38,45,47]
    roster = {player: num for player,num in roster.items() if num in list}

    class Claim: 
        def __init__(self, name, discord_id): 
            self.name = name
            self.discord_id = discord_id

    # Unicorn✨ | AST: 1 account in Reddit X-ray, 0 accounts in Faint Outlaws
    # Account for plural forms
    discord_name_pattern = re.compile(r"(.*): \d+ account(s)? in Reddit X-ray")

    def find_discord_id(name, output): 
        for claim in output:
            if name in claim: 
                discord_name = discord_name_pattern.search(claim).group(1) if discord_name_pattern.search(claim) else None
                if discord_name is None: 
                    print(f"{name} not found in claims")

                # Find the discord ID in the dump file with the matching discord name
                discord_id = None
                for line in dump: 
                    if discord_name in line[1] or discord_name in line[2]: 
                        discord_id = line[0]
                        break

                if discord_id is None: print(f"{discord_name} not found in dump")
                return discord_id

    for player,num in roster.items():
        discord_id = find_discord_id(player, claims)
        if discord_id is not None: 
            print(f"{num}. {player} <@{discord_id}>")

    print("")

    count = 0
    for player,num in roster.items(): 
        discord_id = find_discord_id(player, claims)
        if discord_id is not None:
            count += 1
            if count == 5: 
                print(f"@{player}")
                count = 0
            else: 
                print(f"@{player}", end=" ")