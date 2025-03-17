import pickle, re, subprocess 
from contextlib import redirect_stdout as redirect
from io import StringIO
from datetime import datetime

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

class strike(): 
    def __init__(self, value:int, date:datetime, reason:str):
        self.value = value
        self.date = date
        self.reason = reason

    def output(self): 
        return f"({self.value}) {self.reason}"

class player():
    def __init__(self, name, tag):
        self.name = name
        self.tag = tag
        self.strikes = []

    def output(self):
        print(f'Name: {self.name}')
        print(f'Tag: {self.tag}')
        print(f'Strikes: {self.num_strikes()}')

    def num_strikes(self): 
        return sum([strike.value for strike in self.strikes])
    
    def most_recent(self): 
        return self.strikes[-1].date.strftime('%Y-%m-%d') if self.strikes else None

def export_pickle(): 
    with open('player_data.pickle', 'wb') as f:
        pickle.dump(players, f)

def import_pickle(): 
    try: 
        with open('player_data.pickle', 'rb') as f: 
            players = pickle.load(f)
    except: players = []
    return players

players = import_pickle()

def add_player(): 
    # in_str = input('Enter name and tag, separated by spaces: ').strip()
    # if in_str == '': continue
    # in_str = in_str.rsplit(' ', 1)
    # for i in range(len(players)): 
    #     if players[i].name.lower().startswith(in_str[0].lower()): 
    #         print('This player already exists! Duplicates are not allowed.')
    # p = player(in_str[0], in_str[1].upper())
    # players.append(p)

    # Open the file and read the contents, line by line
    with open(f'xray-minion.txt', 'r', encoding='utf-8', errors='replace') as file:
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

                if "’" in name: name = name.replace("’", "'")
                if "™" in name: name = name.replace("™", "")
                if "✨" in name: name = name.replace("✨", "")
                if "\\" in name: name = name.replace("\\", "")
                if "\~" in name: name = name.replace("\~", "~")

                # Check if the player already exists in the database
                found = False
                for i in range(len(players)):
                    if players[i].name == name:
                        print(f"Player {name} already exists in the database. Skipping...")
                            
                        found = True
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
        if players[i].name == name: 
            found = True
            players[i].output()
            confirm = input('Is this the right player? Y/N: ').lower()
            if confirm == 'y' or confirm == 'yes': 
                players.pop(i)
            return
    if not found: print(f"No such player with name {name} exists.")
	
