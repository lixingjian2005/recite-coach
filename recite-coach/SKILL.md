---
name: recite-coach
description: Turn study material into score-point memorization cards for local browser review. Use when users say "帮我背诵", "帮我记住", "整理踩分点", "生成背诵卡片", "quiz me on", "drill this content", or upload exam prep materials.
---

# Recite Coach

Recite Coach is a two-part workflow:

1. Use this skill and the included `card-generator` sub-skill to turn PDF, lecture notes, textbooks, tables, or pasted text into a compact score-point memorization list, then into `cards.json`.
2. Use the local player launcher to review `cards.json` as flashcard-style hand cards.

The skill creates and validates the deck. The local web app reads the deck and runs the memorization session.

## Output Directory Rule

Always create the final review package in the user's current project root, unless the user explicitly specifies another output directory.

Do not default to the PDF's source directory. A PDF may live in Downloads, a temp folder, or a course-material folder that is not the working project.

The final output directory must contain:

```text
cards.md              (you write this — see format below)
cards.json            (auto-generated from cards.md)
recite-player.html
serve.py
start.bat
start.vbs
start.sh
```

**REQUIRED — After writing `cards.md`, you MUST deploy the player kit.**  
Run this command exactly:

```bash
python recite-coach/assets/deploy-player-kit.py <output-directory>
```

Replace `<output-directory>` with the same directory where you wrote `cards.md`.

The deploy script:
1. Auto-detects `cards.md` and converts it to valid `cards.json` (via `md2cards.py`).
2. Copies all 5 player kit files into the output directory.
3. Validates the output directory is complete.

Do NOT manually copy individual player kit files one by one. Do NOT write `cards.json` directly — write `cards.md` and let the deploy script handle the conversion.

This player kit is the stable launch entry for generated decks. Do not ask the user to find launcher files manually, and do not write `cards.json` into the installed skill directory.

## When to Use

Use this skill when the user wants to:

- turn a full PDF, lecture handout, textbook chapter, or note set into memorization cards;
- compress long material into exam-oriented score points;
- generate a `cards.json` deck for Recite Coach;
- drill existing `cards.json` content in the local player.

## Overall Workflow

### Path A: User already has concise points or `cards.json`

If the user already has `cards.json`, skip generation and explain how to launch the local player.

If the user has a concise memorization list but no JSON, skip extraction and use the card-generation phase only.

### Path B: User has PDF, lecture notes, textbook material, or long notes

Use `recite-coach/card-generator/SKILL.md`.

The required two-stage pipeline is:

1. **Score-point extraction**: full material -> compact score-point memorization list.
2. **Card generation**: score-point list -> `cards.md`.

Do not treat Phase 1 as a generic summary. It must remove filler and keep testable, recitable, scoring content.

## Card Data Format

Cards are authored as **structured markdown** (`cards.md`). The deploy script automatically converts `cards.md` to valid `cards.json` — you never write JSON by hand. This eliminates JSON quoting issues (Chinese/English quotation marks, unescaped quotes) completely.

### Markdown Template

```markdown
# Deck Title Here

> **newItemsPerSession**: 3

---

## 1. Question or concept title
> importance: 1
> mnemonic: Short memory aid (optional)
> hints:
> - First hint (optional)
> - Second hint (optional)

Answer content here. Plain text or markdown.

Supports **bold**, *italic*, `code`, $math$.

Can span multiple paragraphs.
No JSON escaping — "" "" all fine.

---

## 2. Another concept
> importance: 2
...
```

### Format Rules

**Deck-level:**
- `# <text>` (first h1) → deck title (required)
- `> **newItemsPerSession**: N` → batch size (optional, default 3)

**Cards:**
- `---` on a line by itself → separates cards
- `## N. <text>` → card with id=N, question title (required)
- `> importance: N` → 1=core, 2=important, 3=supplemental (required, default 1)
- `> mnemonic: <text>` → memory aid (optional, default "")
- `> hints:` followed by `> - <text>` lines → progressive hints (optional)
- Everything else between `## N.` and the next `---` → answer content (supports inline markdown)

### Critical Rules

- **Never use `---` inside card content.** If content needs a divider, describe it with words.
- **No JSON quoting needed.** Write English `""`, Chinese `""`, or any text directly.
- **Metadata comes first.** `> importance:`, `> mnemonic:`, and `> hints:` must appear before body text.
- **Content supports markdown.** `**bold**`, `*italic*`, `` `code` ``, `$math$` are rendered by the player.

## Local Player Launch Instructions

After `cards.md` has been written and the deploy script has converted it to `cards.json` and copied the player kit, tell the user the exact output directory and launch method.

Windows:

```bat
start.bat
```

or double-click `start.vbs` to avoid a visible console window.

macOS / Linux:

```bash
./start.sh
```

Universal:

```bash
python serve.py
```

`recite-player.html` is the player file, not the recommended launch entry. Do not tell the user to directly double-click it as the primary workflow, because `file://` mode may not reliably load the latest `cards.json` and does not provide the same file-backed progress behavior.

The launcher reads `cards.json` from its own directory. This is why `cards.json`, `serve.py`, `recite-player.html`, and the start scripts must be placed together.

## Scheduling Model

The local player uses a 5-box Leitner-style system:

| Box | Meaning |
|-----|---------|
| 0 | New, not introduced yet |
| 1 | Just learned or missed |
| 2 | Getting familiar |
| 3 | Comfortable |
| 4 | Nearly mastered |
| 5 | Mastered |

Rating behavior:

- `1` / Again: reset for quick review.
- `2` / Hard: reset for quick review.
- `3` / Good: promote gradually.
- `4` / Easy: promote faster.

The exact scheduling is implemented in `recite-player.html`; the deck remains plain JSON.

## Quality Checklist

Before delivering a deck:

- The extracted list contains score points, not a broad prose summary.
- Each card tests one concept or one tightly connected scoring point.
- IDs are sequential and unique.
- Important cards have at least one useful hint.
- Answers are concise enough to review quickly.
- Mnemonics help recall rather than restating the title.
- `cards.md` follows the format rules above: `---` only as card separator, `## N.` header on every card, `> importance:` set on every card, no `---` inside content.

## Safety Notes

Remind the user when relevant:

- `cards.json` may contain private study material.
- Do not publish private notes, copyrighted textbook excerpts, exam dumps, or personal information.
- `.recite-progress.json` is local study progress and should not be shared or committed.

## Suggested Response After Creating Cards

Tell the user:

- where `cards.md` was saved (and that it was converted to `cards.json`);
- where the player kit was copied;
- deck title and card count;
- that they should launch with `start.bat`, `start.vbs`, `./start.sh`, or `python serve.py`;
- that `cards.template.json` can restore the demo deck format;
- to review privacy/copyright content before publishing any deck.
