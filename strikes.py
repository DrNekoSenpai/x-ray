import pickle
import datetime
import argparse

class player():
    def __init__(self, name, tag):
        self.name = name
        self.tag = tag
        self.num_strikes = 0
        self.strikes = []
        self.missed_hit_clans = []
        self.missed_hit_dates = []

    def output(self): 
        print('Name         : %s' % self.name)
        print('Tag          : %s' % self.tag)
        print('# of strikes : %i' % self.num_strikes)
        if self.num_strikes != 0: 
            for i in range(len(self.strikes)):
                print('- %s' % self.strikes[i])

def export_pickle(): 
    with open('player_data.pickle', 'wb') as f:
        pickle.dump(players, f)

def import_pickle(): 
    try: 
        with open('player_data.pickle', 'rb') as f: 
            players = pickle.load(f)
    except: players = []
    return players

# Create an argparse argument. By default, we will use command line (manual) entry. 
# If the user specifies a file, we will use that instead.
# Command line is easier to use, but is more tedious and slower to use. 
# File input is faster, but requires the user to create a file with the correct format. This might result in more errors, so this should only be used by experienced users.
parser = argparse.ArgumentParser(description='Process strikes.')
parser.add_argument('-m', '--mode', type=str, default='manual', help='Mode to use. Can be manual or file.')
parser.add_argument('-f', '--file', type=str, default='strikes_input.csv', help='File to use. Only used if mode is file.')
parser.add_argument("--debug", "-d", help="Enable debug mode.", action="store_true")
args = parser.parse_args()

import requests
import datetime

def up_to_date(): 
    # Get repository details from the GitHub API.
    url = "https://api.github.com/repos/DrNekoSenpai/x-ray"
    response = requests.get(url)
    data = response.json()

    # Get the date of the latest commit.
    last_commit_date = datetime.datetime.strptime(data['pushed_at'], "%Y-%m-%dT%H:%M:%SZ")

    # Grab the current date, and adjust for UTC time. 
    current_date = datetime.datetime.utcnow()

    if args.debug: 
        print("Last commit date", last_commit_date)
        print("Current date", current_date)

    return last_commit_date < current_date

if not up_to_date():
    print("Error: the local repository is not up to date. Please pull the latest changes before running this script.")
    print("To pull the latest changes, simply run the command 'git pull' in this terminal.")
    exit(1)

if args.debug:
    print("The local repository is up to date.")

players = import_pickle()

def add_player(): 
    """Add a new player to the database, provided that they do not already exist."""
    in_str = input('Enter name and tag, separated by spaces: ').strip()
    if in_str == '': return
    in_str = in_str.rsplit(' ', 1)
    for i in range(len(players)): 
        if players[i].name.lower().startswith(in_str[0].lower()): 
            print('This player already exists! Duplicates are not allowed.')
            return
    p = player(in_str[0], in_str[1].upper())
    players.append(p)
	
def remove_player(): 
    """Given an existing player in the database, remove them from the database."""
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
    if not found: print('No such player with name %s exists.' % name.lower())
	
