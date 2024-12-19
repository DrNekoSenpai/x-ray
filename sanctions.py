with open("sanctions.txt", "r", encoding="utf-8") as file: 
    sanctions = file.read().splitlines()

import re

# #2. Satan: firespitters overlapping dark spell factory and dark elixir storage and Bob's hut and workshop❌️

sanction_pattern = re.compile(r"#\d+\.\s(?P<name>.*):\s(?P<reason>.*)❌️")

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

with open(f"./inputs/sanctions.txt", "w", encoding="utf-8") as file:
    for sanction in sanctions:
        match = sanction_pattern.match(sanction)
        if not match: continue
        if match.group("name") in permanent_immunities: continue 
        else: 
            file.write(f"3\n{match.group('name')}\ny\n6\n{match.group('reason')}\n")