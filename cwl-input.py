with open("cwl-input.txt", "r", encoding="utf-8") as f:
    lines = [f.strip() for f in f.readlines()]
    players = {}
    for f in lines:
        try: 
            name = f.rsplit(" ", 1)[0]
            hits = int(f.rsplit(" ", 1)[1])
            print(f"{f.rsplit(' ', 1)[0]} used {hits} hits")
        except:
            name = f
            hits = int(input(f"How many hits did player '{f}' use? "))

        players[name] = hits

with open("cwl-input.txt", "w", encoding="utf-8") as f:
    for name, hits in players.items():
        f.write(f"{name} {hits}\n")