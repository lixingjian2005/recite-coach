"""Deploy Recite Coach player kit files to an output directory.

Copies the 5 player kit files (serve.py, recite-player.html, start.bat,
start.vbs, start.sh) from the bundled player-kit/ directory into the
specified target directory.

If cards.md exists but cards.json does not, automatically converts
cards.md → cards.json via the bundled md2cards.py script.  Use --force
to reconvert even when cards.json already exists.
"""

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

PLAYER_KIT_FILES = [
    "serve.py",
    "recite-player.html",
    "start.bat",
    "start.vbs",
    "start.sh",
]


def convert_markdown(target_dir: Path, converter: Path) -> int:
    """Run md2cards.py on the target directory.  Returns 0 on success, 1 on error."""
    result = subprocess.run(
        [sys.executable, str(converter), str(target_dir)],
        capture_output=True, text=True,
    )
    if result.stdout:
        print(result.stdout)
    if result.returncode != 0:
        if result.stderr:
            print(result.stderr)
        return 1
    return 0


def deploy(target_dir: Path, force: bool = False) -> int:
    source_dir = Path(__file__).resolve().parent / "player-kit"
    target_dir.mkdir(parents=True, exist_ok=True)

    errors = 0

    # ── Step 1: Convert cards.md → cards.json if needed ──
    md_path = target_dir / "cards.md"
    json_path = target_dir / "cards.json"
    converter = Path(__file__).resolve().parent / "md2cards.py"

    if md_path.exists():
        if force or not json_path.exists():
            print("  cards.md found, converting to cards.json...")
            if convert_markdown(target_dir, converter) != 0:
                errors += 1
                # Don't proceed — bad markdown means no valid deck
                print("\n  [FAIL] Markdown conversion failed. Fix errors above and re-run.")
                return 1
        else:
            print("  [INFO] Both cards.md and cards.json exist — using existing cards.json.")
            print("  Re-run with --force to regenerate cards.json from cards.md.")
    elif not json_path.exists():
        print("\n  [WARN] Neither cards.md nor cards.json found in output directory.")
        print("  Run card generation first, then deploy the player kit.")

    # ── Step 2: Copy player kit files ──
    print()
    for filename in PLAYER_KIT_FILES:
        src = source_dir / filename
        dst = target_dir / filename
        try:
            shutil.copy2(src, dst)
            print(f"  [OK] {filename}")
        except Exception as exc:
            print(f"  [FAIL] {filename}: {exc}")
            errors += 1

    return 1 if errors else 0


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Deploy recite-coach player kit to an output directory"
    )
    parser.add_argument(
        "target",
        help="Output directory to copy player files into",
    )
    parser.add_argument(
        "--force", action="store_true",
        help="Reconvert cards.md → cards.json even if cards.json already exists",
    )
    args = parser.parse_args()

    target = Path(args.target)
    print(f"Deploying player kit to: {target}")
    sys.exit(deploy(target, force=args.force))


if __name__ == "__main__":
    main()
