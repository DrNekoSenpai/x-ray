# Define a class called Strike; this is a simple data structure containing of a string and an integer. 
# The string is the message for the strike; and the integer is how many strikes it's worth. 
class Strike:
    def __init__(self, message, value): 
        self.message = message
        self.value = value

# Define a class called Player; this is a data structure containing a player's name, tag, and a list of Strikes.
class Player:
    def __init__(self, name, tag): 
        self.name = name
        self.tag = tag
        self.strikes = []

    # We'll add a function to add a strike to the player's list of strikes. This will take in a message and a value; and then append a Strike object containing those values. 
    def add_strike(self, message, value):
        self.strikes.append(Strike(message, value))
    
    # We'll add a function to return the number of strikes a player has. We'll do this by summing up each of the strike values in the list of strikes.
    def get_num_strikes(self) -> int:
        total = 0
        for strike in self.strikes:
            total += strike.value
        return total

with open("strikes_input.csv", "r") as in_file: 
    in_lines = in_file.readlines()

players = []

for ind,line in enumerate(in_lines):
    line = line.strip()
    if ind == 0: continue 
    line = line.split(",")
    # First, we'll take the first two elements of the line, which are the player's name and tag.
    name = line[0]
    tag = line[1]
    # We'll check if there already exists a Player object with that tag. If there is, we'll use that Player object. If not, we'll create a new Player object.
    current_player = None
    for player in players:
        if player.tag == tag:
            current_player = player
            break
    
    if current_player == None:
        current_player = Player(name, tag)
        players.append(current_player)
    
    # We'll then take the next element, which is the strike category. 
    category = line[2].lower()
    if category == "missed hit": 
        # The third element is what kind of missed hit it was. It can either be; FWA, CWL, or blacklist. 
        missed_hit_type = line[3].lower()
        if missed_hit_type == "fwa":
            # The fourth element is the name of enemy clan; and the fifth element is the date the war ended on. 
            enemy_clan = line[4]
            month = line[5]
            day = line[6]
            # We'll then add a strike to the player's list of strikes. The message will be the enemy clan's name and the date the war ended on. The value will be 1.
            current_player.add_strike(f"Missed hit against {enemy_clan} on {month} {day}", 1)
            # We will check if the player has another missed hit strike; and if so, if the day is less than 3. If so, we'll add another strike.
            if len(current_player.strikes) > 1:
                # We'll loop through the list of strikes, and check if the strike message begins with "Missed hit against". 
                # If it does, we'll check if the date is less than 3 days apart. If so, we'll add another strike.
                for strike in current_player.strikes:
                    if strike.message.startswith("Missed hit against"):
                        # We'll take the name of the other clan from the strike message.
                        import re
                        # We'll search for a date in the format of "Month Day" in the strike message.
                        # This is an explicit search; so we'll search for January/February/March/April/May/June/July/August/September/October/November/December followed by a space, followed by a number.
                        # We'll then take the month and day from the strike message.
                        strike_month, strike_day = re.search(r"(January|February|March|April|May|June|July|August|September|October|November|December) (\d+)", strike.message).groups()

                        previous_enemy_clan = re.search(r"against (.*) on", strike.message).group(1)
                        # We need to check that the previous enemy clan is NOT the same as the current enemy clan.
                        if previous_enemy_clan == enemy_clan:
                            continue

                        # We'll check if the month is the same; and if the day is less than 3 days apart. 
                        if int(day) - int(strike_day) < 3:
                            current_player.add_strike(f"Missed hits in two consecutive wars against {enemy_clan} and {previous_enemy_clan}", 1)
        elif missed_hit_type == "cwl":
            # The fourth element is the current month; and the fifth element is the number of hits missed. 
            # The number of strikes this is worth is proportional to the number of hits missed.
            # 0-2 hits missed; none
            # 3-4 hits missed; 1 strike
            # 5-6 hits missed; 2 strikes
            # 7 hits missed; 3 strikes
            month = line[4]
            num_missed = int(line[5])
            if num_missed == 0 or num_missed == 1 or num_missed == 2:
                pass
            elif num_missed == 3 or num_missed == 4:
                current_player.add_strike(f"Missed {num_missed} hits during CWL week in {month}", 1)
            elif num_missed == 5 or num_missed == 6:
                current_player.add_strike(f"Missed {num_missed} hits during CWL week in {month}", 2)
            elif num_missed == 7:
                current_player.add_strike(f"Missed {num_missed} hits during CWL week in {month}", 3)
        elif missed_hit_type == "blacklist":
            pass
    elif category == "war base": 
        pass
    elif category == "base error":
        pass
    else: 
        print(f"Invalid entry: {line}")

# Finally, we'll sort the players by the number of strikes they have.
players.sort(key=lambda player: player.get_num_strikes(), reverse=True)

# We'll print out strikes in this format: 
# [Number of strikes total] Player name Player tag
# - (Number of strikes for this strike) [Strike message]
# Empty line

# Note that brackets / parentheses are literal and should be included. 

for player in players:
    print(f"[{player.get_num_strikes()}] {player.name} {player.tag}")
    for strike in player.strikes:
        print(f"- ({strike.value}) {strike.message}")
    print()