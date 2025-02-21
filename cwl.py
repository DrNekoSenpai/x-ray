import datetime, re, argparse, subprocess, random, openpyxl, pickle

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
parser.add_argument("--bypass", "-b", action="store_true", help="Bypass check for FWA bases; useful if clan earned immunity")
parser.add_argument("--update", "-u", action="store_true", help="Update distribution history with new data")
parser.add_argument("--winner", "-w", type=str, nargs="+", help="Force a particular player to be selected")
parser.add_argument("--ineligible", "-i", type=str, nargs="+", help="Force a particular player to be unable to be selected")
parser.add_argument("--view_history", "-v", action="store_true", help="View distribution history and exit")

# Parse the arguments
args = parser.parse_args()

if args.update: 
    # Load distribution history
    try: 
        with open("dist_history.pickle", "rb") as f:
            dist_history = pickle.load(f)

    except FileNotFoundError:
        dist_history = []

    # Ask how many distributions there were last month
    num_dists = int(input("How many distributions were available? "))
    date_received = input("Date received (YYYY-MM-DD): ")
    date_received = datetime.datetime.strptime(date_received, "%Y-%m-%d")

    print("")
    for i in range(num_dists): 
        player = input(f"Player {i+1}: ")

        weeks_logged = 0
        log_dates = []
        
        dist_history.append((player, date_received, weeks_logged, log_dates))

    with open("dist_history.pickle", "wb") as f:
        pickle.dump(dist_history, f)

    exit(0)

if args.view_history:
    try: 
        with open("dist_history.pickle", "rb") as f: 
            dist_history = pickle.load(f)

    except FileNotFoundError: 
        print("No distribution history found.")
        exit(0)

    for i, entry in enumerate(dist_history): 
        print(f"Player {i+1}: {entry[0]}")
        print(f"  - Date received: {entry[1].strftime('%Y-%m-%d')}")
        print(f"  - Weeks logged: {entry[2]}")
        print(f"  - Log dates: {entry[3]}")
        print("")

    exit(0)

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

if not args.bypass: 
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

                    except KeyError: 
                        # Assume they aren't in the database because they did no hits. Continue. 
                        continue 

                else: 
                    fwa_base_penalties[player] = 0

else: 
    # EVERYONE has no FWA base points.
    fwa_base_penalties = {player: 0 for player in entries.keys()}

# Sort entries by weight in descending order, then by hit entries, then by loyalty entries 
entries = {k: v for k, v in sorted(entries.items(), key=lambda item: (item[1], hit_entries[item[0]]), reverse=True)}

month = datetime.datetime.now().strftime("%B")
year = datetime.datetime.now().year

if args.num_dists == 0: 
    num_dists = int(input("How many distributions are available? "))

else:
    num_dists = args.num_dists

pool = []

class Player: 
    def __init__(self, name:str, date_received:datetime.datetime, weeks_logged:int, log_dates:list): 
        self.name = name
        self.date_received = date_received
        self.weeks_logged = weeks_logged
        self.log_dates = log_dates

try: 
    with open("dist_history.pickle", "rb") as f: 
        dist_history = pickle.load(f)

except FileNotFoundError:
    dist_history = []

# For all players in the input, add one week per two hits done. If they did seven, add one more.
# Two hits, one week. Four hits, two weeks. Six hits, three weeks. Seven hits, four weeks.

max_value = 32

for player, hits in hit_entries.items():
    # First, check if this player already exists in dist_history.
    if player in [p[0] for p in dist_history]:
        for i, entry in enumerate(dist_history): 
            if entry[0] == player: 
                # Add one week per two hits done. If they did seven, add one more.
                weeks_logged = entry[2] + (hits // 2)
                if hits == 7: weeks_logged += 1

                dist_history[i] = (player, entry[1], weeks_logged)

                # Check if the number of weeks elapsed between their receipt date and now, plus the number of weeks logged, is greater than the maximum value.

                if (datetime.datetime.now() - entry[1]).days // 7 + weeks_logged >= max_value: 
                    print(f"Player {player} has hit the threshold.")
                    print(f"  - Date received: {entry[1].strftime('%Y-%m-%d')}")
                    print(f"  - Weeks logged: {weeks_logged}")
                    print(f"  - Weeks elapsed: {(datetime.datetime.now() - entry[1]).days // 7}")
                    print(f"  - Maximum value: {max_value}")

                    # If the player has hit the threshold, remove them from the list.
                    dist_history.pop(i)

                else: 
                    print(f"Player {player}:")
                    print(f"  - Date received: {entry[1].strftime('%Y-%m-%d')}")
                    print(f"  - Weeks logged: {weeks_logged}")
                    print(f"  - Weeks elapsed: {(datetime.datetime.now() - entry[1]).days // 7}")
                    print(f"  - Maximum value: {max_value}")

                break

print("")
print(f"**Reddit X-ray {month} {year} Weighted Distribution**")
if args.bypass: print(f"({num_dists} available bonuses, total; FWA base penalties ignored)")
else: print(f"({num_dists} available bonuses, total)")
print("")

with open("dist_history.pickle", "wb") as f: 
    pickle.dump(dist_history, f)

eligible = [p for p in entries.keys() if p not in dist_history]
ineligible = [p for p in entries.keys() if p in dist_history]

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
    print(f"{i} entries: ", end = "")
    print(f"{', '.join(tier)}")
    for player in tier: 
        for _ in range(i): 
            pool.append(player)

print("")
print(f"Ineligible: {', '.join(ineligible)}")
print("")

winners = []

if args.winner: 
    # If there was a forced winner, we should remove them from the pool and add them to the list of winners. 
    winners.extend(args.winner)

print(f"**This month's {num_dists} selected winners are**:")

while True:  
    choice = random.choice(pool)
    # Remove all instances of this player from the pool.
    pool = [p for p in pool if p != choice]

    if args.ineligible and choice in args.ineligible: continue
    if choice in winners: continue

    winners.append(choice)

    if len(winners) == num_dists: break

for winner in winners:
    print(f"- {winner}")