import os, re
from datetime import datetime, timedelta

# Permanent immunities are players who are members of Leadership as well as known alts; they cannot be kicked. 
permanent_immunities = [ 
    "Sned",
    "Sned 2.0",
    "Sned 3.0",
    "Sned 4.0",
    "BumblinMumbler",
    "BumblinMumbler2",
    "BumblinMumbler3",
    "Ascended", 
    "Smitty™", 
    "Ligma", 
    "Sugma", 
    "CrazyWaveIT", 
    "LOGAN911", 
    "skyeshade", 
    "Golden Unicorn✨"
]

for filename in os.listdir("./logs/sanctions/"):
    with open(f"./logs/sanctions/{filename}", "r", encoding="utf-8") as file: 
        sanctions = file.read().splitlines()

    date = datetime.strptime(sanctions[2], "%b %d %Y").strftime("%Y-%m-%d")
    if datetime.strptime(sanctions[2], "%b %d %Y") < datetime.now() - timedelta(days=60): continue

    enemy_clan = None

    # Open the logs folder and find the corresponding war. It might not be the exact same date, but we should look up to two days backwards. 
    for war in os.listdir("./logs/"): 
        date_pattern = re.compile(r"\d{4}_\d{2}_\d{2}")

        war_date = date_pattern.search(war)
        if not war_date: continue

        if timedelta(days=2) >= datetime.strptime(sanctions[2], "%b %d %Y") - datetime.strptime(war_date.group(), "%Y_%m_%d") >= timedelta(days=0):
            print(f"Found war on {war_date.group()}")
            # Open the corresponding filename and find the name of the clan we faced. 
            enemy_clan_pattern = re.compile(r"War with #[A-Z0-9]{5,9} ‭⁦(.*)⁩‬ starts in \d+ minutes.")

            with open(f"./logs/{war}", "r", encoding="utf-8") as file: 
                for line in file: 
                    match = enemy_clan_pattern.match(line)
                    if match: 
                        print(f"Found enemy clan: {match.group(1)}")
                        enemy_clan = match.group(1)
                        break
                else: 
                    print("No enemy clan found.")
                    break
        
    # Points: 16
    points_pattern = re.compile(r"Points:\s+(\d+)")
    num_points = points_pattern.search(sanctions[-1])

    if not num_points: continue
    sanction_value = (int(num_points.group(1)) - 6) // 3
    
    if sanction_value < 1: continue
    elif sanction_value > 3: sanction_value = 3

    sanction_pattern_1 = re.compile(r"#\d+\.\s+(?P<name>[^:]+):(?P<reason>.*?)(?P<symbol>❌|🔥|☠️)")
    sanction_pattern_2 = re.compile(r"#\d+\s+(?P<name>[^-]+)\s+-(?P<reason>.*?)(?P<symbol>❌|🔥|☠️)")

    with open(f"./inputs/sanctions_{filename}", "w", encoding="utf-8") as file:
        for sanction in sanctions:
            match = sanction_pattern_1.match(sanction)
            if not match: match = sanction_pattern_2.match(sanction)
            if not match: continue

            if match.group("name") in permanent_immunities: continue 

            player_name = match.group("name").strip()
            reason = match.group("reason").strip()
            symbol = match.group("symbol").strip()

            if symbol == "❌":
                file.write(f"3\n{match.group('name')}\ny\n4\n{date}\n{enemy_clan}\nn\n")

            elif symbol == "🔥":
                file.write(f"3\n{match.group('name')}\ny\n4\n{date}\n{enemy_clan}\ny\n")

            elif symbol == "☠️":
                file.write(f"3\n{match.group('name')}\ny\n3\n{date}\n{enemy_clan}\n{sanction_value}\n")