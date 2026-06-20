#!/usr/bin/env python3
"""md2cards.py — Convert recite-coach structured markdown to valid cards.json.

Parse rules:
  # <text>                             → deck title (first h1 only)
  > **newItemsPerSession**: <N>        → newItemsPerSession (optional, default 3)
  --- (on a line by itself)            → card separator
  ## <N>. <text>                       → new card: id=N, title=<text>
  > importance: <1|2|3>               → card importance (required per card)
  > mnemonic: <text>                   → card mnemonic (optional, default "")
  > hints:                             → starts hints block
  > - <text>                           → hint entry (must follow "> hints:")
  All other non-blank lines            → content_full body
"""

import argparse
import json
import re
import sys
from pathlib import Path

VALID_IMPORTANCE = {1, 2, 3}

# ── Regex patterns ──
HEADING_H1_RE   = re.compile(r'^# (.+)$')
CARD_HEADER_RE  = re.compile(r'^##\s+(\d+)\.\s+(.+)$')
NIPS_RE         = re.compile(r'>\s*\*\*newItemsPerSession\*\*\s*:\s*(\d+)')
IMP_RE          = re.compile(r'>\s*importance\s*:\s*(\d)')
MNEMONIC_RE     = re.compile(r'>\s*mnemonic\s*:\s*(.*)')
HINTS_START_RE  = re.compile(r'>\s*hints\s*:\s*$')
HINT_ITEM_RE    = re.compile(r'>\s+-\s+(.*)')
META_LINE_RE    = re.compile(r'>\s+(\S.*)')


