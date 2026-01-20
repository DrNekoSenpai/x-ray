#!/usr/bin/env python3
"""
cwl_selection_refactored.py

CWL 30-player roster helper for Clash of Clans.

Inputs:
- Excel signup workbook (e.g., Google Form responses export):
    Columns used: "In-Game Name", "Availability"
- (Mid-week swap only) A "current status" file with player star counts and (optionally) roster membership.

Status file formats supported:
1) CSV/TSV with headers, e.g.
      In-Game Name,Stars,InRoster
      Sned,5,1
      Icestar Nyrissa,8,1
      Some Bench,0,0
   Recognized header names (case-insensitive):
      name:  "in-game name", "name", "player", "ign"
      stars: "stars", "star"
      roster: "inroster", "roster", "in_roster", "active", "inwar", "in_war"
2) No header, 2 columns (assumed to be CURRENT roster):
      Name,Stars
   In this case, everyone listed is treated as currently rostered.

Behavior:
1) The script asks whether this is:
   - Beginning of CWL week (set initial roster), or
   - Mid-week swap (reshuffle based on stars so far).
2) Beginning-of-week:
   - Pick exactly 30 members.
   - Must include ALL members with Availability == "8 stars only".
   - Fill remaining slots with a random subset of Availability == "All 7 wars".
3) Mid-week swap (computed from status file, no manual star prompts):
   - "8 stars only" members who have >= 8 stars AND are currently rostered are removed.
   - Anyone currently rostered with < 6 stars is protected (cannot be removed).
   - Roster is rebuilt to 30 with priority:
        (1) Auto sub-ins: not currently rostered AND still need stars
            - (a) "8 stars only" with < 8 stars
            - (b) anyone with < 6 stars (prioritize Standby/bench first)
        (2) Protected (<6 stars) currently rostered
        (3) Remaining "8 stars only" who aren't completed
        (4) Standby / bench
        (5) Random subset of "All 7 wars"
   - If required priorities exceed 30, the script aborts with a clear message.

Outputs:
- A text file listing FINAL ROSTER and BENCHED players, plus notes.

"""

from __future__ import annotations

import argparse
import csv
import random
import re
import sys
import unicodedata
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Set, Tuple

import pandas as pd


AVAIL_ALL7 = "All 7 wars"
AVAIL_8_ONLY = "8 stars only"
AVAIL_STANDBY = "Standby / bench"


# ---------------------------
# Utilities
# ---------------------------

def normalize_name(s: str) -> str:
    """Normalize a player name for matching/deduping.

    - Case-insensitive (casefold)
    - Ignores whitespace and common punctuation differences (e.g., 'Dr Stone' vs 'Dr. Stone')
    - Preserves letters/numbers and symbols (including most emoji), drops punctuation/separators.
    """
    if s is None:
        return ""
    s = str(s).strip().casefold()

    # Remove all whitespace
    s = re.sub(r"\s+", "", s)

    # Drop punctuation/separators, keep letters/numbers/symbols (emoji are usually symbols)
    kept = []
    for ch in s:
        cat = unicodedata.category(ch)
        if cat.startswith(("L", "N", "S")):
            kept.append(ch)
        # else drop (punctuation, separators, control chars, etc.)
    return "".join(kept)


def dedupe_preserve_order(items: Iterable[str]) -> List[str]:
    seen: Set[str] = set()
    out: List[str] = []
    for x in items:
        if x not in seen:
            seen.add(x)
            out.append(x)
    return out


def print_verbatim_list(title: str, names: Sequence[str]) -> None:
    print()
    print(title)
    if not names:
        print("  (none)")
        return
    for n in names:
        print(f"  - {n}")


def prompt_choice() -> str:
    print()
    print("Are we setting the roster at the beginning of CWL week, or doing a mid-week swap?")
    print("  1) Beginning of CWL week (pick initial 30)")
    print("  2) Mid-week swap (reshuffle using star status input)")
    while True:
        choice = input("Enter 1 or 2: ").strip()
        if choice == "1":
            return "begin"
        if choice == "2":
            return "swap"
        print("Please enter 1 or 2.")


def choose_output_dir(input_path: Path, requested: Optional[Path]) -> Path:
    if requested:
        requested.mkdir(parents=True, exist_ok=True)
        return requested

    # Prefer ./outputs next to cwd; fallback to input directory.
    cwd_outputs = Path.cwd() / "outputs"
    try:
        cwd_outputs.mkdir(parents=True, exist_ok=True)
        return cwd_outputs
    except Exception:
        in_dir = input_path.parent / "outputs"
        in_dir.mkdir(parents=True, exist_ok=True)
        return in_dir


