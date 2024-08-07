import pickle, os, re, subprocess 

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

class player():
    def __init__(self, name, tag, clan):
        self.name = name
        self.tag = tag
        self.clan = clan
        self.num_strikes = 0
        self.strikes = []
        self.missed_hit_clans = []
        self.missed_hit_dates = []

    def output(self):
        print(f'Name: {self.name}')
        print(f'Tag: {self.tag}')
        print(f'Clan: {self.clan}')
        print(f'Strikes: {self.num_strikes}')

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

def add_player(clan): 
    """Add a new player to the database, provided that they do not already exist."""
    # in_str = input('Enter name and tag, separated by spaces: ').strip()
    # if in_str == '': continue
    # in_str = in_str.rsplit(' ', 1)
    # for i in range(len(players)): 
    #     if players[i].name.lower().startswith(in_str[0].lower()): 
    #         print('This player already exists! Duplicates are not allowed.')
    # p = player(in_str[0], in_str[1].upper())
    # players.append(p)

    # Check if a file named "minion.txt" exists in the current directory

    if not os.path.isfile(f'{clan}-minion.txt'):
        print(f'No file named "{clan}-minion.txt" exists in the current directory.')
        return

    # Open the file and read the contents, line by line
    with open(f'{clan}-minion.txt', 'r', encoding='utf-8', errors='replace') as file:
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
                if "\_" in name: name = name.replace("\_", "_")
                if "\~" in name: name = name.replace("\~", "~")

                # Check if the player already exists in the database
                found = False
                for i in range(len(players)):
                    if players[i].name == name:
                        if players[i].clan != "Reddit X-ray" and clan == "xray":
                            players[i].clan = "Reddit X-ray"
                            print(f"Player {name} already exists in the database, but in the wrong clan. Changing clan to Reddit X-ray.")

                        elif players[i].clan != "Faint Outlaws" and clan == "outlaws":
                            players[i].clan = "Faint Outlaws"
                            print(f"Player {name} already exists in the database, but in the wrong clan. Changing clan to Faint Outlaws.")

                        else: 
                            print(f"Player {name} already exists in the database. Skipping...")
                            
                        found = True
                        break

                # If the player does not exist, add them to the database
                if not found:
                    player_clan = "Reddit X-ray" if clan == "xray" else "Faint Outlaws"
                    p = player(name, tag, player_clan)
                    players.append(p)
                    print(f"Added player {name} #{tag} to the database.")

	
