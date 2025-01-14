import os, re
from datetime import datetime, timedelta

for filename in os.listdir("./logs/sanctions/"):
    with open(f"./logs/sanctions/{filename}", "r", encoding="utf-8") as file: 
        sanctions = file.read().splitlines()

    # #2. Satan: firespitters overlapping dark spell factory and dark elixir storage and Bob's hut and workshop❌️

    # Line 3; Dec 17 2024
    # strftime to %Y-%m-%d format

    date = datetime.strptime(sanctions[2], "%b %d %Y").strftime("%Y-%m-%d")

    # Incorrect bases: 20❌
    # Hot Mess Bases: 00🔥
    # War Bases: 00☠️

    # We want to match a line with one of these symbols and categorize based on the symbol found. The text isn't important. 
    # We only need to extract the name and symbol found. Nothing else is important, including the reason. 

    # #2. Satan: firespitters overlapping dark spell factory and dark elixir storage and Bob's hut and workshop❌️
    # #42. Rising Unicorn✨: war base☠️

    enemy_clan = None

    # Open the logs folder and find the corresponding war. It might not be the exact same date, but we should look up to two days backwards. 
    for war in os.listdir("./logs/"): 
        date_pattern = re.compile(r"\d{4}_\d{2}_\d{2}")
        # Go through each war and see if it is within two days of the date, one-directional. 
        # For example, if the sanction date is 2024-12-17, we should look for wars on 2024-12-17, 2024-12-16, and 2024-12-15.
        war_date = date_pattern.search(war)
        if not war_date: continue

        if timedelta(days=2) >= datetime.strptime(war_date.group(), "%Y_%m_%d") - datetime.strptime(sanctions[2], "%b %d %Y") >= timedelta(days=-2):
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

    sanction_pattern = re.compile(r"#\d+\.\s+(?P<name>[^:]+):.*?(?P<symbol>❌|🔥|☠️)")

    permanent_immunities = [ 
        "Sned",
        "Sned 2.0",
        "Sned 3.0",
        "Sned 4.0",
        "BumblinMumbler",
        "BumblinMumbler2",
        "BumblinMumbler3",
        "Arcohol",
        "bran6", 
        "katsu", 
        "K.L.A.U.S v2",
        "Marlec", 
        "Ascended", 
        "Smitty™", 
        "Ligma", 
        "Sugma"
    ]

    with open(f"./inputs/sanctions_{filename}", "w", encoding="utf-8") as file:
        for sanction in sanctions:
            match = sanction_pattern.match(sanction)

            if not match: continue
            if match.group("name") in permanent_immunities: continue 

            if match.group("symbol") == "❌":
                file.write(f"3\n{match.group('name')}\ny\n4\n{date}\nn\n{enemy_clan}\n")

            elif match.group("symbol") == "🔥":
                file.write(f"3\n{match.group('name')}\ny\n4\n{date}\ny\n{enemy_clan}\n")

            elif match.group("symbol") == "☠️":
                file.write(f"3\n{match.group('name')}\ny\n3\n{date}\n{enemy_clan}\n")