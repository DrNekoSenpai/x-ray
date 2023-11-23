players = []

while(True): 
    name = input("Enter player name: ")
    clan = "MINI LORDS"
    date = "1121"
    if name == "": break
    players.append([name, clan, date])

for player in players: 
    name, clan, date = player
    print(f"3\n{name}\ny\n1\n{clan}\n{date}")