def remove_player(): 
    """Given an existing player in the database, remove them from the database."""
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
                print('[1] Missed FWA attack')
                print('[2] CWL attacks')
                print('[3] Blacklist war')
                print('[4] War base')
                print('[5] Base errors')
                print('[6] Directions not followed')
                print('[7] Repeat offender in sanctions')
                print('[8] Other')
                sel = input('Selection: ')
                try: sel = int(sel)
                except: sel = 0
                print('')
                if sel == 1: 
                    clan = input('Enter name of opponent clan when this player missed attacks: ')
                    date = input('Enter date of when this player missed attacks. Please use MMDD format: ')
                    try: date = int(date)
                    except: date = -1
                    if date == -1: 
                        print('Invalid date entered. No strike will be awarded.')
                        return
                    players[i].missed_hit_clans.append(clan)
                    players[i].missed_hit_dates.append(date)
                    players[i].strikes.append(f"(1) Missed hits during war against `{clan}`.")
                    players[i].num_strikes += 1
                    if len(players[i].missed_hit_dates) > 1: 
                        this_war = len(players[i].missed_hit_dates) - 1
                        previous_war = len(players[i].missed_hit_dates) - 2
                        # Check if this war and previous war are the same. If so, return. 
                        if players[i].missed_hit_dates[this_war] == players[i].missed_hit_dates[previous_war]: return
                        if players[i].missed_hit_dates[previous_war] + 3 >= players[i].missed_hit_dates[this_war]: 
                            players[i].strikes.append(f"(1) Missed hits in two consecutive wars against `{players[i].missed_hit_clans[previous_war]}` and `{players[i].missed_hit_clans[this_war]}`.")
                            players[i].num_strikes += 1
                elif sel == 2: 
                    confirm = input('Please confirm you wish to award CWL strikes to this player. Y/N: ').lower()
                    if confirm != 'y' and confirm != 'yes': return
                    players[i].strikes.append('(1) Missed 4 or more hits during CWL week.')
                    players[i].num_strikes += 1
                elif sel == 3: 
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
                        players[i].strikes.append(f"(1) Missed two attacks during a blacklist war against `{clan}`; we won, and met the conditional.")
                        players[i].num_strikes += 1

                    elif conditional == 'y' and win == 'y' and num == 1:
                        continue

                    elif conditional == 'y' and win == 'n' and num == 2:
                        players[i].strikes.append(f"(2) Missed two attacks during a blacklist war against `{clan}`; we lost, but met the conditional.")
                        players[i].num_strikes += 2

                    elif conditional == 'y' and win == 'n' and num == 1:
                        players[i].strikes.append(f"(1) Missed one attack during a blacklist war against `{clan}`; we lost, but met the conditional.")
                        players[i].num_strikes += 1

                    elif conditional == 'n' and win == 'y' and num == 2:
                        players[i].strikes.append(f"(2) Missed two attacks during a blacklist war against `{clan}`; but we won.")
                        players[i].num_strikes += 2

                    elif conditional == 'n' and win == 'y' and num == 1:
                        continue

                    elif conditional == 'n' and win == 'n' and num == 2:
                        players[i].strikes.append(f"(5) Missed two attacks during a blacklist war against `{clan}`; and we lost.")
                        players[i].num_strikes += 5

                    elif conditional == 'n' and win == 'n' and num == 1:
                        players[i].strikes.append(f"(2) Missed one attack during a blacklist war against `{clan}`; and we lost.")
                        players[i].num_strikes += 2

                    else:
                        print('Invalid input entered. No strike will be awarded.')
                        return
                    
                elif sel == 4: 
                    clan = input('Enter name of opponent blacklist clan: ')
                    conditional = input("Did we meet the conditional for reduced strikes? Y/N: ").lower()

                    if conditional == 'y': 
                        players[i].strikes.append(f"(1) Failed to set war base during battle day against `{clan}`; we lost, but met the conditional.")
                        players[i].num_strikes += 1

                    elif conditional == 'n':
                        players[i].strikes.append(f"(3) Failed to set war base during battle day against `{clan}`; and we lost.")
                        players[i].num_strikes += 3

                elif sel == 5: 
                    clan = input('Enter name of opponent clan when this player had a war base: ')
                    sanctions = input('Did sanctions result due to this player having a war base? Y/N: ').lower()

                    if sanctions == 'y': 
                        players[i].strikes.append(f"(5) Had war base during battle day against `{clan}`, and sanctions resulted from it.")
                        players[i].num_strikes += 5

                    elif sanctions == 'n': 
                        players[i].strikes.append(f"(3) Had war base during battle day against `{clan}`.")
                        players[i].num_strikes += 3
                    else: 
                        print('Invalid input entered. No strike will be awarded.')
                        return
                    
                elif sel == 6: 
                    num_errors = input('How many base errors did this player have? ')
                    try: num_errors = int(num_errors)
                    except: num_errors = 0

                    if num_errors <= 0: 
                        print('Either this player had no base errors, or something went wrong. No strike will be awarded. ')
                        return
                    
                    if num_errors < 5: 
                        players[i].strikes.append('(0.5) Had 4 or less base errors')
                        players[i].num_strikes += 0.5

                    else: 
                        players[i].strikes.append('(1) Had 5 or more base errors')
                        players[i].num_strikes += 1

                elif sel == 7: 
                    print('What kind of instruction did this player not follow? ')
                    print('[1] Three-starred during a loss war')
                    print('[2] Sniped for more than 2 stars during a win war')
                    print('[3] Sniped for more than 1 star during a loss war')
                    print('[4] Attacked someone else than mirror')
                    sel = input('Selection: ')
                    try: sel = int(sel)
                    except: sel = 0

                    if sel == 0: 
                        print('Invalid input entered. No strike will be awarded.')
                        print('')

                    elif sel == 1: 
                        clan = input('Enter opponent clan name for when this player three-starred during a loss war: ')
                        players[i].strikes.append(f"(0.5) Three-starred during a loss war against `{clan}`.")
                        players[i].num_strikes += 0.5

                    elif sel == 2: 
                        clan = input('Enter opponent clan name for when this player sniped for more than 2 stars during a win war: ')
                        players[i].strikes.append(f"(0.5) Sniped for more than 2 stars during a win war against `{clan}`.")
                        players[i].num_strikes += 0.5

                    elif sel == 3: 
                        clan = input('Enter opponent clan name for when this player sniped for more than 1 star during a loss war: ')
                        players[i].strikes.append(f"(0.5) Sniped for more than 1 star during a loss war against `{clan}`.")
                        players[i].num_strikes += 0.5

                    elif sel == 4:
                        clan = input('Enter opponent clan name for when this player attacked someone else than mirror: ')
                        clan = clan.split("#")[0]
                        players[i].strikes.append(f"(0.5) Attacked someone else than mirror during a war against `{clan}`.")
                        players[i].num_strikes += 0.5
                                    
                elif sel == 8: 
                    clan = input('Enter opponent clan name who initiated sanctions against us: ')
                    players[i].strikes.append(f"(1) Repeat offender in sanctions during war against `{clan}`.")
                    players[i].num_strikes += 1

                elif sel == 9: 
                    clan = input('Enter opponent clan name for when this player disobeyed instructions: ')
                    message = input('Enter strike message here. Use <clan> to substitute the opponent clan name: ')
                    message = message.split('<clan>')
                    if len(message) == 1: message = message[0]
                    else: message = clan.join(message)
                    n = input('How many strikes is this worth? ')
                    try: n = float(n)
                    except: n = 0
                    if n == 0: 
                        print('Invalid number of strikes entered. No strikes will be awarded.')
                        return
                    elif n > 5: 
                        print('A strike can\'t be worth more than 5 strikes! No strikes will be awarded.')
                        return
                    else: 
                        players[i].strikes.append(f"({n}): {message}")
                        players[i].num_strikes += n
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
                    if players[i].strikes[num-1].startswith('(1) Missed hits during war'): 
                        clan = players[i].strikes[num-1][36:-2]
                        print(f"Clan to remove: {clan}")
                        for j in range(len(players[i].missed_hit_clans)): 
                            if players[i].missed_hit_clans[j] == clan: 
                                print(f"Found clan: {clan}")
                                players[i].missed_hit_clans.pop(j)
                                players[i].missed_hit_dates.pop(j)

                                if num != len(players[i].strikes):
                                    if players[i].strikes[num].startswith('(1) Missed hits in two consecutive wars'): 
                                        players[i].num_strikes -= 1
                                        players[i].strikes.pop(num)
                    float_val = re.search(r"\((\d.\d)\)", players[i].strikes[num-1])
                    int_val = re.search(r"\((\d)\)", players[i].strikes[num-1])

                    if float_val: val = float(float_val.group(1))
                    elif int_val: val = int(int_val.group(1))

                    players[i].num_strikes -= val
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
                players[i].num_strikes = 0
                players[i].strikes = []
                players[i].missed_hit_clans = []
                players[i].missed_hit_dates = []
                return
            
    if not found: 
        print(f"No such player with name {name} exists.")

