import os, re, datetime, argparse, pickle, time, json, pandas as pd
from dataclasses import dataclass
from datetime import date
from collections import defaultdict
from strikes import up_to_date

if up_to_date() is False:
    print("Error: the local repository is not up to date. Please pull the latest changes before running this script.")
    print("To pull the latest changes, simply run the command 'git pull' in this terminal.")
    exit(1)
    
# Immunities is a list of either player names only, or player names and dates. 
immunities = [
    # Permanent immunities are players who are members of Leadership as well as known alts; they cannot be kicked. 
    "Sned",
    "Sned 2.0",
    "BumblinMumbler",
    "BumblinMumbler2",
    "Ascended", 
    "Smitty™", 
    "Ligma", 
    "CrazyWaveIT", 
    "skyeshade"
]

parser = argparse.ArgumentParser(description="Analyze war logs for generating strikes.")
parser.add_argument("--bypass", "-b", action="store_true", help="If set to true, program also outputs bypass messages. Default: False")
parser.add_argument("--snipe", "-s", action="store_true", help="If set to true, program outputs snipe messages when bypass is also true. Default: False")
parser.add_argument("--debug", "-d", action="store_true", help="If set to true, program outputs log messages for immune players. Default: False")
parser.add_argument("--log", "-l", action="store_true", help="If set to true, program also outputs log messages. Default: False")
parser.add_argument("--mirrors", "-m", action="store_true", help="If set to true, program also outputs invalid mirror messages. Default: False")
parser.add_argument("--war", "-w", type=str, default="", help="If specified, only analyze the war log with the given name. Default: ''")
parser.add_argument("--update", "-u", action="store_true", help="If set to true, only update player activity logs and exit without analyzing wars. Default: False")
parser.add_argument("--inactivity", "-i", action="store_true", help="If set to true, only calculate inactivity and skip strikes entirely.")
args = parser.parse_args()

@dataclass
class Claim: 
    displayname: str
    username: str
    id: int
    name: str
    tag: str
    in_clan: bool = False
    is_main: bool = False

# Assert that "xray-members.xlsx" and "attack-log.xlsx" exist and their last edited timestamps are within 48 hours of each other
xray_path = "./inputs/xray-members.xlsx"
attack_log_path = "./inputs/attack-log.xlsx"
missed_hits_path = "./inputs/missed-hits.xlsx"

if not os.path.exists(xray_path):
    raise FileNotFoundError(f"Error: '{xray_path}' does not exist.")

if not os.path.exists(attack_log_path):
    raise FileNotFoundError(f"Error: '{attack_log_path}' does not exist.")

if not os.path.exists(missed_hits_path): 
    raise FileNotFoundError(f"Error: '{missed_hits_path}' does not exist.")

xray_mtime = os.path.getmtime(xray_path)
attack_log_mtime = os.path.getmtime(attack_log_path)
missed_hits_mtime = os.path.getmtime(missed_hits_path)

time_difference = abs(xray_mtime - attack_log_mtime)
if time_difference > 48 * 3600: 
    raise ValueError("Error: The last edited timestamps of 'xray-members.xlsx' and 'attack-log.xlsx' differ by more than 48 hours.")

time_difference = abs(xray_mtime - missed_hits_mtime)
if time_difference > 48 * 3600: 
    raise ValueError("Error: The last edited timestamps of 'xray-members.xlsx' and 'missed-hits.xlsx' differ by more than 48 hours.")

claims_dictionary = {}
xray_claims = pd.read_excel(xray_path, sheet_name=0)

for _, row in xray_claims.iterrows():
    claim_displayname = row['DisplayName']
    claim_username = row['Username']
    claim_id = int(row['ID'])
    claim_name = row['Name']
    claim_tag = row['Tag']
    claim_clan = row['Clan']

    if type(claim_name) is float: continue 

    # Remove unwanted characters from claim_name and claim_displayname

    try: 
        if "\\" in claim_name:
            claim_name = claim_name.replace("\\", "")
        if "\\" in claim_displayname:
            claim_displayname = claim_displayname.replace("\\", "")

    except Exception as e:
        print(f"Error processing claim: {claim_name} ({claim_username}) - {e}")
        exit(1)

    # Add the claim to the claims_dictionary
    if claim_username not in claims_dictionary:
        claims_dictionary[claim_username] = []
    claims_dictionary[claim_username].append(
        Claim(
            displayname=claim_displayname,
            username=claim_username,
            id=claim_id,
            name=claim_name,
            tag=claim_tag,
            in_clan=(claim_clan == "Reddit X-ray")
        )
    )

