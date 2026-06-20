"""Deploy Recite Coach player kit files to an output directory.

Copies the 5 player kit files (serve.py, recite-player.html, start.bat,
start.vbs, start.sh) from the bundled player-kit/ directory into the
specified target directory.  Run this AFTER writing cards.json.
"""

import argparse
import shutil
import sys
from pathlib import Path

PLAYER_KIT_FILES = [
    "serve.py",
    "recite-player.html",
    "start.bat",
    "start.vbs",
    "start.sh",
]


def deploy(target_dir: Path) -> int:
    source_dir = Path(__file__).resolve().parent / "player-kit"
    target_dir.mkdir(parents=True, exist_ok=True)

    errors = 0
    for filename in PLAYER_KIT_FILES:
        src = source_dir / filename
        dst = target_dir / filename
        try:
            shutil.copy2(src, dst)
            print(f"  [OK] {filename}")
        except Exception as exc:
            print(f"  [FAIL] {filename}: {exc}")
            errors += 1

    if not (target_dir / "cards.json").exists():
        print("\n  [WARN] cards.json not found in output directory.")
        print("  Run card generation first, then deploy the player kit.")

    return 1 if errors else 0


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Deploy recite-coach player kit to an output directory"
    )
    parser.add_argument(
        "target",
        help="Output directory to copy player files into",
    )
    args = parser.parse_args()

    target = Path(args.target)
    print(f"Deploying player kit to: {target}")
    sys.exit(deploy(target))


if __name__ == "__main__":
    main()