def add_strike(): 
    name = input('Enter name of player to award a strike to: ')
    if name == '': return
    found = False
    for i in range(len(players)): 
        if players[i].name.lower().startswith(name.lower()): 
            found = True
            players[i].output()
            confirm = input('Is this the right player? Y/N: ').lower()
            if confirm == 'y' or confirm == 'yes': 
                print('')
                print('What kind of strike is this?')
                print('[1] Missed FWA attack')
                print('[2] CWL attacks')
                print('[3] Blacklist attacks')
                print('[4] FWA base during blacklist war')
                print('[5] War base')
                print('[6] Base errors')
                print('[7] Directions not followed')
                print('[8] Repeat offender in sanctions')
                print('[9] Other')
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
                    players[i].strikes.append('(1) Missed hits during war against `%s`.' % clan)
                    players[i].num_strikes += 1
                    if len(players[i].missed_hit_dates) != 1: 
                        this_war = len(players[i].missed_hit_dates) - 1
                        previous_war = len(players[i].missed_hit_dates) - 2
                        if players[i].missed_hit_dates[previous_war] + 3 >= players[i].missed_hit_dates[this_war]: 
                            players[i].strikes.append('(1) Missed hits in two consecutive wars against `%s` and `%s`.' % (players[i].missed_hit_clans[previous_war], players[i].missed_hit_clans[this_war]))
                            players[i].num_strikes += 1
                elif sel == 2: 
                    confirm = input('Please confirm you wish to award CWL strikes to this player. Y/N: ').lower()
                    if confirm != 'y' and confirm != 'yes': return
                    players[i].strikes.append('(1) Missed 4 or more hits during CWL week.')
                    players[i].num_strikes += 1
                elif sel == 3: 
                    clan = input('Enter name of opponent blacklist clan: ')
                    win = input('Did we win? Y/N: ').lower()
                    num = int(input("How many hits did this player miss? "))
                    if win == 'y' and num == 2: 
                        players[i].strikes.append('(2) Missed two attacks during a blacklist war against `%s`, but we won.' % clan)
                        players[i].num_strikes += 2
                    elif win == 'n' and num == 2: 
                        players[i].strikes.append('(5) Missed two attacks during a blacklist war against `%s`, and cost us the victory.' % clan)
                        players[i].num_strikes += 5
                    elif win == 'n' and num == 1: 
                        players[i].strikes.append('(2) Missed one attack during a blacklist war against `%s`, and cost us the victory.' % clan)
                        players[i].num_strikes += 2
                    else: 
                        print('Invalid input entered. No strike will be awarded.')
                        return
                elif sel == 4: 
                    clan = input('Enter name of opponent blacklist clan: ')
                    win = input('Did we win? Y/N: ').lower()
                    if win == "n": 
                        players[i].strikes.append('(3) Had FWA base during a blacklist war against `%s`, and cost us the victory.' % clan)
                        players[i].num_strikes += 3
                elif sel == 5: 
                    clan = input('Enter name of opponent clan when this player had a war base: ')
                    sanctions = input('Did sanctions result due to this player having a war base? Y/N: ').lower()
                    if sanctions == 'y': 
                        players[i].strikes.append('(5) Had war base during battle day against `%s`, and sanctions resulted from it.' % clan)
                        players[i].num_strikes += 5
                    elif sanctions == 'n': 
                        players[i].strikes.append('(3) Had war base during battle day against `%s`.' % clan)
                        players[i].num_strikes += 3
                    else: 
                        print('Invalid input entered. No strike will be awarded.')
                        return
                elif sel == 6: 
                    num_errors = input('How many base errors did this player have? ')
                    try: num_errors = int(num_errors)
                    except: num_errors = 0
                    if num_errors == 0: 
                        print('Either this player had no base errors, or something went wrong. No strike will be awarded. ')
                        return
                    if num_errors < 5: 
                        players[i].strikes.append('(1) Had 4 or less base errors')
                        players[i].num_strikes += 1
                    else: 
                        players[i].strikes.append('(2) Had 5 or more base errors')
                        players[i].num_strikes += 2
                elif sel == 7: 
                    print('What kind of instruction did this player not follow? ')
                    print('[1] Three-starred during a loss war')
                    print('[2] Sniped for more than 2 stars during a win war')
                    print('[3] Sniped for more than 1 star during a loss war')
                    sel = input('Selection: ')
                    try: sel = int(sel)
                    except: sel = 0
                    if sel == 0: 
                        print('Invalid input entered. No strike will be awarded.')
                        print('')
                    elif sel == 1: 
                        clan = input('Enter opponent clan name for when this player disobeyed instructions: ')
                        players[i].strikes.append('(1) Three-starred during a loss war against `%s`.' % clan)
                        players[i].num_strikes += 1
                    elif sel == 2: 
                        clan = input('Enter opponent clan name for when this player disobeyed instructions: ')
                        players[i].strikes.append('(1) Sniped for more than 2 stars during a win war against `%s`.' % clan)
                        players[i].num_strikes += 1
                    elif sel == 3: 
                        clan = input('Enter opponent clan name for when this player disobeyed instructions: ')
                        players[i].strikes.append('(1) Sniped for more than 1 star during a loss war against `%s`.' % clan)
                        players[i].num_strikes += 1
                elif sel == 8: 
                    clan = input('Enter opponent clan name who initiated sanctions against us: ')
                    players[i].strikes.append('(1) Repeat offender in sanctions during war against `%s`.' % clan)
                    players[i].num_strikes += 1
                elif sel == 9: 
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
                        players[i].strikes.append('(%i) %s' % (n, message))
                        players[i].num_strikes += n
                return
    if not found: print('No such player with name %s exists.' % name)
	
