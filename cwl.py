from argparse import ArgumentParser
import datetime
import requests
import re

parser = ArgumentParser()
parser.add_argument('-i', '--input', help='Command line input', default=None)
args = parser.parse_args()

with open("cwl-input.txt", "r", encoding="utf-8") as f: 
    cwl = f.readlines()
    cwl = [x.strip().rsplit(" ", 1) for x in cwl]

players = []

def regular_keyboard(input_string): 
    pattern = r"^[A-Za-z0-9 \~!@#$%^&*()\-=\[\]{}|;:'\",.<>/?\\_+]*$"
    return re.match(pattern, input_string) is not None 

clan = "outlaws"

with open(f"minion-{clan}.txt", "r", encoding="utf-8") as f: 
    minion = f.readlines()
    pattern = re.compile(r"#([0-9A-Z]{5,9})\s+\d+\s+(.*)")
    for line in minion: 
        match = pattern.match(line)
        if match: 
            tag, player = match.groups()
            player = player.replace("\\_", "_")
            player = player.replace("™", "")

            if player == "JALVIN ø": player = "JALVIN"
            if player == "★ıċєʏקѧṅṭś★": player = "IceyPants"
            if player == "༺༃༼SEV༽༃༻": player = "SEV"
            if player == "\~CLUNK\~": player = "CLUNK"
            if player == "❤️lav❤️": player = "lav"
            if player == "Lil’ Blump": player = "Lil' Blump"
            if player == "「 NightEye 」": player = "NightEye"

            if "✨" in player: player = player.replace("✨", "")

            if not regular_keyboard(player):
                print(f"Error: {player} #{tag} contains invalid characters")
                continue

            if player not in [p[1] for p in players]:
                players.append((player, tag))
        else: 
            print(f"Error: {line} does not match pattern")

entries = {}
hit_entries = {}
loyalty_entries = {}

for player,hits in cwl: 
    if hits == "0":
        entries[player] = 0
        hit_entries[player] = 0
    else: 
        entries[player] = int(hits)
        hit_entries[player] = int(hits)

    tag = ""

    # Find the player in the list of players, as well as their player tag. 
    for i in range(len(players)):
        if players[i][0] == player: 
            tag = players[i][1]
            break

    if tag == "":
        print(f"Error: {player} not found in list of players")
        entries[player] = 0
        loyalty_entries[player] = 0
        continue

    # Override: BumblinMumbler has 6 months of loyalty, no matter what
    if player == "BumblinMumbler": 
        entries[player] += 6
        loyalty_entries[player] = 6
        continue
    
    # Send a GET request to the player's profile page.
    html = requests.get(f"https://fwa.chocolateclash.com/cc_n/member.php?tag={tag}").text

    joined_pattern = re.compile(r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})</a></td><td>Joined clan")
    scan_pattern = re.compile(r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})</a></td><td>Seen in clan")
    join_matches = joined_pattern.findall(html)
    scan_matches = scan_pattern.findall(html)
    matches = join_matches + scan_matches
    matches.sort(key=lambda x: datetime.datetime.strptime(x, "%Y-%m-%d %H:%M:%S"), reverse=True)

    if len(matches) == 0:
        entries[player] += 6
        loyalty_entries[player] = 6
        continue

    timedelta = datetime.datetime.now() - datetime.datetime.strptime(matches[0], "%Y-%m-%d %H:%M:%S")
    months = timedelta.days // 30

    if months > 6:
        entries[player] += 6
        loyalty_entries[player] = 6

    else:
        entries[player] += months
        loyalty_entries[player] = months

# Sort entries by weight in descending order, then by hit entries, then by loyalty entries 
entries = {k: v for k, v in sorted(entries.items(), key=lambda item: (item[1], hit_entries[item[0]], loyalty_entries[item[0]]), reverse=True)}

# for player,weight in entries.items(): 
#     if weight != 0: print(f"{player}: {weight} entries ({hit_entries[player]} entries from hits, {loyalty_entries[player]} entries from loyalty)")

from datetime import datetime
month = datetime.now().strftime("%B")
year = datetime.now().year
dists_possible = int(input("How many distributions are available? "))
print("")
print(f"**{'Reddit X-ray' if clan == 'xray' else 'Faint Outlaws'} {month} {year} Weighted Distribution** \n ({dists_possible} available bonuses, total) \n ")

pool = []

already_received_xray = """
Satan
Trunx
Hokage
Lord Zameow
katsu
Jonas
BumblinMumbler
Eddy
IceyPants
Sned
Shomeer
Ben TH9
Coolguyagent
Kaselcap
Annayake
Protips
mysterydeath
kallikrein
Arcohol
Nitin 4.0
ViperX56
K.L.A.U.S
Bounce_04
Big Daddy T
Sivankh39
RAJE
""".strip().split("\n")

already_received_outlaws = """  
Durp
SEV
Chrispy
Clone Castle
Camo
CatoTomato
DisasterBaiter
Your Angry Ex
Dark Hell Mutt
""".strip().split("\n")

eligible = [p for p in entries.keys() if p not in already_received_xray and p not in already_received_outlaws]
# Print a warning if there are less eligible people than there are possible distributions. 
if len(eligible) < dists_possible: 
    print(f"Warning: There are only {len(eligible)} eligible people, but {dists_possible} distributions are available.")
    print("By default, this means that the following people will receive a distribution:")
    for player in eligible: 
        print(f"- {player}")
        
    exit(0)

entries = {k: v for k, v in entries.items() if k in eligible}

for i in range(15, 0, -1): 
    # Get the tier, that is, all the players who have this amount of entries. 
    tier = [k for k,v in entries.items() if v == i]
    if len(tier) == 0: continue
    print(f"{i} entries:")
    for player in tier: 
        if player in already_received_xray or player in already_received_outlaws: continue
        print(f"- {player} ({hit_entries[player]} entries from hits, {loyalty_entries[player]} entries from loyalty)")
        for _ in range(i): 
            pool.append(player)
    print("")

import random
print(f"**This month's {dists_possible} selected winners are**:")
for _ in range(dists_possible): 
    choice = random.choice(pool)
    # Remove all instances of this player from the pool.
    pool = [p for p in pool if p != choice]
    print(f"- {choice}")

with open("strikes-input.txt", "w") as file: 
    for player,hits in cwl: 
        if int(hits) > 3: continue
        else: 
            file.write(f"3\n{player}\ny\n2\ny\n")
            print(f"Player {player} missed {7-int(hits)} CWL hits; assigning strikes.")