known_mains = ["Marlec", "Plantos"]

num_alts_xray = 0

for claimer in claims_dictionary: 
    for claim in claims_dictionary[claimer]:
        accounts_xray = [claim for claim in claims_dictionary[claimer] if claim.in_clan]
        num_accounts_xray = len(accounts_xray)

        known_main = False
        if num_accounts_xray > 1:
            for account in accounts_xray:
                if account.name in known_mains: 
                    account.is_main = True
                    known_main = True
                    break

        if known_main:
            claims_dictionary[claimer] = [account for account in accounts_xray if account.is_main] + [account for account in accounts_xray if not account.is_main]

        elif num_accounts_xray == 1: 
            main_account = accounts_xray[0]
            main_account.is_main = True

            claims_dictionary[claimer] = [main_account] + [claim for claim in claims_dictionary[claimer] if claim.tag != main_account.tag]

        else: 
            for account in accounts_xray:
                if account.name in known_mains: 
                    account.is_main = True
                    break

            else: 
                claims_dictionary[claimer] = [account for account in accounts_xray if account.is_main] + [account for account in accounts_xray if not account.is_main]

for claimer in claims_dictionary:
    for claim in claims_dictionary[claimer]: 
        if not claim.is_main and claim.in_clan: num_alts_xray += 1

# Sort the claims dictionary by the number of known alts ascending.
claims_dictionary = dict(sorted(claims_dictionary.items(), key=lambda item: len(item[1]), reverse=True))

with open("./outputs/claims_output.txt", "w", encoding="utf-8") as file:
    for claimer in claims_dictionary: 
        accounts_xray = [claim for claim in claims_dictionary[claimer] if claim.in_clan]
        num_accounts_xray = len(accounts_xray)

        if num_accounts_xray == 1: file.write(f"{claimer}: {num_accounts_xray} account in Reddit X-ray")
        else: file.write(f"{claimer}: {num_accounts_xray} accounts in Reddit X-ray")

        file.write("\n")
        
        for account in accounts_xray: 
            file.write(f"  - {account.name}")
            if account.is_main: file.write(" -- (main)")
            file.write("\n")

        file.write("\n")

class player_activity: 
    # We need; player name, player tag, total number of hits missed, and an array of which wars were missed.
    # We also need a value that says the last time this player was found in our roster. 
    def __init__(self, name:str, tag:str): 
        self.name = name
        self.tag = tag
        self.base_value = 0
        self.wars_missed = []
        # Set last seen to 14 days before today, so that we can catch any players who haven't been seen in a while.
        self.last_seen = f"{datetime.datetime.now() - datetime.timedelta(days=14):%Y-%m-%d}"
        self.banked_counter = []
        self.mirror_tolerance = 0
        self.wars_logged = [] # Same as banked counter, but is not wiped when the reset hits. 

try: 
    with open("activity_data.pickle", "rb") as file: 
        player_activity_dict = pickle.load(file)

except:
    # Assume no such file exists, create a new one. 
    print(f"Error: no such file 'activity_data.pickle' was found. Creating a new one.")
    player_activity_dict = {}

try: 
    with open("activity_data.pickle", "rb") as file: 
        player_activity_dict = pickle.load(file)
except FileNotFoundError:
    # Assume no such file exists, create a new one. 
    print(f"Error: no such file 'activity_data.pickle' was found. Creating a new one.")
    player_activity_dict = {}