def clear_strikes():
    confirm = input('Are you sure you want to clear all strikes? This cannot be undone. Y/N: ').lower()
    if confirm == 'y': 
        for i in range(len(players)): 
            players[i].num_strikes = 0
            players[i].strikes = []
            players[i].missed_hit_clans = []
            players[i].missed_hit_dates = []

def output_strikes():
    with open('strikes.txt', 'w', encoding="utf-8") as file: 
        xray_printed = False 
        outlaws_printed = False

        for i in range(len(players)): 
            if players[i].clan != "Reddit X-ray": continue
            if players[i].num_strikes != 0: 
                # If the player's strikes are an integer value, round it. 
                if players[i].num_strikes == int(players[i].num_strikes):
                    players[i].num_strikes = int(players[i].num_strikes)
                
                if not xray_printed:
                    file.write('**Reddit X-ray**:\n\n')
                    xray_printed = True
                    
                file.write(f"[{players[i].num_strikes}] {players[i].name} #{players[i].tag}:\n")

                for j in range(len(players[i].strikes)): 
                    file.write(f"- {players[i].strikes[j]}\n")

                file.write('\n')

        for i in range(len(players)): 
            if players[i].clan != "Faint Outlaws": continue
            if players[i].num_strikes != 0: 
                if not outlaws_printed:
                    file.write('**Faint Outlaws**:\n\n')
                    outlaws_printed = True
                    
                file.write(f"[{players[i].num_strikes}] {players[i].name} #{players[i].tag}:\n")

                for j in range(len(players[i].strikes)): 
                    file.write(f"- {players[i].strikes[j]}\n")

                file.write('\n')

players = import_pickle()
while(True): 
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
    if sel == 1: add_player("xray"); add_player("outlaws")
    elif sel == 2: remove_player()
    elif sel == 3: add_strike()
    elif sel == 4: remove_strike()
    elif sel == 5: remove_all_strikes()
    elif sel == 6: clear_strikes()
    elif sel == 7: output_strikes()
    elif sel == 9: break

    if sel != 9: 
        players.sort(key = lambda x: (-x.num_strikes, x.name))
        print('')

    else: break