# ---------------------------
# Signup loading
# ---------------------------

def load_signups(xlsx_path: Path) -> pd.DataFrame:
    df = pd.read_excel(xlsx_path)
    # Normalize expected columns if the sheet varies slightly
    # Prefer exact column names used by the sample file.
    expected_name = "In-Game Name"
    expected_avail = "Availability"
    if expected_name not in df.columns or expected_avail not in df.columns:
        # Try fuzzy match
        cols = {c.casefold(): c for c in df.columns}
        name_col = cols.get("in-game name") or cols.get("in game name") or cols.get("name") or cols.get("ign")
        avail_col = cols.get("availability")
        if not name_col or not avail_col:
            raise ValueError(f"Could not find required columns in signup sheet. Found columns: {list(df.columns)}")
        df = df.rename(columns={name_col: expected_name, avail_col: expected_avail})

    df = df[[expected_name, expected_avail]].copy()
    df[expected_name] = df[expected_name].astype(str).str.strip()
    df[expected_avail] = df[expected_avail].astype(str).str.strip()

    # Drop blank names
    df = df[df[expected_name].str.len() > 0]
    return df


@dataclass(frozen=True)
class SignupPools:
    all_names: List[str]
    name_index: Dict[str, str]  # normalized -> canonical
    avail_by_name: Dict[str, str]  # canonical -> availability (raw cell text)
    eight_only: List[str]
    all7: List[str]
    standby: List[str]
    other: List[str]


def build_pools(df: pd.DataFrame) -> SignupPools:
    names = df["In-Game Name"].tolist()
    avail = df["Availability"].tolist()

    # canonicalize duplicates in sheet (keep first spelling encountered)
    name_index: Dict[str, str] = {}
    avail_by_name: Dict[str, str] = {}
    canonical_names: List[str] = []
    for n, a in zip(names, avail):
        cn = str(n).strip()
        key = normalize_name(cn)
        if not key:
            continue
        if key not in name_index:
            name_index[key] = cn
            canonical_names.append(cn)
        # store availability for canonical name
        avail_by_name[name_index[key]] = str(a).strip()

    def by_availability(target: str) -> List[str]:
        out = []
        for cn in canonical_names:
            if avail_by_name.get(cn, "") == target:
                out.append(cn)
        return out

    eight_only = by_availability(AVAIL_8_ONLY)
    all7 = by_availability(AVAIL_ALL7)
    standby = by_availability(AVAIL_STANDBY)

    known = set(eight_only) | set(all7) | set(standby)
    other = [n for n in canonical_names if n not in known]

    return SignupPools(
        all_names=canonical_names,
        name_index=name_index,
        avail_by_name=avail_by_name,
        eight_only=eight_only,
        all7=all7,
        standby=standby,
        other=other,
    )


# ---------------------------
# Status loading
# ---------------------------

def _looks_like_header(row: List[str]) -> bool:
    joined = " ".join([c.strip().casefold() for c in row if c is not None])
    # crude heuristic: if it contains "star" or "roster" or "name", it's probably a header
    return any(k in joined for k in ["star", "roster", "inroster", "in_roster", "name", "ign", "player", "in-game"])


def _parse_bool(s: str) -> bool:
    if s is None:
        return False
    t = str(s).strip().casefold()
    return t in {"1", "true", "t", "yes", "y", "roster", "in", "active"}


def _parse_int(s: str) -> int:
    if s is None:
        return 0
    t = str(s).strip()
    if t == "":
        return 0
    try:
        return int(float(t))
    except ValueError:
        return 0


