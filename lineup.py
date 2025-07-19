import re, subprocess, argparse
import pandas as pd
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

with open("./inputs/lineup.txt", "r", encoding="utf-8") as file: 
    lineup = file.read().splitlines()

    if lineup[0] == ":Blank: :Sword: :BarbarianKing: :ArcherQueen: :GrandWarden: :RoyalChampion:":
        lineup.pop(0)

xray_claims = pd.read_excel("xray-members.xlsx", sheet_name=0)
player_roster = {}
for _, row in xray_claims.iterrows():
    claim_id = int(row['ID'])
    claim_name = row['Name']
    claim_clan = row['Clan']
    if claim_clan != "Reddit X-ray": continue
    player_roster[claim_name] = [claim_id, claim_name]

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

list = [int(x) for x in "1 2 4 6 8 11 12 14 17 18 20 22 23 24 25 26 27 28 29 30 31 32 33 34 ".split( )]
roster = {player: num for player,num in roster.items() if num in list}

class Claim: 
    def __init__(self, name, discord_id): 
        self.name = name
        self.discord_id = discord_id

for player,num in roster.items():
    discord_id = player_roster.get(player, None)[0]
    if discord_id is not None: 
        print(f"{num}. {player} <@{discord_id}>")

print("")

count = 0
for player,num in roster.items(): 
    discord_id = player_roster.get(player, None)
    if discord_id is not None:
        count += 1
        if count == 5: 
            print(f"@{player}")
            count = 0
        else: 
            print(f"@{player}", end=" ")