def remove_strike():
    name = input('Enter name of player to remove a strike from: ')
    if name == '': return
    found = False
    for i in range(len(players)): 
        if players[i].name.lower().startswith(name.lower()): 
            found = True
            players[i].output()
            confirm = input('Is this the right player? Y/N ').lower()
            if confirm == 'y' or confirm == 'yes': 
                for j in range(len(players[i].strikes)):
                    print('%i) ' % (j+1) + players[i].strikes[j])
                num = input('Which strike needs to be removed? ')
                try: num = int(num)
                except: num = 0
                if num == 0: 
                    print('Invalid selection entered. No strike will be removed.')
                    return
                else: 
                    if players[i].strikes[num-1].startswith('(1) Missed hits during war'): 
                        clan = players[i].strikes[num-1][36:-2]
                        print('Clan to remove: %s' % clan)
                        for j in range(len(players[i].missed_hit_clans)): 
                            if players[i].missed_hit_clans[j] == clan: 
                                print('Found clan: %s' % clan)
                                players[i].missed_hit_clans.pop(j)
                                players[i].missed_hit_dates.pop(j)

                                if num != len(players[i].strikes):
                                    if players[i].strikes[num].startswith('(1) Missed hits in two consecutive wars'): 
                                        players[i].num_strikes -= 1
                                        players[i].strikes.pop(num)
                    val = int(players[i].strikes[num-1][1])
                    players[i].num_strikes -= val
                    players[i].strikes.pop(num-1)
                return
    if not found: print('No such player with name %s exists.' % name)
	
def remove_all_strikes(): 
    name = input('Enter name of player to remove all strike from: ')
    if name == '': return
    found = False
    for i in range(len(players)): 
        if players[i].name.lower().startswith(name.lower()): 
            found = True
            players[i].output()
            confirm = input('Is this the right player? Y/N ').lower()
            if confirm == 'y' or confirm == 'yes': 
                players[i].num_strikes = 0
                players[i].strikes = []
                players[i].missed_hit_clans = []
                players[i].missed_hit_dates = []
                return
    if not found: print('No such player with name %s exists.' % name)

def clear_strikes():
    confirm = input('Are you sure you want to clear all strikes? This cannot be undone. Y/N: ').lower()
    if confirm == 'y': 
        for i in range(len(players)): 
            players[i].num_strikes = 0
            players[i].strikes = []

def regular_keyboard(input_string): 
    pattern = r"^[A-Za-z0-9 !@#$%^&*()\-=\[\]{}|;:'\",.<>/?\\_+]*$"
    return re.match(pattern, input_string) is not None 

players = import_pickle()
while(args.mode == 'manual'): 
    print('---- Reddit X-ray Strike Automation System ----')
    print('[1] Add a new player')
    print('[2] Remove a player')
    print('[3] Award a strike')
    print('[4] Remove a strike')
    print('[5] Clear all strikes for a given player')
    print('[6] Reset all strikes')
    print('[7] Output strikes list')
    print('[8] Mass import from Minion Bot \'/clan villages search\' command')
    print('[9] Exit')
    sel = input('Selection: ')
    try: sel = int(sel)
    except: sel = 0
    export_pickle()
    if sel != 9: print('')
    if sel == 1: add_player()
    elif sel == 2: remove_player()
    elif sel == 3: add_strike()
    elif sel == 4: remove_strike()
    elif sel == 5: remove_all_strikes()
    elif sel == 6: clear_strikes()
    elif sel == 7: 
        with open('strikes.txt', 'w') as file: 
            for i in range(len(players)): 
                if players[i].num_strikes != 0: 
                    file.write('[%i] %s #%s:\n' % (players[i].num_strikes, players[i].name, players[i].tag))
                    print('[%i] %s #%s:' % (players[i].num_strikes, players[i].name, players[i].tag))

                    for j in range(len(players[i].strikes)): 
                        file.write('- %s\n' % (players[i].strikes[j]))
                        print('- %s' % (players[i].strikes[j]))

                    file.write('\n')
                    print('')
    elif sel == 8: 
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
        import os 
        import re

        if not os.path.isfile('minion.txt'):
            print('No file named "minion.txt" exists in the current directory.')
            continue

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

    if sel != 9: 
        players.sort(key = lambda x: (-x.num_strikes, x.name))
        print('')
    else: break