def load_status_file(
    status_path: Path,
    name_index: Dict[str, str],
    expected_total_signups: Optional[int] = None,
) -> Tuple[Dict[str, int], Set[str]]:
    """
    Returns:
      stars_by_name: canonical name -> stars (int)
      current_roster: set of canonical names currently rostered

    Notes:
      - If the status file does NOT include a roster indicator column, every row is treated as rostered.
      - If some signups are missing from the status file, they are assumed to be NOT rostered with 0 stars.
        (This can make the swap algorithm aggressively "sub them in" if they need stars.)
    """
    if not status_path.exists():
        raise FileNotFoundError(f"Status file not found: {status_path}")

    stars_by_name: Dict[str, int] = {}
    current_roster: Set[str] = set()

    ext = status_path.suffix.casefold()

    # ---- Excel status file ----
    if ext in {".xlsx", ".xls", ".xlsm"}:
        df = pd.read_excel(status_path)
        if df.empty:
            raise ValueError("Status file appears to be empty.")

        cols = {str(c).strip().casefold(): c for c in df.columns}

        # Column picks (fuzzy)
        name_col = (
            cols.get("in-game name") or cols.get("in game name") or cols.get("name") or cols.get("player") or cols.get("ign")
        )
        stars_col = cols.get("stars") or cols.get("star")
        roster_col = (
            cols.get("inroster") or cols.get("in_roster") or cols.get("roster") or cols.get("active") or cols.get("inwar") or cols.get("in_war")
        )

        if not name_col or not stars_col:
            raise ValueError(f"Status Excel must include name + stars columns. Found columns: {list(df.columns)}")

        for _, row in df.iterrows():
            raw_name = str(row.get(name_col, "")).strip()
            if not raw_name:
                continue
            key = normalize_name(raw_name)
            canonical = name_index.get(key, raw_name)

            st = _parse_int(row.get(stars_col, 0))
            stars_by_name[canonical] = st

            if roster_col is None:
                current_roster.add(canonical)
            else:
                if _parse_bool(row.get(roster_col, "")):
                    current_roster.add(canonical)

        if roster_col is not None and not current_roster:
            raise ValueError(
                "Status Excel had a roster column, but no rows were marked rostered. "
                "Check the InRoster/roster values (expected 1/0, yes/no, true/false)."
            )

        # If no roster column, we can't tell who is benched; warn if this looks like a partial list.
        if roster_col is None and expected_total_signups and len(df) < expected_total_signups:
            print(
                "WARNING: Status file has no roster column and contains fewer rows than total signups. "
                "Anyone missing will be assumed NOT rostered with 0 stars.",
                file=sys.stderr,
            )

        return stars_by_name, current_roster

    # ---- CSV/TSV status file ----
    text = status_path.read_text(encoding="utf-8", errors="ignore")
    delim = "," if text.count(",") >= text.count("\t") else "\t"

    reader = csv.reader(text.splitlines(), delimiter=delim)
    rows = [r for r in reader if any(c.strip() for c in r)]
    if not rows:
        raise ValueError("Status file appears to be empty.")

    header = None
    data_rows = rows

    if _looks_like_header(rows[0]):
        header = [c.strip() for c in rows[0]]
        data_rows = rows[1:]

    name_col = 0
    stars_col = 1 if len(rows[0]) > 1 else None
    roster_col = None

    if header:
        cols = {h.casefold(): i for i, h in enumerate(header)}
        for key in ["in-game name", "in game name", "name", "player", "ign"]:
            if key in cols:
                name_col = cols[key]
                break
        for key in ["stars", "star"]:
            if key in cols:
                stars_col = cols[key]
                break
        for key in ["inroster", "in_roster", "roster", "active", "inwar", "in_war"]:
            if key in cols:
                roster_col = cols[key]
                break

    for r in data_rows:
        if name_col >= len(r):
            continue
        raw_name = r[name_col].strip()
        if not raw_name:
            continue
        key = normalize_name(raw_name)
        canonical = name_index.get(key, raw_name.strip())

        st = 0
        if stars_col is not None and stars_col < len(r):
            st = _parse_int(r[stars_col])
        stars_by_name[canonical] = st

        if roster_col is None:
            current_roster.add(canonical)
        else:
            val = r[roster_col] if roster_col < len(r) else ""
            if _parse_bool(val):
                current_roster.add(canonical)

    if header and roster_col is not None and not current_roster:
        raise ValueError(
            "Status file had a roster column, but no rows were marked rostered. "
            "Check the InRoster/roster values (expected 1/0, yes/no, true/false)."
        )

    if roster_col is None and expected_total_signups and len(rows) - (1 if header else 0) < expected_total_signups:
        print(
            "WARNING: Status file has no roster column and contains fewer rows than total signups. "
            "Anyone missing will be assumed NOT rostered with 0 stars.",
            file=sys.stderr,
        )

    return stars_by_name, current_roster



# ---------------------------
# Selection logic
# ---------------------------

