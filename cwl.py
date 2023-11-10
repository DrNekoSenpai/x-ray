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
    pattern = r"^[A-Za-z0-9 !@#$%^&*()\-=\[\]{}|;:'\",.<>/?\\_+]*$"
    return re.match(pattern, input_string) is not None 

with open("minion.txt", "r", encoding="utf-8") as f: 
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

    # Find the player in the list of players, as well as their player tag. 
    for i in range(len(players)):
        if players[i][0] == player: 
            tag = players[i][1]
            break
    
    # Send a GET request to the player's profile page.
    html = requests.get(f"https://fwa.chocolateclash.com/cc_n/member.php?tag={tag}").text

    pattern = re.compile(r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})</a></td><td>Joined clan  as <span style=\"background-color:#eee;\">a member</span>")
    match = pattern.search(html)

    if match: 
        timedelta = datetime.datetime.now() - datetime.datetime.strptime(match.group(1), "%Y-%m-%d %H:%M:%S")
        months = timedelta.days // 30

        if months > 6: 
            entries[player] += 6
            loyalty_entries[player] = 6
        else: 
            entries[player] += months
            loyalty_entries[player] = months

    else: 
        entries[player] += 6
        loyalty_entries[player] = 6

# Sort entries by weight in descending order, then by hit entries, then by loyalty entries 
entries = {k: v for k, v in sorted(entries.items(), key=lambda item: (item[1], hit_entries[item[0]], loyalty_entries[item[0]]), reverse=True)}

# for player,weight in entries.items(): 
#     if weight != 0: print(f"{player}: {weight} entries ({hit_entries[player]} entries from hits, {loyalty_entries[player]} entries from loyalty)")

from datetime import datetime
month = datetime.now().strftime("%B")
year = datetime.now().year
dists_possible = 4

print(f"**Reddit X-ray {month} {year} Weighted Distribution** \n ({dists_possible} available bonuses, total) \n ")

pool = []

for i in range(15, 0, -1): 
    # Get the tier, that is, all the players who have this amount of entries. 
    tier = [k for k,v in entries.items() if v == i]
    if len(tier) == 0: continue
    print(f"{i} entries:")
    for player in tier: 
        print(f"- {player} ({hit_entries[player]} entries from hits, {loyalty_entries[player]} entries from loyalty)")
        for _ in range(i): 
            pool.append(player)
    print("")

import random

for _ in range(dists_possible): 
    choice = random.choice(pool)
    # Remove all instances of this player from the pool.
    pool = [p for p in pool if p != choice]
    print(choice)