for user in claims_dictionary: 
    # Only update their last seen date if they are in the clan.
    for claim in claims_dictionary[user]: 
        if not claim.in_clan: continue

        if claim.tag not in player_activity_dict:
            player_activity_dict[claim.tag] = player_activity(claim.name, claim.tag)

        player_activity_dict[claim.tag].last_seen = f"{datetime.datetime.now():%Y-%m-%d}"
        player_activity_dict[claim.tag].base_value = 0
        player_activity_dict[claim.tag].mirror_tolerance = 0

with open("./outputs/strikes.txt", "r", encoding="utf-8") as file: 
    strikes = file.readlines()
    strikes_pattern = re.compile(r"\[(\d+)\]\s+(.*)\s+(#[A-Z0-9]{5,9})")

    for strike in strikes: 
        if not re.search(strikes_pattern, strike): continue
        num_strikes, name, tag = re.search(strikes_pattern, strike).groups()

        if tag in player_activity_dict: 
            player_activity_dict[tag].base_value = int(num_strikes)

if args.update:
    with open("activity_data.pickle", "wb") as file: 
        pickle.dump(player_activity_dict, file)
    exit()


attack_log = pd.read_excel(attack_log_path, sheet_name=0)
attack_log["War Start Time"] = (
    pd.to_datetime(attack_log["War Start Time"], utc=True)
    .dt.tz_convert(None)     # drop UTC
    .dt.date                 # use only the date
)

unique_wars = attack_log[["Enemy Clan Name", "War Start Time"]].drop_duplicates()
unique_wars = list(unique_wars.itertuples(index=False, name=None))
# Drop any war that is older than 40 days old
current_date = datetime.datetime.now().date()
unique_wars = [
    (war, war_start) for war, war_start in unique_wars
    if (current_date - war_start).days <= 40
]

missed_hits_log = pd.read_excel(missed_hits_path, sheet_name=0)
missed_hits = {unique_war[0]: None for unique_war in unique_wars}
# missed_hits = {missed_hits_log["Enemy Clan"]: {missed_hits_log["Name"]: int(missed_hits_log["Missed"])}}
print(missed_hits)

accounts_in_clan = [player_activity_dict[player].name for player in player_activity_dict]
logs = [f"{war_start.strftime('%Y')}_{war_start.strftime('%m')}_{war_start.strftime('%d')}_{war.lower().replace(' ', '_')}" for war, war_start in unique_wars]

def get_war_status(enemy_clan, war_start):
    war_log_path = "./inputs/war-log.json"
    war_key = f"{war_start}"

    # Load existing war log if it exists
    if os.path.exists(war_log_path):
        with open(war_log_path, "r", encoding="utf-8") as file:
            war_log = json.load(file)
    else:
        war_log = {}

    # Check if the war status is already recorded
    if war_key in war_log: return war_log[war_key][0]

    # Query user for war status
    print(f"Status for war against '{enemy_clan}' on {war_start} not found.")
    winloss = input("Enter the war status (e.g., win, loss, mismatch, blacklist win, blacklist loss):").strip().lower()

    if "blacklist" in winloss: 
        conditional = input("Blacklist conditional (true/false): ").strip().lower()
        winloss = f"{winloss}/{conditional}"

    # Save the new status to the war log
    war_log[war_key] = (winloss, enemy_clan) 

    with open(war_log_path, "w", encoding="utf-8") as file:
        json.dump(war_log, file, indent=4)

    return winloss