def pick_beginning_of_week(pools: SignupPools, rng: random.Random) -> Tuple[List[str], List[str], List[str]]:
    eight_only = pools.eight_only
    all7 = pools.all7

    if len(eight_only) > 30:
        raise ValueError(f"More than 30 members are marked '{AVAIL_8_ONLY}' ({len(eight_only)}). Cannot create a 30 roster.")

    roster: List[str] = []
    notes: List[str] = []

    roster.extend(eight_only)
    notes.append(f"Included all '{AVAIL_8_ONLY}': {len(eight_only)}")

    remaining_slots = 30 - len(roster)

    # Fill from All 7 wars (as requested)
    if remaining_slots > 0:
        take = min(remaining_slots, len(all7))
        picked_all7 = rng.sample(all7, take) if take > 0 else []
        roster.extend(picked_all7)
        notes.append(f"Randomly selected from '{AVAIL_ALL7}': {len(picked_all7)} (seeded)")
        remaining_slots = 30 - len(roster)

    # If All7 isn't enough, fall back to Standby/bench, then "other" signups.
    if remaining_slots > 0:
        standby_fill = [n for n in pools.standby if n not in set(roster)]
        take = min(remaining_slots, len(standby_fill))
        roster.extend(standby_fill[:take])
        if take:
            notes.append(f"Filled remaining slots from '{AVAIL_STANDBY}': {take}")
        remaining_slots = 30 - len(roster)

    if remaining_slots > 0:
        other_fill = [n for n in pools.other if n not in set(roster)]
        take = min(remaining_slots, len(other_fill))
        roster.extend(other_fill[:take])
        if take:
            notes.append(f"Filled remaining slots from OTHER availability: {take}")
        remaining_slots = 30 - len(roster)

    roster = dedupe_preserve_order(roster)

    if len(roster) < 30:
        raise ValueError(f"Not enough total signups to build a 30 roster (have {len(roster)} after filling).")

    roster = roster[:30]
    benched = [n for n in pools.all_names if n not in set(roster)]
    return roster, benched, notes


def pick_midweek_swap(
    pools: SignupPools,
    stars_by_name: Dict[str, int],
    current_roster: Set[str],
    rng: random.Random,
) -> Tuple[List[str], List[str], List[str]]:
    avail = pools.avail_by_name

    def stars(n: str) -> int:
        return int(stars_by_name.get(n, 0))

    # Rule (a): rostered 8-only members who already have 8+ stars are removed.
    completed_8_rostered = [n for n in pools.eight_only if n in current_roster and stars(n) >= 8]
    completed_8_all = set([n for n in pools.eight_only if stars(n) >= 8])

    remaining_8 = [n for n in pools.eight_only if n not in completed_8_all]

    # Rule (b): currently rostered members with <6 stars are protected.
    protected_rostered_under6 = [n for n in pools.all_names if (n in current_roster and stars(n) < 6 and n not in completed_8_rostered)]

    # Auto "sub-ins" derived from status vs signups:
    # - Not currently rostered, still need stars (8-only incomplete OR anyone <6 stars)
    non_rostered = [n for n in pools.all_names if n not in current_roster and n not in completed_8_all]

    # Priority inside auto-sub-ins:
    #   1) 8-only incomplete
    #   2) <6 stars, Standby first
    sub_ins_8_only = [n for n in non_rostered if avail.get(n, "") == AVAIL_8_ONLY and stars(n) < 8]
    sub_ins_under6_standby = [n for n in non_rostered if stars(n) < 6 and avail.get(n, "") == AVAIL_STANDBY and n not in sub_ins_8_only]
    sub_ins_under6_other = [n for n in non_rostered if stars(n) < 6 and n not in sub_ins_8_only and n not in sub_ins_under6_standby]

    auto_sub_ins = dedupe_preserve_order(sub_ins_8_only + sub_ins_under6_standby + sub_ins_under6_other)

    # Remaining 8-only incomplete (whether rostered or not) should be prioritized so they can finish 8 stars.
    remaining_8_incomplete = [n for n in remaining_8 if stars(n) < 8]

    # Build priority list:
    priority = dedupe_preserve_order(
        auto_sub_ins +
        protected_rostered_under6 +
        remaining_8_incomplete
    )

    if len(priority) > 30:
        # This is an impossible constraint set.
        msg_lines = [
            "ERROR: Priority-required members exceed 30. You must resolve manually.",
            f"Priority count: {len(priority)}",
            "",
            "Priority-required list (in order):",
        ] + [f"  - {n} (avail={avail.get(n,'')}, stars={stars(n)}, rostered={'Y' if n in current_roster else 'N'})" for n in priority]
        raise ValueError("\n".join(msg_lines))

    # Fill with standby, then random all7
    roster = list(priority)

    standby_fill = [n for n in pools.standby if n not in set(roster) and n not in completed_8_all]
    roster.extend(standby_fill)

    # Fill remaining from All7 random
    remaining_slots = 30 - len(roster)
    all7_candidates = [n for n in pools.all7 if n not in set(roster) and n not in completed_8_all]
    if remaining_slots > 0:
        if remaining_slots > len(all7_candidates):
            # If we still don't have enough, fill from any other "other" signups as last resort
            other_candidates = [n for n in pools.other if n not in set(roster) and n not in completed_8_all]
            take_all7 = all7_candidates
            roster.extend(take_all7)
            remaining_slots = 30 - len(roster)
            if remaining_slots > 0 and other_candidates:
                roster.extend(other_candidates[:remaining_slots])
        else:
            roster.extend(rng.sample(all7_candidates, remaining_slots))

    roster = roster[:30]

    benched = [n for n in pools.all_names if n not in set(roster)]
    notes: List[str] = []

    # Diagnostics
    removed = sorted([n for n in current_roster if n not in set(roster)], key=lambda x: (avail.get(x,""), x.casefold()))
    added = sorted([n for n in roster if n not in current_roster], key=lambda x: (avail.get(x,""), x.casefold()))

    notes.append(f"Current roster size (from status file): {len(current_roster)}")
    notes.append(f"Removed completed '{AVAIL_8_ONLY}' (>=8 stars) who were rostered: {', '.join(completed_8_rostered) if completed_8_rostered else '(none)'}")
    notes.append(f"Protected rostered members with <6 stars: {', '.join(protected_rostered_under6) if protected_rostered_under6 else '(none)'}")
    notes.append(f"Auto sub-ins (derived from signups vs roster + stars): {', '.join(auto_sub_ins) if auto_sub_ins else '(none)'}")
    notes.append(f"Roster additions vs current roster: {', '.join(added) if added else '(none)'}")
    notes.append(f"Roster removals vs current roster: {', '.join(removed) if removed else '(none)'}")

    return roster, benched, notes


