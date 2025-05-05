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


def write_list(path: Path, names: list[str]) -> None:
    """Write a list of names to a file, one per line."""
    path.write_text("\n".join(names) + "\n", encoding='utf-8')


def main():
    parser = argparse.ArgumentParser(description="Randomly bench players for CWL.")
    parser.add_argument('-s', '--seed', type=int, help='Random seed for reproducibility')
    parser.add_argument('-b', '--bench', nargs='+', help='Players to force bench this season')
    parser.add_argument('-p', '--play', nargs='+', help='Players to force include this season')
    parser.add_argument('-o', '--output-prefix', default='cwl', help='Prefix for output files')
    args = parser.parse_args()

    # Load and filter signups
    names = load_signups("./cwl-responses.xlsx")
    total = len(names)
    bench_count = total - 30
    if bench_count <= 0:
        print(f"Error: Need to bench at least one player. Total signups: {total}", file=sys.stderr)
        sys.exit(1)

    # Previous bench handling
    bench_file = Path(f"{args.output_prefix}_bench.txt")
    prev_bench = load_prev_bench(bench_file)
    # Only re-include those who re-signed up
    rebench = [n for n in prev_bench if n in names]

    # Prepare forced lists
    forced_bench = args.bench or []
    forced_play = args.play or []
    # Validate forced names
    for p in forced_bench + forced_play:
        if p not in names:
            print(f"Error: '{p}' not found in current signups.", file=sys.stderr)
            sys.exit(1)

    # Build pool eligible for random benching
    eligible = set(names)
    # Exclude previously benched who re-signed up
    eligible -= set(rebench)
    # Exclude forced-players from bench pool
    eligible -= set(forced_play)
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
    bench = list(dict.fromkeys(forced_bench + random_bench))  # preserve order, unique
    play = [n for n in names if n not in bench]

    # Write outputs
    write_list(bench_file, bench)
    write_list(Path(f"{args.output_prefix}_play.txt"), play)

    # Summary
    print(f"Total 'All 7 wars' signups: {total}")
    print(f"Previously benched re-signed: {len(rebench)}")
    if prev_bench and not rebench:
        print(f"Note: previous bench entries no longer signed up: {len(prev_bench) - len(rebench)}")
    if forced_bench:
        print(f"Forced bench ({len(forced_bench)}): {', '.join(forced_bench)}")
    if forced_play:
        print(f"Forced play ({len(forced_play)}): {', '.join(forced_play)}")
    print(f"Benched players ({len(bench)}): written to {bench_file}")
    print(f"Playing players ({len(play)}): written to {args.output_prefix}_play.txt")

if __name__ == '__main__':
    main()