for enemy_clan, war_start in unique_wars: 
    enemy_clan:str 
    war_start:datetime.datetime

    war_end_date = (war_start + datetime.timedelta(days=2)).strftime("%Y-%m-%d")
    if datetime.datetime.strptime(war_end_date, "%Y-%m-%d").date() > current_date: 
        print(f"War against {enemy_clan} ends in the future, skipping...")
        continue

    else: 
        print(f"\nWar against {enemy_clan}:")

    log = []
    invalid_mirror = []
    one_missed_hit = []
    two_missed_hits = []
    war_ids = []

    win_loss = get_war_status(enemy_clan, war_start)
    if "/" in win_loss: win_loss, conditional = win_loss.split("/")
    else: conditional = None

    if win_loss is None: 
        print(f"War against {enemy_clan} not recorded -- fix?")
        continue 

    for _, row in attack_log.iterrows(): 
        if row["Enemy Clan Name"] != enemy_clan: continue 
        if row["Name"] not in accounts_in_clan: continue 
        if abs((row["War Start Time"] - war_start).days) > 5: continue

        pname = row["Name"]
        attacker = row["Position"]
        defender = row["Defender Position"]
        stars = row["Stars"]
        attack_order = row["Attack Order"]

        log.append((pname, attacker, defender, stars, attack_order))
        war_ids.append(row.get("War ID", None))

    # Sort log by attack order ascending 
    log = sorted(log, key=lambda log: log[4])


    # Pull missed-hit info for this war from missed-hits.xlsx (by War ID).
    # Note: players who missed both hits may have *no* entries in `log`, so we use the missed-hits sheet.
    try:
        war_id = None
        war_ids_clean = [wid for wid in war_ids if pd.notna(wid)]
        if war_ids_clean:
            war_id = pd.Series(war_ids_clean).mode().iloc[0]

        if war_id is not None:
            mh_rows = missed_hits_log[missed_hits_log["War ID"] == war_id]

            # Build missed-hit lists using tags (more reliable than names)
            for _, mh_row in mh_rows.iterrows():
                missed = mh_row.get("Missed", 0)
                try:
                    missed = int(missed)
                except Exception:
                    continue

                tag = str(mh_row.get("Tag", "")).strip()
                if not tag:
                    continue
                if not tag.startswith("#"):
                    tag = "#" + tag

                # Prefer name from our roster (player_activity_dict) to avoid name-formatting mismatches.
                pname_mh = player_activity_dict[tag].name if tag in player_activity_dict else str(mh_row.get("Name", "")).strip()
                if not pname_mh:
                    continue

                if missed == 1:
                    one_missed_hit.append(pname_mh)
                elif missed >= 2:
                    two_missed_hits.append(pname_mh)

            # Deduplicate while preserving order
            one_missed_hit[:] = list(dict.fromkeys(one_missed_hit))
            two_missed_hits[:] = list(dict.fromkeys(two_missed_hits))
    except Exception as e:
        print(f"Warning: failed to ingest missed-hits.xlsx for war against {enemy_clan} on {war_start}: {e}")
    matches = [log_file for log_file in logs if enemy_clan.lower().replace(" ", "_") in log_file]

    if len(matches) == 1: log_file = matches[0]
    else: 
        war_start_dates = [datetime.datetime.strptime(log[:10], "%Y_%m_%d") for log in matches]
        date_distance = [abs((war_date.date() - war_start).days) for war_date in war_start_dates]
        idx = date_distance.index(min(date_distance))
        log_file = matches[idx]

    with open(f"./strikes/{log_file}.txt", "w", encoding="utf-8") as file: 
        rules_broken = {player_name: False for player_name in [entry[0] for entry in log]}
        player_entries = {player_name: [entry for entry in log if entry[0] == player_name] for player_name in [entry[0] for entry in log]}

        if win_loss in ["win", "loss"]: 
            snipe_count = {}
            rules_broken = {player_name: False for player_name in [entry[0] for entry in log]}

            # FWA war
            for entry in log: 
                player_name, attacker, defender, stars, attack_order = entry

                if defender is None: # Missed hit, skip for now 
                    continue

                if args.log: print(f"Player: {player_name}, Attacker: {attacker}, Defender: {defender}, Stars: {stars}")
                if args.mirrors: print(f"Invalid Mirrors: {invalid_mirror}")

                player_immune = False

                if player_name in immunities: 
                    player_immune = True

                if player_immune and not args.debug: 
                    invalid_mirror.append(defender)
                    continue 
                
                # Find the player in the player_activity_dict and check their mirror_tolerance value. 
                p = next((player_activity_dict[tag] for tag in player_activity_dict if player_activity_dict[tag].name == player_name), None)
                mirror_tolerance = p.mirror_tolerance if p else 0

                if attacker == defender: mirror = True
                else: 
                    tolerance = abs(int(attacker) - int(defender))
                    if tolerance <= 2 and mirror_tolerance == 0: 
                        mirror = True 
                        p.mirror_tolerance = 3
                    else: 
                        mirror = False 

                if mirror: 
                    # Check if the player three-starred their mirror on a loss.
                    if win_loss == "loss" and stars > 2:
                        print(f"Warning: {player_name} three-starred their mirror on a loss.")
                        file.write(f"3\n{player_name}\ny\n5\n{war_end_date}\n1\n{enemy_clan}\n")
                        rules_broken[player_name] = True

                    # Add this base to the invalid_mirror list, since it was taken by a mirror.
                    invalid_mirror.append(defender)

                    continue

                # If this is NOT a mirror, we do still need to check if they three-starred during a loss. 
                elif win_loss == "loss" and stars == 3: 
                    # Check if this player already hit their mirror. 
                    # If so, only penalize them for three-starring during a loss. 
                    # If not, check if they hit another base because their mirror was already taken. 
                    # If not, check if they hit another base because less than four hours remain in the war.
                    # If none of these are true, additionally penalize them for hitting a base not their mirror.

                    if player_immune and args.debug: 
                        if attacker in [entry[2] for entry in log if entry[1] == attacker]:
                            print(f"Debug: {player_name} three-starred a base not their mirror #{defender} on a loss, but they already hit their mirror")

                        elif attacker in invalid_mirror:
                            print(f"Debug: {player_name} three-starred a base not their mirror #{defender} on a loss, but their mirror was already taken")

                        else: 
                            print(f"Debug: {player_name} three-starred on a loss")
                            print(f"Debug: {player_name} hit a base not their own mirror #{defender}")

                    else: 
                        if attacker in [entry[2] for entry in log if entry[1] == attacker]:
                            print(f"Warning: {player_name} three-starred a base not their mirror #{defender} on a loss, but they already hit their mirror")
                            file.write(f"3\n{player_name}\ny\n5\n{war_end_date}\n1\n{enemy_clan}\n")
                            rules_broken[player_name] = True

                        elif attacker in invalid_mirror:
                            print(f"Warning: {player_name} three-starred a base not their mirror #{defender} on a loss, but their mirror was already taken")
                            file.write(f"3\n{player_name}\ny\n5\n{war_end_date}\n1\n{enemy_clan}\n")
                            rules_broken[player_name] = True

                        else: 
                            print(f"Warning: {player_name} three-starred on a loss")
                            file.write(f"3\n{player_name}\ny\n5\n{war_end_date}\n1\n{enemy_clan}\n")
                            print(f"Warning: {player_name} hit a base not their own mirror #{defender}")
                            file.write(f"3\n{player_name}\ny\n5\n{war_end_date}\n2\n{enemy_clan}\n")
                            rules_broken[player_name] = True
                    
                # First, check if this looks to be a snipe. 

                if win_loss == "loss" and stars < 2 and int(defender) <= 5 and int(attacker) > 5: 
                    if args.bypass and args.snipe: 
                        print(f"Bypass: #{attacker} {player_name} hit someone not their own mirror #{defender}, but this appears to be a snipe")

                    if player_name in snipe_count: 
                        snipe_count[player_name] += 1
                    else:
                        snipe_count[player_name] = 1

                    # Check if they have sniped twice.
                    if snipe_count[player_name] >= 2:
                        if player_immune and args.debug: 
                            print(f"Debug: {player_name} appears to have sniped twice.")
                            
                        else: 
                            print(f"Warning: {player_name} appears to have sniped twice.")
                            file.write(f"3\n{player_name}\ny\n5\n{war_end_date}\n3\n{enemy_clan}\n")
                            rules_broken[player_name] = True

                    continue

                elif win_loss == "win" and stars < 3 and int(defender) <= 5 and int(attacker) > 5:
                    if args.bypass and args.snipe: 
                        print(f"Bypass: #{attacker} {player_name} hit someone not their own mirror #{defender}, but this appears to be a snipe")

                    if player_name in snipe_count: 
                        snipe_count[player_name] += 1
                    else:
                        snipe_count[player_name] = 1

                    if snipe_count[player_name] >= 2:
                        if player_immune and args.debug: 
                            print(f"Debug: {player_name} appears to have sniped twice.")

                        else:
                            print(f"Warning: {player_name} appears to have sniped twice.")
                            file.write(f"3\n{player_name}\ny\n5\n{war_end_date}\n3\n{enemy_clan}\n")
                            rules_broken[player_name] = True

                    continue

                # Check their other hit to see if they hit their mirror. 
                elif attacker in [entry[2] for entry in log if entry[1] == attacker]:
                    if int(defender) <= 5:
                        if args.bypass and args.snipe: print(f"Bypass: #{attacker} {player_name} hit someone not their own mirror #{defender}, but this appears to be a snipe")
                        invalid_mirror.append(defender)

                    else: 
                        invalid_mirror.append(defender)

                else: 
                    # Debug; print the player's name, attacker, defender, stars, and time remaining.
                    # print(f"Unhandled case: {player_name}, Attacker: {attacker}, Defender: {defender}, Stars: {stars}, Time Remaining: {time_remaining:.2f}")

                    # Check if the defender's number is already in invalid_mirror. 
                    # If so, that means someone else took their mirror first, and therefore this is allowed. 
                    if attacker in invalid_mirror:
                        mirror_entry = [entry for entry in log if entry[2] == attacker][0]
                        if args.bypass: print(f"Bypass: {player_name} hit someone not their own mirror #{defender}, but their mirror was already taken by #{mirror_entry[1]} {mirror_entry[0]}")
                        continue

                    # Check if the defender's number is less than or equal to 5.
                    # If so, this still counts as a snipe, and we should not penalize.
                    if int(defender) <= 5:
                        if args.bypass and args.snipe: print(f"Bypass: {player_name} hit someone not their own mirror #{defender}, but this appears to be a snipe")
                        continue

                    else:
                        if player_immune and args.debug: 
                            print(f"Debug: {player_name} hit someone not their own mirror #{defender}")

                        else:
                            print(f"Warning: {player_name} hit someone not their own mirror #{defender}")
                            file.write(f"3\n{player_name}\ny\n5\n{war_end_date}\n2\n{enemy_clan}\n")
                            rules_broken[player_name] = True

                        invalid_mirror.append(defender)


            # Apply missed-hit penalties.
            # NOTE: `two_missed_hits` players may have zero attacks in `log`, so handle them without needing a log_entry.

            def _tag_for_name(_name: str):
                return next((t for t in player_activity_dict if player_activity_dict[t].name == _name), None)

            for entry in two_missed_hits:
                player_tag = _tag_for_name(entry)
                if not player_tag:
                    print(f"Error: {entry} not found in player_activity_dict. Continuing.")
                    continue

                war_data = (war_end_date, enemy_clan, win_loss)
                print(f"Warning: {entry} missed two hits")

                if war_data not in player_activity_dict[player_tag].wars_missed:
                    player_activity_dict[player_tag].wars_missed.append(war_data)

                rules_broken[entry] = True

            for entry in one_missed_hit:
                # Try to find their recorded hit(s) for snipe-bypass logic.
                player_hits = [le for le in log if le[0] == entry and le[2] is not None]

                # If we can't find a hit at all, still count the missed hit.
                if not player_hits:
                    player_tag = _tag_for_name(entry)
                    if not player_tag:
                        print(f"Error: {entry} not found in player_activity_dict. Continuing.")
                        continue

                    war_data = (war_end_date, enemy_clan, win_loss)
                    print(f"Warning: {entry} missed one hit")

                    if war_data not in player_activity_dict[player_tag].wars_missed:
                        player_activity_dict[player_tag].wars_missed.append(war_data)

                    rules_broken[entry] = True
                    continue

                for log_entry in player_hits:
                    mirror = log_entry[1] == log_entry[2]

                    # If their one attack was a low-base snipe and we allow bypass, don't penalize the missed hit.
                    if (not mirror) and int(log_entry[2]) < 6:
                        if args.bypass:
                            print(f"Bypass: #{log_entry[1]} {entry} missed one hit, and used the other to snipe")
                        break

                    player_tag = _tag_for_name(entry)
                    if not player_tag:
                        print(f"Error: {entry} not found in player_activity_dict. Continuing.")
                        break

                    war_data = (war_end_date, enemy_clan, win_loss)
                    print(f"Warning: {entry} missed one hit")

                    if war_data not in player_activity_dict[player_tag].wars_missed:
                        player_activity_dict[player_tag].wars_missed.append(war_data)

                    rules_broken[entry] = True
                    break

            # Check snipes 
            # for player_name, entry in player_entries.items(): 
            #     snipe_count = 0

            #     for hit in entry: 
            #         pname, attacker, defender, stars, attack_order = hit

            #         invalid_mirror = 

            #         if attacker in invalid_mirror: continue 
            #         if int(attacker) > 5 and int(defender) <= 5 and stars < 2: 
            #             snipe_count += 1

            #     if snipe_count == 2: 
            #         print(f"Warning: {player_name} appears to have sniped twice.")
            #         file.write(f"3\n{player_name}\ny\n5\n{war_end_date}\n3\n{enemy_clan}\n")
            #         rules_broken[player_name] = True

        elif win_loss in ["blacklist win", "blacklist loss"]: pass

        # Update each player's last seen date to the date of this war, if it is before this date. 
        for player in player_activity_dict:
            last_seen_value = player_activity_dict[player].last_seen
            if player_activity_dict[player].name in [entry[0] for entry in log]:
                player_activity_dict[player].last_seen = last_seen_value if datetime.datetime.strptime(last_seen_value, '%Y-%m-%d').date() > war_start else f"{war_start.strftime('%Y-%m-%d')}"

        # If player didn't break rules this war, check if they have any wars missed. If so, remove the oldest one. 
        for player in rules_broken: 
            if not rules_broken[player]: 
                # Find the corresponding player in the player_activity_dict. however, as it's categorized by player tag, we will need to do a search. 
                for player_tag in player_activity_dict:
                    if player_activity_dict[player_tag].name == player: 
                        # First, check the banked counter. If it's not three, add one. 
                        # If it is, remove a war if possible. If not, do nothing; we can't go into negative. 

                        if len(player_activity_dict[player_tag].banked_counter) < 3: 
                            # Check if this player already has this war banked. 
                            if not war_end_date in player_activity_dict[player_tag].wars_logged: 
                                player_activity_dict[player_tag].banked_counter.append(war_end_date)
                                player_activity_dict[player_tag].wars_logged.append(war_end_date)

                        if len(player_activity_dict[player_tag].banked_counter) >= 3:
                            # Check if they have any wars missed. If not, skip. 
                            if len(player_activity_dict[player_tag].wars_missed) == 0: 
                                continue 

                            print(f"Bank: {player} did not break any rules this war, and has inactivity value of {len(player_activity_dict[player_tag].wars_missed)}. Removing oldest war missed.")
                            player_activity_dict[player_tag].wars_missed.pop(0)
                            player_activity_dict[player_tag].banked_counter = []
                            
    # press any key to continue 
    input("Press any key to continue...")

