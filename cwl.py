import datetime, requests, re, argparse, subprocess, random, openpyxl

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

# Create an argument parser
parser = argparse.ArgumentParser(description="Calculate weighted distribution for CWL")
parser.add_argument("--num_dists", "-n", type=int, default=0, help="Number of distributions available")

# Parse the arguments
args = parser.parse_args()

with open("cwl-input.txt", "r", encoding="utf-8") as f: 
    cwl = f.readlines()
    cwl = [x.strip().rsplit(" ", 1) for x in cwl]

players = []

with open(f"xray-minion.txt", "r", encoding="utf-8") as f: 
    minion = f.readlines()
    pattern = re.compile(r"#([0-9A-Z]{5,9})\s+\d+\s+(.*)")
    for line in minion: 
        match = pattern.match(line)
        if match: 
            tag, player = match.groups()
            player = player.replace("\_", "_")

            if player not in [p[1] for p in players]:
                players.append((player, tag))
        else: 
            print(f"Error: {line} does not match pattern")

entries = {}
hit_entries = {}
loyalty_entries = {}
fwa_base_penalties = {}

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
    seen_pattern = re.compile(r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})</a></td><td>Seen in clan")
    join_matches = joined_pattern.findall(html)
    seen_matches = seen_pattern.findall(html)
    matches = join_matches + seen_matches
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

# Open the war_bases.xlsx file
wb = openpyxl.load_workbook("war_bases.xlsx", data_only=True)

sheet = wb.active
data = sheet.iter_rows(values_only=True, max_row=31, max_col=3)

# For each row... 
for row in data:
    name = row[1]
    try: points = int(row[2])
    except: continue # assume header row

    # Find the corresponding player in the list of players
    for player,tag in players:
        if player == name: 
            # Print out the number of points they had, if it's above zero. 
            if points > 0:
                try: 
                    fwa_base_penalties[player] = points
                    entries[player] -= points
                    print(f"Player {player} has {points} FWA base points, resulting in a {points} entry penalty.")

                except KeyError: 
                    # Assume they aren't in the database because they did no hits. Continue. 
                    print(f"Player {player} has {points} FWA base points, but did no hits. Ignoring.")
                    continue 

            else: 
                fwa_base_penalties[player] = 0
                print(f"Player {player} has no FWA base points.")

# Failsafe: check if loyalty entries is negative. If so, set it to 0. Reflect this in entries as well.
for player in entries.keys():
    if loyalty_entries[player] < 0:
        loyalty_entries[player] = 0
        entries[player] = hit_entries[player]

# Sort entries by weight in descending order, then by hit entries, then by loyalty entries 
entries = {k: v for k, v in sorted(entries.items(), key=lambda item: (item[1], hit_entries[item[0]], loyalty_entries[item[0]]), reverse=True)}

# for player,weight in entries.items(): 
#     if weight != 0: print(f"{player}: {weight} entries ({hit_entries[player]} entries from hits, {loyalty_entries[player]} entries from loyalty)")

month = datetime.datetime.now().strftime("%B")
year = datetime.datetime.now().year

if args.num_dists == 0: 
    num_dists = int(input("How many distributions are available? "))

else:
    num_dists = args.num_dists

print("")
print(f"**Reddit X-ray {month} {year} Weighted Distribution** \n ({num_dists} available bonuses, total) \n ")

pool = []

already_received = """
brycee
K.L.A.U.S
katsu
Satan
BumblinMumbler
YOYOMAN12D
W1nter
Reactorge
Smitty™
""".strip().split("\n")

eligible = [p for p in entries.keys() if p not in already_received]
# Print a warning if there are less eligible people than there are possible distributions. 
if len(eligible) < num_dists: 
    print(f"Warning: There are only {len(eligible)} eligible people, but {num_dists} distributions are available.")
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
        if player in already_received: continue
        print(f"- {player} ({hit_entries[player]} entries from hits, {loyalty_entries[player]} entries from loyalty", end = "")
        if fwa_base_penalties[player] > 0: 
            print(f", {fwa_base_penalties[player]} entry penalty from FWA bases)", end="")
        else: 
            print(")", end="")
        print("")
        for _ in range(i): 
            pool.append(player)
    print("")

print(f"**This month's {num_dists} selected winners are**:")
for _ in range(num_dists): 
    choice = random.choice(pool)
    # Remove all instances of this player from the pool.
    pool = [p for p in pool if p != choice]
    print(f"- {choice}")

month, year = datetime.datetime.now().strftime("%B").lower(), datetime.datetime.now().year
with open(f"./inputs/cwl_{month}_{year}.txt", "w", encoding="utf-8") as file: 
    for player,hits in cwl: 
        if int(hits) > 3: continue
        # Else, if the player would have had zero entries due to FWA base penalty, continue. 
        if int(hits) - fwa_base_penalties[player] <= 0: 
            print(f"Player {player} would have been assigned strikes, but due to FWA base penalty, is not eligible for the distribution.")
            continue
        else: 
            file.write(f"3\n{player}\ny\n2\ny\n")
            print(f"Player {player} missed {7-int(hits)} CWL hits; assigning strikes.")