def add_strike(): 
    name = input('Enter name of player to award a strike to: ').strip()
    if name == '': return
    found = False
    for i in range(len(players)): 
        if players[i].name == name:  
            found = True
            players[i].output()
            confirm = input('Is this the right player? Y/N: ').lower()
            if confirm == 'y' or confirm == 'yes': 
                print('')
                print('What kind of strike is this?')
                print('[1] Blacklist war')
                print('[2] FWA base during blacklist war')
                print('[3] War base')
                print('[4] Base errors')
                print('[5] Directions not followed')
                print('[6] Sanctions')
                print('[7] Other')
                sel = input('Selection: ')
                try: sel = int(sel)
                except: sel = 0
                print('')
                if sel == 1: 
                    date = input('Enter date (YYYY-MM-DD): ')
                    clan = input('Enter name of opponent blacklist clan: ')
                    conditional = input("Did we meet the conditional for reduced strikes? Y/N: ").lower()
                    win = input('Did we win? Y/N: ').lower()
                    num = input("How many hits did this player miss? ")

                    try: num = int(num)
                    except: num = 0
                    if num == 0: 
                        print('Invalid input entered. No strike will be awarded.')
                        return
                    
                    # Conditional for reduced strikes: true
                    # If we won, and this player missed two attacks, award one strike. 
                    # If we won, and this player missed one attack, continue (no strike awarded).
                    # If we lost, and this player missed two attacks, award two strikes.
                    # If we lost, and this player missed one attack, award one strike.
                    # If this player didn't have a war base, award one strike if we lose. 

                    # Conditional for reduced strikes: false
                    # If we won, and this player missed two attacks, award two strikes.
                    # If we won, and this player missed one attack, continue (no strike awarded).
                    # If we lost, and this player missed two attacks, award five strikes.
                    # If we lost, and this player missed one attack, award two strikes.
                    # If this player didn't have a war base, award three strikes if we lose.

                    if conditional == 'y' and win == 'y' and num == 2:
                        players[i].strikes.append(strike(1, datetime.strptime(date, "%Y-%m-%d"), f"Missed two attacks during a blacklist war against `{clan}` on {date}; we won, and met the conditional."))

                    elif conditional == 'y' and win == 'y' and num == 1:
                        continue

                    elif conditional == 'y' and win == 'n' and num == 2:
                        players[i].strikes.append(strike(2, datetime.strptime(date, "%Y-%m-%d"), f"Missed two attacks during a blacklist war against `{clan}` on {date}; we lost, but met the conditional."))

                    elif conditional == 'y' and win == 'n' and num == 1:
                        players[i].strikes.append(strike(1, datetime.strptime(date, "%Y-%m-%d"), f"Missed one attack during a blacklist war against `{clan}` on {date}; we lost, but met the conditional."))

                    elif conditional == 'n' and win == 'y' and num == 2:
                        players[i].strikes.append(strike(2, datetime.strptime(date, "%Y-%m-%d"), f"Missed two attacks during a blacklist war against `{clan}` on {date}; we won."))

                    elif conditional == 'n' and win == 'y' and num == 1:
                        continue

                    elif conditional == 'n' and win == 'n' and num == 2:
                        players[i].strikes.append(strike(5, datetime.strptime(date, "%Y-%m-%d"), f"Missed two attacks during a blacklist war against `{clan}` on {date}; we lost."))

                    elif conditional == 'n' and win == 'n' and num == 1:
                        players[i].strikes.append(strike(2, datetime.strptime(date, "%Y-%m-%d"), f"Missed one attack during a blacklist war against `{clan}` on {date}; we lost."))

                    else:
                        print('Invalid input entered. No strike will be awarded.')
                        return
                    
                elif sel == 2: 
                    date = input('Enter date (YYYY-MM-DD): ')
                    clan = input('Enter name of opponent blacklist clan: ')
                    conditional = input("Did we meet the conditional for reduced strikes? Y/N: ").lower()

                    if conditional == 'y': 
                        players[i].strikes.append(strike(1, datetime.strptime(date, "%Y-%m-%d"), f"FWA base during blacklist war against `{clan}`; we won, and met the conditional on {date}."))

                    elif conditional == 'n':
                        players[i].strikes.append(strike(3, datetime.strptime(date, "%Y-%m-%d"), f"FWA base during blacklist war against `{clan}`; we won, but didn't meet the conditional on {date}."))

                elif sel == 3: 
                    date = input('Enter date (YYYY-MM-DD): ')
                    enemy_clan = input('Enter name of opponent clan: ')
                    players[i].strikes.append(strike(5, datetime.strptime(date, "%Y-%m-%d"), f"Had war base during battle day against `{enemy_clan}` on {date}."))
                    
                elif sel == 4: 
                    date = input('Enter date (YYYY-MM-DD): ')
                    hot_mess = input('Did we have five or more base errors? Y/N: ').lower()
                    enemy_clan = input('Enter name of opponent clan: ')

                    if hot_mess == 'y': 
                        players[i].strikes.append(strike(2, datetime.strptime(date, "%Y-%m-%d"), f"Had five or more base errors during a war against `{enemy_clan}` on {date}."))
                        
                    else:
                        players[i].strikes.append(strike(1, datetime.strptime(date, "%Y-%m-%d"), f"Had less than five base errors during a war against `{enemy_clan}` on {date}."))

                elif sel == 5: 
                    date = input('Enter date (YYYY-MM-DD): ')
                    print('What kind of instruction did this player not follow? ')
                    print('[1] Three-starred during a loss war')
                    print('[2] Attacked someone else than mirror')
                    print('[3] Sniped twice instead of attacking mirror')
                    print('[4] Sniped once and didn\'t use other hit')
                    sel = input('Selection: ')
                    try: sel = int(sel)
                    except: sel = 0

                    if sel == 0: 
                        print('Invalid input entered. No strike will be awarded.')
                        print('')

                    elif sel == 1: 
                        clan = input('Enter opponent clan name for when this player three-starred during a loss war: ')
                        players[i].strikes.append(strike(1, datetime.strptime(date, "%Y-%m-%d"), f"Three-starred during a loss war against `{clan}` on {date}."))

                    elif sel == 2:
                        clan = input('Enter opponent clan name for when this player attacked someone else than mirror: ')
                        players[i].strikes.append(strike(1, datetime.strptime(date, "%Y-%m-%d"), f"Attacked someone else than mirror during a war against `{clan}` on {date}."))

                    elif sel == 3:
                        clan = input('Enter opponent clan name for when this player sniped twice instead of attacking mirror: ')
                        players[i].strikes.append(strike(1, datetime.strptime(date, "%Y-%m-%d"), f"Sniped twice instead of attacking mirror during a war against `{clan}` on {date}."))

                    elif sel == 4:
                        clan = input('Enter opponent clan name for when this player sniped once and didn\'t use other hit: ')
                        players[i].strikes.append(strike(1, datetime.strptime(date, "%Y-%m-%d"), f"Sniped once and didn't use other hit during a war against `{clan}` on {date}."))
                                    
                elif sel == 6: 
                    date = input('Enter date (YYYY-MM-DD): ')
                    message = input('Enter sanction message here: ')
                    players[i].strikes.append(strike(1, datetime.strptime(date, "%Y-%m-%d"), f"Targeted by sanctions on {date}; {message}"))

                elif sel == 7: 
                    date = input('Enter date (YYYY-MM-DD): ')
                    clan = input('Enter opponent clan name for when this player disobeyed instructions: ')
                    message = input('Enter strike message here. Use <clan> to substitute the opponent clan name: ')
                    message = message.split('<clan>')
                    if len(message) == 1: message = message[0]
                    else: message = clan.join(message)
                    n = input('How many strikes is this worth? ')
                    try: n = int(n)
                    except: n = 0
                    if n == 0: 
                        print('Invalid number of strikes entered. No strikes will be awarded.')
                        return
                    elif n > 5: 
                        print('A strike can\'t be worth more than 5 strikes! No strikes will be awarded.')
                        return
                    else: 
                        players[i].strikes.append(strike(n, datetime.strptime(date, "%Y-%m-%d"), f"{message}"))
                return
                
    if not found: 
        print(f"No such player with name {name} exists.")
	