def parse_cards_md(text: str, source_path: str = "cards.md") -> dict:
    """Parse structured markdown into the cards.json data model.

    Returns a dict with keys: title, newItemsPerSession, items.
    Raises SystemExit(1) on validation errors.
    """

    lines = text.split('\n')
    result = {'title': '', 'newItemsPerSession': 3, 'items': []}

    current_card = None
    content_lines = []          # accumulates content_full body
    in_hints_block = False      # True while inside "> hints:" section
    errors = []

    # ── State helpers ──

    def error(msg: str) -> None:
        errors.append(msg)

    def emit_card() -> None:
        """Push current_card into result['items'] and reset."""
        nonlocal current_card, content_lines, in_hints_block
        if current_card is None:
            return
        # Strip leading/trailing empty lines from content
        body = '\n'.join(content_lines).strip()
        current_card['content_full'] = body
        result['items'].append(current_card)
        current_card = None
        content_lines = []
        in_hints_block = False

    def new_card(id_val: int, title: str, line_no: int) -> dict:
        if any(c['id'] == id_val for c in result['items']):
            error(f"Line {line_no}: duplicate card id={id_val}")
        return {
            'id': id_val,
            'title': title.strip(),
            'importance': 1,
            'content_full': '',
            'mnemonic': '',
            'hints': [],
        }

    # ── Main parse loop ──

    state = 'LOOKING_FOR_TITLE'

    for line_no, raw_line in enumerate(lines, start=1):
        stripped = raw_line.strip()

        # ===== LOOKING_FOR_TITLE =====
        if state == 'LOOKING_FOR_TITLE':
            m = HEADING_H1_RE.match(stripped)
            if m:
                result['title'] = m.group(1).strip()
                state = 'DECK_META'
            # blank/other lines before title are ignored
            continue

        # ===== DECK_META =====
        if state == 'DECK_META':
            m_nips = NIPS_RE.match(stripped)
            if m_nips:
                result['newItemsPerSession'] = int(m_nips.group(1))
                continue
            if stripped == '---':
                state = 'BETWEEN_CARDS'
                continue
            m_card = CARD_HEADER_RE.match(stripped)
            if m_card:
                state = 'CARD_HEADER'
                emit_card()
                current_card = new_card(int(m_card.group(1)), m_card.group(2), line_no)
                state = 'CARD_META'
                continue
            # blank / other lines in deck meta zone: ignored
            continue

        # ===== BETWEEN_CARDS =====
        if state == 'BETWEEN_CARDS':
            if stripped == '' or stripped == '---':
                continue
            m_card = CARD_HEADER_RE.match(stripped)
            if m_card:
                emit_card()
                current_card = new_card(int(m_card.group(1)), m_card.group(2), line_no)
                state = 'CARD_META'
                continue
            error(f"Line {line_no}: expected '## N. Title' after '---', got: {stripped[:80]}")
            continue

        # ===== CARD_META =====
        if state == 'CARD_META':
            if stripped == '':
                continue

            # Separator (end card early, before content)
            if stripped == '---':
                if current_card is not None and not content_lines:
                    error(f"Line {line_no}: card id={current_card['id']} has no content — "
                           "add answer text after the metadata lines")
                emit_card()
                state = 'BETWEEN_CARDS'
                continue

            # Next card header (previous card had no content)
            m_card = CARD_HEADER_RE.match(stripped)
            if m_card:
                if current_card is not None and not content_lines:
                    error(f"Line {line_no}: card id={current_card['id']} has no content before "
                           f"next card header — add answer text after the metadata lines")
                emit_card()
                current_card = new_card(int(m_card.group(1)), m_card.group(2), line_no)
                state = 'CARD_META'
                continue

            # Metadata: importance
            m_imp = IMP_RE.match(stripped)
            if m_imp:
                val = int(m_imp.group(1))
                if val not in VALID_IMPORTANCE:
                    error(f"Line {line_no}: importance must be 1, 2, or 3, got {val}")
                else:
                    current_card['importance'] = val
                continue

            # Metadata: mnemonic
            m_mne = MNEMONIC_RE.match(stripped)
            if m_mne:
                current_card['mnemonic'] = m_mne.group(1).strip()
                continue

            # Metadata: hints block start
            if HINTS_START_RE.match(stripped):
                in_hints_block = True
                continue

            # Metadata: hint entry
            if in_hints_block:
                m_hint = HINT_ITEM_RE.match(stripped)
                if m_hint:
                    current_card['hints'].append(m_hint.group(1).strip())
                    continue
                # Loose hint line without "- " (flexibility)
                m_loose = META_LINE_RE.match(stripped)
                if m_loose:
                    current_card['hints'].append(m_loose.group(1).strip())
                    continue
                # Empty line or non-> line ends hints block; fall through to content transition
                in_hints_block = False
                if stripped == '':
                    continue

            # Unknown metadata line (starts with "> ") — warn, consume as metadata
            if stripped.startswith('> '):
                error(f"Line {line_no}: unrecognized metadata (expected importance/mnemonic/hints): "
                       f"{stripped[:60]}")
                continue

            # First non-blank, non-metadata line → transition to CONTENT
            state = 'CARD_CONTENT'
            content_lines.append(raw_line)
            continue

        # ===== CARD_CONTENT =====
        if state == 'CARD_CONTENT':
            if stripped == '---':
                emit_card()
                state = 'BETWEEN_CARDS'
                continue
            m_card = CARD_HEADER_RE.match(stripped)
            if m_card:
                emit_card()
                current_card = new_card(int(m_card.group(1)), m_card.group(2), line_no)
                state = 'CARD_META'
                continue
            # Everything else is content
            content_lines.append(raw_line)

    # ── Don't forget the last card ──
    emit_card()

    # ── Validation ──
    if not result['title']:
        error("No deck title found — add '# Your Deck Title' at the top of cards.md")
    if not result['items']:
        error("No cards found — add '## 1. Card Title' sections after the deck title")
    for card in result['items']:
        if not card['content_full']:
            error(f"Card id={card['id']} ('{card['title'][:40]}') has empty content — "
                   "add answer text after the metadata lines")
        if card['importance'] not in VALID_IMPORTANCE:
            error(f"Card id={card['id']} has invalid importance={card['importance']} "
                   "(must be 1, 2, or 3)")

    if errors:
        print(f"Validation errors in {source_path}:\n", file=sys.stderr)
        for e in errors:
            print(f"  ✗ {e}", file=sys.stderr)
        print(f"\n  {len(errors)} error(s) found. Fix cards.md and re-run.", file=sys.stderr)
        sys.exit(1)

    return result


def convert(source_dir: Path) -> int:
    """Read cards.md from source_dir, write cards.json.  Return 0/1."""
    md_path = source_dir / "cards.md"
    json_path = source_dir / "cards.json"

    if not md_path.exists():
        print(f"Error: {md_path} not found", file=sys.stderr)
        return 1

    text = md_path.read_text(encoding='utf-8')
    data = parse_cards_md(text, str(md_path))

    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    card_count = len(data['items'])
    importance_counts = {1: 0, 2: 0, 3: 0}
    for c in data['items']:
        imp = c['importance']
        if imp in importance_counts:
            importance_counts[imp] += 1
    imp_summary = ", ".join(f"L{i}={importance_counts[i]}" for i in (1, 2, 3))

    print(f"  [OK] cards.md → cards.json ({card_count} cards, {imp_summary})")
    return 0


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Convert recite-coach cards.md to valid cards.json"
    )
    parser.add_argument(
        "target",
        help="Directory containing cards.md (cards.json written to same dir)",
    )
    args = parser.parse_args()
    sys.exit(convert(Path(args.target)))


if __name__ == "__main__":
    main()
