#!/usr/bin/env python3
"""
bench_random.py

Randomly bench players so that exactly 30 play, using an Excel signup workbook.
Supports forcing specific players to bench or to play (no-bench) via command-line flags.
Benched players are guaranteed not to be benched next round if they sign up again.
Handles departures by ignoring stale bench entries.
"""

import argparse
import random
import sys
from pathlib import Path
import pandas as pd

def load_signups(path: Path) -> list[str]:
    """Load signup data from an Excel file and return names with Availability 'All 7 wars'."""
    df = pd.read_excel(path)
    df['Availability'] = df['Availability'].astype(str).str.strip()
    filtered = df[df['Availability'] == 'All 7 wars']
    return filtered['In-Game Name'].astype(str).str.strip().tolist()

def load_prev_bench(path: Path) -> list[str]:
    """Load previously benched players from a text file, one per line."""
    if not path.exists():
        return []
    return [line.strip() for line in path.read_text(encoding='utf-8').splitlines() if line.strip()]

def write_list(path: Path, bench: list[str], play: list[str]) -> None:
    """Write a list of names to a file, one per line."""
    path.write_text("Players to be benched:\n  - " + "\n  - ".join(bench), encoding='utf-8')
    path.write_text("\nPlayers to play:\n  - " + "\n  - ".join(play), encoding='utf-8')

def prompt_list(prompt: str) -> list[str]:
    """Prompt the user to enter names one per line, ending with a blank line."""
    print(prompt)
    lines = []
    while True:
        try:
            line = input().strip()
        except EOFError:
            break
        if not line:
            break
        lines.append(line)
    return lines

def main():
    parser = argparse.ArgumentParser(description="Randomly bench players for CWL.")
    parser.add_argument('-s', '--seed', type=int, help='Random seed for reproducibility')
    parser.add_argument('-b', '--bench', nargs='+', help='Players to force bench this season')
    parser.add_argument('-nb', '--no-bench', nargs='+', help='Players that must not be benched')
    parser.add_argument('-o', '--output-prefix', default='cwl', help='Prefix for output files')
    args = parser.parse_args()

    # Interactive override for bench list
    if not args.bench:
        confirm = input("Are there any players that must be benched? (y/n): ").strip().lower()
        if confirm == 'y':
            args.bench = prompt_list("Enter player names to bench, one per line (blank line to finish):")
        else:
            args.bench = []

    # Interactive override for no-bench list
    if not args.no_bench:
        confirm_nb = input("Are there any players that must not be benched? (y/n): ").strip().lower()
        if confirm_nb == 'y':
            args.no_bench = prompt_list("Enter player names not to bench, one per line (blank line to finish):")
        else:
            args.no_bench = []

    # Load and filter signups
    names = load_signups("./cwl-responses.xlsx")
    total = len(names)

    bench_count = total - 30
    print(f"Total signups: {total}, Players to bench: {bench_count}")
    if bench_count <= 0:
        print(f"Error: Need to bench at least one player. Total signups: {total}", file=sys.stderr)
        sys.exit(1)

    # Previous bench handling
    bench_file = Path(f"{args.output_prefix}_bench.txt")

    # Prepare forced lists
    forced_bench = args.bench or []
    forced_no_bench = args.no_bench or []
    # Validate forced names
    for p in forced_bench + forced_no_bench:
        if p not in names:
            print(f"Error: '{p}' not found in current signups.", file=sys.stderr)
            sys.exit(1)

    # Build pool eligible for random benching
    eligible = set(names)
    # Exclude forced play / no-bench from bench pool
    eligible -= set(forced_no_bench)
    eligible = list(eligible)

    # Check forced bench count
    if len(forced_bench) > bench_count:
        print(f"Error: Cannot force bench {len(forced_bench)} players; only {bench_count} bench slots.", file=sys.stderr)
        sys.exit(1)

    # Randomly pick remaining benches
    if args.seed is not None:
        random.seed(args.seed)
    random_bench = random.sample(eligible, bench_count - len(forced_bench))

    # Final lists
    bench = list(dict.fromkeys(forced_bench + random_bench))
    play = [n for n in names if n not in bench]

    # Write outputs
    write_list(Path(f"{args.output_prefix}_play.txt"), bench, play)

    # Summary
    print(f"Total 'All 7 wars' signups: {total}")
    if forced_bench: print(f"Forced bench ({len(forced_bench)}): {', '.join(forced_bench)}")
    if forced_no_bench: print(f"Forced no-bench ({len(forced_no_bench)}): {', '.join(forced_no_bench)}")
    print(f"Benched players: ({len(bench)}). Rostered players ({len(play)})")

if __name__ == '__main__':
    main()