# Check for players who have not been seen in one month. That is, 30 days. 
to_be_deleted = []
for player in player_activity_dict:
    last_seen = datetime.datetime.strptime(player_activity_dict[player].last_seen, "%Y-%m-%d")
    if (datetime.datetime.now() - last_seen).days >= 30: 
        print(f"Warning: {player_activity_dict[player].name} has not been seen in a month. Removing from player activity.")
        to_be_deleted.append(player)

for player in to_be_deleted:
    del player_activity_dict[player]

with open("activity_data.pickle", "wb") as file:
    pickle.dump(player_activity_dict, file)

# Sort the player_activity_dict by the number of wars missed. 
player_activity_dict = {player: player_activity_dict[player] for player in sorted(player_activity_dict, key=lambda player: len(player_activity_dict[player].wars_missed) + player_activity_dict[player].base_value, reverse=True)}

# For each player in the player activity dict, sort their wars missed by date descending. 
for player in player_activity_dict:
    player_activity_dict[player].wars_missed = sorted(player_activity_dict[player].wars_missed, key=lambda war: datetime.datetime.strptime(war[0], "%Y-%m-%d"), reverse=True)

# Manual backup dump. 
with open("./outputs/player_activity.txt", "w", encoding="utf-8") as file:
    # Format: player name, player tag
    for player in player_activity_dict:
        file.write(f"{player_activity_dict[player].name}: {player_activity_dict[player].tag}\n")
        file.write(f"  - Wars missed: {len(player_activity_dict[player].wars_missed)}\n")
        for war in player_activity_dict[player].wars_missed: 
            file.write(f"    - {war}\n")
        file.write(f"  - Last seen in clan: {player_activity_dict[player].last_seen}\n")
        file.write(f"  - Banked counter: {player_activity_dict[player].banked_counter}\n")
        file.write(f"  - Wars logged: {player_activity_dict[player].wars_logged}\n\n")

