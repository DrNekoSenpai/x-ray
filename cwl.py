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
            player = player.replace("\\", "").strip()

            if player not in [p[1] for p in players]:
                players.append((player, tag))
        else: 
            print(f"Error: {line} does not match pattern")

entries = {}
hit_entries = {}
fwa_base_penalties = {}

for player,hits in cwl: 
    if hits == "0":
        entries[player] = 0
        hit_entries[player] = 0
    else: 
        entries[player] = int(hits)
        hit_entries[player] = int(hits)

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

# Sort entries by weight in descending order, then by hit entries, then by loyalty entries 
entries = {k: v for k, v in sorted(entries.items(), key=lambda item: (item[1], hit_entries[item[0]]), reverse=True)}

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
Mythos
ViperX56
pg
DPK|LLZONE
skyeshade
slothnz
Plantos
RoyalOne
Sned
Baleus
DNG
Kaselcap
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
        print(f"- {player} ({hit_entries[player]} entries from hits", end = "")
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