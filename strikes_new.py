import pickle, datetime, argparse, requests, os, re, subprocess
from contextlib import redirect_stdout as redirect
from io import StringIO

class player():
    def __init__(self, name, tag):
        self.name = name
        self.tag = tag
        self._leadership = False
        self.num_strikes = 0
        self.strikes = []
        self.missed_hit_clans = []
        self.missed_hit_dates = []

def export_pickle(players): 
    with open('player_data.pickle', 'wb') as f:
        pickle.dump(players, f)

def import_pickle(): 
    try: 
        with open('player_data.pickle', 'rb') as f: 
            players = pickle.load(f)
    except: players = []
    return players

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
        return False
    
if not up_to_date():
    print("Error: Updates available for pulling. Please pull the latest changes (using 'git pull') and try again.")
    exit()

players = import_pickle()

def regular_keyboard(input_string): 
    pattern = r"^[A-Za-z0-9 !@#$%^&*()\-=\[\]{}|;:'\",.<>/?\\_+]*$"
    return re.match(pattern, input_string) is not None 

def add_player():
    if not os.path.isfile('minion.txt'):
        print('No file named "minion.txt" exists in the current directory.')
        return

    # Open the file and read the contents, line by line
    with open('minion.txt', 'r', encoding='utf-8', errors='replace') as file:
        for line in file: 
            # Line format: 
            # #P2UPPVYL    15 Senpai™
            # Tag is 7-9 alphanumeric characters long 
            # The number is 1-2 digits long, and is the town hall level -- we can ignore this
            # Everything else is the name 
            # We can use regex to extract the tag and name
            match = re.search(r"#([0-9A-Z]{5,9})\s+\d+\s+(.*)", line)
            if match:
                # Extract the tag and name
                tag = match.group(1)
                name = match.group(2)

                if name == "JALVIN ø": name = "JALVIN"
                if name == "★ıċєʏקѧṅṭś★": name = "IceyPants"
                if "™" in name: name = name.replace("™", "")
                if "✨" in name: name = name.replace("✨", "")

                # Check if the player's name is alphanumeric, including spaces and regular punctuation
                # If not, we need to ask the user to input the name manually. 
                if not regular_keyboard(name):
                    print(f"Player name {name} is not valid. Please input the name manually.")

                # Check if the player already exists in the database
                found = False
                for i in range(len(players)):
                    if players[i].name.lower().startswith(name.lower()):
                        found = True
                        print(f"Player {name} already exists in the database. Skipping...")
                        break

                # If the player does not exist, add them to the database
                if not found:
                    p = player(name, tag)
                    players.append(p)
                    print(f"Added player {name} #{tag} to the database.")
	
def remove_player(): 
    name = input('Enter name of player to remove: ')
    if name == '': return
    found = False
    for i in range(len(players)): 
        if players[i].name.lower().startswith(name.lower()): 
            found = True
            players[i].output()
            confirm = input('Is this the right player? Y/N: ').lower()
            if confirm == 'y' or confirm == 'yes': 
                players.pop(i)
            return
    if not found: print(f'No such player with name {name.lower()} exists.')

def add_strike(): 
    name = input("Enter name of player to add strike to: ").split("#")[0].strip()
    if name == '': return
    found = False
    for i in range(len(players)): 
        if players[i].name.lower().startswith(name.lower()): 
            found = True
            players[i].output()
            confirm = input('Is this the right player? Y/N: ').lower()
            if confirm == 'y' or confirm == 'yes': 
                