unix_time = int(time.time())
# Dump to be posted in a Discord channel.
with open("./outputs/activity_output.txt", "w", encoding="utf-8") as file:
    file.write(f"As of <t:{unix_time}:F> (<t:{unix_time}:R>):\n```\n")
    inactive_players = []

    for player in player_activity_dict: 
        # First, print out all the players that are in the clan; that is, whose in_clan values are set to True. 
        # We need to find the player in the other dictionary; claims_dictionary. 

        player_found = False 
        for claimer in claims_dictionary:
            for account in claims_dictionary[claimer]: 
                if account.name == player_activity_dict[player].name:
                    # Check if this player is in the clan.
                    if account.in_clan: 
                        player_found = True
                        break

                if player_found: break

        if player_found: 
            wars_missed = len(player_activity_dict[player].wars_missed)
            base_value = player_activity_dict[player].base_value
            pname = player_activity_dict[player].name

            if (wars_missed + base_value) == 0: continue
            if player_activity_dict[player].name in immunities: continue

            most_recent_missed_war = max(player_activity_dict[player].wars_missed, key=lambda war: datetime.datetime.strptime(war[0], "%Y-%m-%d"))[0]
            missed_timedelta = (datetime.datetime.now() - datetime.datetime.strptime(most_recent_missed_war, "%Y-%m-%d")).days
            # If the most recent missed war was more than 30 days ago, skip them. 
            # if missed_timedelta > 30: continue

            inactive_players.append((pname, base_value + wars_missed, missed_timedelta))


    if not inactive_players:
        file.write("No inactive players found.```")
    else:
        longest_player_name = max(len(p[0]) for p in inactive_players)

        file.write(f"╔══{'═'*longest_player_name}╤═════════════╤═════════════╗\n")
        file.write(f"║ Player name{' ' * (longest_player_name - 11)} │ Wars missed │ Most recent ║\n")

        for pname, value, missed_timedelta in inactive_players:
            file.write(f"║ {pname:<{longest_player_name}} │ {value:<11} │ {' ' if missed_timedelta < 10 else ''}{missed_timedelta} days ago ║\n")

        file.write(f"╚══{'═'*longest_player_name}╧═════════════╧═════════════╝ ```")

    for player in player_activity_dict: 
        # Next, print out all the players that are not in the clan; that is, whose in_clan values are set to False. 
        player_found = False 
        for claimer in claims_dictionary:
            for account in claims_dictionary[claimer]: 
                if account.name == player_activity_dict[player].name:
                    # Check if this player is in the clan.
                    if not account.in_clan: 
                        player_found = True
                        break
                    
                if player_found: break

        if player_found: 
            wars_missed = len(player_activity_dict[player].wars_missed)
            # Skip this player if they have not missed any wars.

            if wars_missed == 0: continue

            # Skip this player if they are immune. 
            if player_activity_dict[player].name in immunities: continue

            if wars_missed == 1: file.write(f"{player_activity_dict[player].name}: 1 war missed\n")
            else: file.write(f"{player_activity_dict[player].name}: {wars_missed} wars missed\n")

            file.write(f"  \- Last seen in clan: {player_activity_dict[player].last_seen}\n\n")

# Look in ./inputs and delete all files that are empty

for filename in os.listdir("./strikes"):
    if filename.endswith(".txt"):
        filepath = os.path.join("./strikes", filename)
        if os.path.getsize(filepath) == 0:
            os.remove(filepath)