def remove_strike():
    name = input('Enter name of player to remove a strike from: ')
    if name == '': return
    found = False

    for i in range(len(players)): 
        if players[i].name == name: 
            found = True

            players[i].output()
            confirm = input('Is this the right player? Y/N ').lower()
            if confirm == 'y' or confirm == 'yes': 
                for j in range(len(players[i].strikes)):
                    print(f"{j+1}) {players[i].strikes[j]}")
                num = input('Which strike needs to be removed? ')
                try: num = int(num)
                except: num = 0
                if num == 0: 
                    print('Invalid selection entered. No strike will be removed.')
                    return
                else: 
                    int_val = re.search(r"\((\d)\)", players[i].strikes[num-1].reason)
                    if int_val: val = int(int_val.group(1))
                    players[i].strikes.pop(num-1)

                return
            
    if not found: 
        print(f"No such player with name {name} exists.")
	
def remove_all_strikes(): 
    name = input('Enter name of player to remove all strike from: ')
    if name == '': return
    found = False
    for i in range(len(players)): 
        if players[i].name == name:  
            found = True
            players[i].output()
            confirm = input('Is this the right player? Y/N ').lower()
            if confirm == 'y' or confirm == 'yes': 
                players[i].strikes = []
                return
            
    if not found: 
        print(f"No such player with name {name} exists.")

def clear_strikes():
    confirm = input('Are you sure you want to clear all strikes? This cannot be undone. Y/N: ').lower()
    if confirm == 'y': 
        for i in range(len(players)):
            players[i].strikes = []

def output_strikes():
    with open('strikes.txt', 'w', encoding="utf-8") as file: 
        file.write('**Reddit X-ray**:\n\n')
        
        for i in range(len(players)): 
            if players[i].num_strikes() != 0:
                file.write(f"[{players[i].num_strikes()}] {players[i].name} #{players[i].tag} -- last strike received on {players[i].most_recent()}\n")

                for j in range(len(players[i].strikes)): 
                    file.write(f"- {players[i].strikes[j].output()}\n")

                file.write('\n')

def epoch_timestamp(dt:datetime): 
    return int(dt.strftime('%Y%m%d')) if dt else 0

if __name__ == "__main__":
    players = import_pickle()

    strike_threshold = 60

    for i in range(len(players)):
        if players[i].strikes and (datetime.now() - players[i].strikes[-1].date).days > strike_threshold: 
            print(f"Player {players[i].name}'s last strike was more than {strike_threshold} days ago. Clearing all strikes.")
            players[i].strikes = []

    while(True): 
        # Sort the list of players; first by number of strikes descending, then by date of last strike descending, then by name ascending.
        # Not everyone's going to have strikes; if their number of strikes is 0, there's not going to be a last strike. In this case, ignore the date and sort without it. 
        players.sort(key=lambda x: (
            -x.num_strikes(),  # Sort by strikes descending
            -max([epoch_timestamp(strike.date) for strike in x.strikes], default=0),  # Sort by date of last strike descending
            x.name.lower()  # Sort by name ascending
        ))
        print('')

        print('---- Reddit X-ray Strike Automation System ----')
        print('[1] Add new players')
        print('[2] Remove a player')
        print('[3] Award a strike')
        print('[4] Remove a strike')
        print('[5] Clear all strikes for a given player')
        print('[6] Reset all strikes')
        print('[7] Output strikes list')
        print('[9] Exit')
        sel = input('Selection: ')
        if sel == "": break 
        
        try: sel = int(sel)
        except: continue

        export_pickle()
        if sel == 1: add_player()
        elif sel == 2: remove_player()
        elif sel == 3: add_strike()
        elif sel == 4: remove_strike()
        elif sel == 5: remove_all_strikes()
        elif sel == 6: clear_strikes()
        elif sel == 7: output_strikes()

        else: break