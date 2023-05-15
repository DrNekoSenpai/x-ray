import pickle
import datetime

class player():
    def __init__(self, name, tag):
        self.name = name
        self.tag = tag
        self.num_strikes = 0
        self.strikes = []
        self.missed_hit_clans = []
        self.missed_hit_dates = []
        self.immune = False

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
                if players[i].immune: 
                    print('This player is immune to strikes! No strike will be awarded.')
                    return
                print('')
                print('What kind of strike is this?')
                print('[1] Missed FWA attack')
                print('[2] CWL attacks')
                print('[3] Blacklist attacks')
                print('[4] War base')
                print('[5] Base errors')
                print('[6] Directions not followed')
                print('[7] No league badge')
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
                    players[i].strikes.append('(1) Missed hits during war against `%s`.' % clan)
                    players[i].num_strikes += 1
                    if len(players[i].missed_hit_dates) != 1: 
                        this_war = len(players[i].missed_hit_dates) - 1
                        previous_war = len(players[i].missed_hit_dates) - 2
                        if players[i].missed_hit_dates[previous_war] + 3 >= players[i].missed_hit_dates[this_war]: 
                            players[i].strikes.append('(1) Missed hits in two consecutive wars against `%s` and `%s`.' % (players[i].missed_hit_clans[previous_war], players[i].missed_hit_clans[this_war]))
                            players[i].num_strikes += 1
                elif sel == 2: 
                    num_wars = input('How many hits did this player miss? ')
                    try: num_wars = int(num_wars)
                    except: num_wars = 0
                    if num_wars < 0: print('Either this player missed no hits, or something went wrong. No strike will be awarded.')
                    elif num_wars < 3: print('This player hasn\'t missed enough wars to be awarded strikes!')
                    elif num_wars < 5: 
                        players[i].strikes.append('(1) Missed 3 or 4 hits during CWL week.')
                        players[i].num_strikes += 1
                    elif num_wars < 7: 
                        players[i].strikes.append('(2) Missed 5 or 6 hits during CWL week.')
                        players[i].num_strikes += 2
                    elif num_wars == 7: 
                        players[i].strikes.append('(3) Missed 7 hits during CWL week.')
                        players[i].num_strikes += 3
                    else: 
                        print('Invalid number of hits entered. No strike will be awarded.')
                        return
                elif sel == 3: 
                    clan = input('Enter name of opponent blacklist clan: ')
                    win = input('Did we win? Y/N: ').lower()
                    if win == 'y': 
                        players[i].strikes.append('(2) Missed one or more attacks during a blacklist war against `%s`, but we won.' % clan)
                        players[i].num_strikes += 2
                    elif win == 'n': 
                        players[i].strikes.append('(5) Missed one or more attacks during a blacklist war against `%s`, and cost us the victory.' % clan)
                        players[i].num_strikes += 5
                    else: 
                        print('Invalid input entered. No strike will be awarded.')
                        return
                elif sel == 4: 
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
                elif sel == 5: 
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
                elif sel == 6: 
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
                elif sel == 7: 
                    current_month = datetime.datetime.now().strftime('%B')
                    deadline = input('Is this the 24 or the 48 hour deadline? ')
                    try: deadline = int(deadline)
                    except: deadline = 0
                    if deadline == 24: 
                        message = 'Failed to obtain league badge 24 hours after %s CWL ended.' % current_month
                        players[i].strikes.append('(1) %s' % message)
                        players[i].num_strikes += 1
                    elif deadline == 48: 
                        message = 'Failed to obtain league badge 48 hours after %s CWL ended.' % current_month
                        players[i].strikes.append('(2) %s' % message)
                        players[i].num_strikes += 2
                    else: 
                        print('Invalid input entered. No strikes will be awarded.')
                        return
                elif sel == 8: 
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

def immune(): 
    name = input('Enter name of player to immune / de-immune: ')
    if name == '': return
    found = False
    for i in range(len(players)): 
        if players[i].name.lower().startswith(name.lower()): 
            found = True
            players[i].output()
            confirm = input('Is this the right player? Y/N ').lower()
            if confirm == 'y' or confirm == 'yes': 
                if players[i].immune: 
                    print('This player is no longer immune to strikes.')
                    players[i].immune = False
                else: 
                    print('This player is now immune to strikes.')
                    players[i].immune = True

players = import_pickle()
while(True): 
    print('---- Reddit X-ray Strike Automation System ----')
    print('[1] Add a new player')
    print('[2] Remove a player')
    print('[3] Award a strike')
    print('[4] Remove a strike')
    print('[5] Clear all strikes for a given player')
    print('[6] Reset all strikes')
    print('[7] Output strikes list')
    print('[8] Immune / de-immune a player')
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
    elif sel == 8: immune()
    if sel != 9: 
        players.sort(key = lambda x: (-x.num_strikes, x.name))
        print('')
    else: break