# ---------------------------
# Output
# ---------------------------

def write_output(out_path: Path, mode: str, roster: List[str], benched: List[str], notes: List[str]) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as f:
        f.write(f"MODE: {mode}\n")
        f.write("\nNOTES:\n")
        for n in notes:
            f.write(f"- {n}\n")
        f.write("\nFINAL ROSTER (30):\n")
        for n in roster:
            f.write(f"- {n}\n")
        f.write("\nBENCHED / NOT ROSTERED:\n")
        for n in benched:
            f.write(f"- {n}\n")


# ---------------------------
# Main
# ---------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description="CWL roster selection helper (30-player roster).")
    parser.add_argument("-i", "--input", required=True, help="Path to CWL signups Excel workbook (.xlsx).")
    parser.add_argument("-o", "--output-prefix", default="cwl", help="Output filename prefix (default: cwl).")
    parser.add_argument("--output-dir", default=None, help="Output directory (default: ./outputs or next to input).")
    parser.add_argument("-s", "--seed", default=None, help="Random seed for reproducible picks (optional).")
    parser.add_argument("--mode", choices=["begin", "swap"], default=None, help="Skip prompt and force a mode.")
    parser.add_argument("--status", default=None, help="(swap mode) Path to status CSV/TSV file with stars (and optional roster flags).")
    args = parser.parse_args()

    input_path = Path(args.input).expanduser().resolve()
    df = load_signups(input_path)
    pools = build_pools(df)

    seed = args.seed
    if seed is None:
        # deterministic-ish seed from system entropy; still reproducible if user passes -s
        rng = random.Random()
    else:
        rng = random.Random(str(seed))

    mode = args.mode or prompt_choice()

    notes: List[str] = []
    notes.append(f"Signup file: {input_path.name}")
    if seed is not None:
        notes.append(f"Seed: {seed}")

    if mode == "begin":
        roster, benched, more_notes = pick_beginning_of_week(pools, rng)
        notes.extend(more_notes)
    else:
        status_path = Path(args.status).expanduser().resolve() if args.status else None
        if status_path is None:
            print()
            status_in = input("Enter path to status file (CSV/TSV): ").strip()
            status_path = Path(status_in).expanduser().resolve()

        stars_by_name, current_roster = load_status_file(status_path, pools.name_index, expected_total_signups=len(pools.all_names))
        notes.append(f"Status file: {status_path.name}")

        # Print quick summary table (verbatim names) for sanity
        print_verbatim_list("CURRENT ROSTER (from status file):", sorted(current_roster, key=lambda x: x.casefold()))

        roster, benched, more_notes = pick_midweek_swap(pools, stars_by_name, current_roster, rng)
        notes.extend(more_notes)

    print_verbatim_list("FINAL ROSTER (rostered players):", roster)
    print_verbatim_list("BENCHED / NOT ROSTERED:", benched)

    out_dir = choose_output_dir(input_path, Path(args.output_dir).expanduser().resolve() if args.output_dir else None)
    out_path = out_dir / f"{args.output_prefix}_roster.txt"
    write_output(out_path, mode=mode, roster=roster, benched=benched, notes=notes)

    print()
    print(f"Wrote output to: {out_path.resolve()}")


if __name__ == "__main__":
    main()
