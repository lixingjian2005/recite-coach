---
name: card-generator
description: Turn study materials (PDF, text, lecture notes, tables) into recite-coach cards. Two-phase pipeline: extract compact score-point memorization lists from raw materials → split them into Q&A cards with mnemonics and hints. Users can skip Phase 1 if their input is already a concise memorization list.
---

# Card Generator

Convert raw study materials into structured card sets (`cards.json`) for the **recite-coach** local spaced-repetition player.

## Two-Phase Pipeline

```
Raw materials (PDF / TXT / MD / pasted text)
    │
    ▼
┌─────────────────────────────────┐
│ Phase 1: SCORE POINTS (optional)│
│ Full lecture notes / textbook   │
│ → score-point memorization list │
│ User can skip if input is       │
│ already concise                 │
└──────────────┬──────────────────┘
               │ score points (markdown)
               ▼
┌─────────────────────────────────┐
│ Phase 2: CARDS                  │
│ Score points → cards.md         │
│ One concept per card:           │
│ Q + A + mnemonic + hints        │
└──────────────┬──────────────────┘
               │ cards.md
               ▼
       deploy-player-kit.py
       (auto-converts to cards.json)
               │
               ▼
       local player launcher
```

## Quick Start

1. Receive user's uploaded file (PDF/TXT/Markdown) or pasted text
2. **Ask:** Is the material already a concise score-point memorization list, or does it need extraction from a longer source?
   - If it needs extraction → go through **Phase 1** first, then **Phase 2**
   - If already concise → skip to **Phase 2** directly
3. Show the final card preview (first 3 cards + summary stats), get user confirmation
4. Write `cards.md` to the output directory
5. Deploy the player kit by running `python recite-coach/assets/deploy-player-kit.py <output-directory>`

## Output Directory and Player Kit

Default output directory: the user's current project root.

If the user explicitly names an output directory, use that directory. Do not default to the PDF's source directory unless the user asks for that.

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

**REQUIRED: After writing `cards.md`, deploy the player kit with this exact command:**

```bash
python recite-coach/assets/deploy-player-kit.py <output-directory>
```

Replace `<output-directory>` with the same directory where you wrote `cards.md`.

The deploy script:
1. Auto-detects `cards.md` and converts it to valid `cards.json` (via `md2cards.py`).
2. Copies all player kit files (`serve.py`, `recite-player.html`, `start.bat`, `start.vbs`, `start.sh`) into the output directory.
3. Validates the output directory is complete.

Do NOT copy files manually. Do NOT write `cards.json` directly — write `cards.md` and let the deploy script handle the conversion.

Do not write generated decks into the installed skill directory. Do not tell the user to hunt for launcher files. The player reads `cards.json` from the same directory as `serve.py`.

## Phase 1: Score-Point Extraction

### When to use

The user provides a **full-length source** — a textbook chapter, lecture PDF, course notes with narration, etc. The material contains filler, repetition, background stories, and explanatory prose mixed with testable content.

**Skip Phase 1** when the user explicitly says their input is already distilled ("these are my study notes, just turn them into cards") or the material is clearly a bullet-point score-point list to memorize.

### Extraction principles

Phase 1 is not a generic summary. Its output should be a compact memorization list that preserves likely scoring points and removes prose that is unlikely to be recited or tested.

**Keep (high testability):**
- Core concept definitions and key terms
- Formulas, laws, theorems (exact wording matters)
- Compare/contrast points ("X vs Y", "difference between...")
- Enumerations ("three characteristics", "four reasons", "five stages")
- Cause-effect chains and logical sequences
- Proper names, dates, classifications that are tested

**Remove / compress:**
- Narrative transitions and filler ("Let us now consider...")
- Redundant examples (keep the most illustrative one)
- Biographical anecdotes unless directly tested
- Commentary and opinion not required for the exam
- Extended background stories

### Output format

Produce a clean markdown score-point list organized by the source material's own chapter/section structure:

```markdown
## Chapter/Section Name

### Topic A
- **Key term:** definition (why it matters)
- Point 1
- Point 2

### Topic B
- **Another term:** definition
- Enumeration: (1) X, (2) Y, (3) Z
```

### User review

Show the extracted score points. Ask the user:
- Any points missed that should be added?
- Any points to remove?
- Any revisions to wording?

Wait for confirmation before moving to Phase 2.

## Phase 2: Card Generation

### Card splitting rules

**One concept per card.** Do not cram multiple independent ideas into one card.

| Content type | How to card |
|---|---|
| Single definition | One card: "What is X?" → definition |
| Enumeration (N items) | One card: "What are the N types of X?" → numbered list |
| Compare/contrast (A vs B) | One card with both sides, structured for clarity |
| Cause → effect chain | One card: "What causes X? What is the result?" |
| Fill-in-blank term | Title uses `____` for the blank: "The ____ is the core of X" |

**Card count guideline:** 1 page of dense notes ≈ 3-5 cards. Don't over-split — a 100-page textbook should yield maybe 30-60 cards, not 300.

### Card fields

```json
{
  "id": 1,
  "title": "Question or concept title",
  "importance": 1,
  "content_full": "Complete answer — key points in numbered list if applicable",
  "mnemonic": "Memory aid — short, catchy",
  "hints": ["Direction hint", "Near-answer hint"]
}
```

#### `title` (the question)
- Short — one concept, one sentence
- For enumerations: "What are the four characteristics of X?"
- For definitions: "X (key concept)"
- For fill-in-blank: "1.2c The ____ of value and ____ of truth"

#### `importance` (priority)
- **1** = Core concept, must-know, frequently tested. Introduced first.
- **2** = Important supporting point, secondary distinction. Introduced mid-session.
- **3** = Supplementary detail, background, nice-to-know. Introduced last.

Guideline: in a typical set, ~40% should be importance=1, ~40% importance=2, ~20% importance=3.

#### `content_full` (the answer)
- Key points only — not full textbook paragraphs
- Use numbered lists for enumerations
- Keep it scannable: the user will read this during review
- Bold or highlight the most critical phrase within (just one)

#### `mnemonic` (memory aid)
- **Chinese materials:** Chinese 口诀 — take the first character of each point and combine, or create a rhyming short phrase. Max 30 characters.
- **English materials:** Acronym, rhyme, vivid association, or word play. Max 15 words.
- If no good mnemonic fits, provide a vivid analogy or mental image instead.
- Leave as empty string `""` only if the concept is so simple it doesn't need one.

#### `hints` (progressive clues)
- 1-3 hints, ordered from vague to specific
- **Hint 1:** Points in the right direction but doesn't reveal the answer (e.g., "Think about the relationship between X and Y")
- **Hint 2 (or last):** Very close to the answer — a keyword or first part (e.g., "The first characteristic is 客...")
- At least 1 hint for importance=1 cards

### Output: `cards.md`

```markdown
# 卡片集标题

> **newItemsPerSession**: 3

---

## 1. What is X?
> importance: 1
> mnemonic: 一三五记心中
> hints:
> - Hint 1
> - Hint 2

X is ...

Key points:
(1) ...
(2) ...
```

- `id`: sequential integer starting from 1 (specified in `## N.`)
- `newItemsPerSession`: batch size, default 3. Use 2 for dense material, 3-4 for lighter material.
- **Never write `---` inside card content.** Describe dividers with words instead.
- **No JSON escaping needed.** Write English `""`, Chinese `""`, or any text directly.
- **Metadata must come before body text.** `> importance:`, `> mnemonic:`, `> hints:` go right after `## N. Title`, before the answer content.

### Workflow

1. **Parse** the score points from Phase 1 (or user's direct input)
2. **Generate cards** following the rules above
3. **Show preview** — first 3 cards fully rendered + summary stats:
   - Total cards: N
   - Importance breakdown: 1: X, 2: Y, 3: Z
   - Title: "XXX"
4. **Ask for confirmation** — user can request edits before writing the file
5. **Write** to `cards.md` (or user-specified filename) in the output directory using the Write tool
6. **Deploy the player kit** by running:
   ```bash
   python recite-coach/assets/deploy-player-kit.py <output-directory>
   ```
   This converts `cards.md` → `cards.json`, copies all 5 player files, and verifies the output. Do NOT skip this step.
   If conversion fails, read the error messages (they include line numbers), fix `cards.md`, and re-run.
7. **Verify** the output directory contains all 7 files:
   `cards.md`, `cards.json`, `serve.py`, `recite-player.html`, `start.bat`, `start.vbs`, `start.sh`

### After generation

Tell the user:
- File saved to: `cards.md` (auto-converted to `cards.json`)
- Player files deployed to the same output directory (verify all 7 files: `cards.md`, `cards.json`, `serve.py`, `recite-player.html`, `start.bat`, `start.vbs`, `start.sh`)
- Launch with `start.bat`, `start.vbs`, `./start.sh`, or `python serve.py`
- Do not recommend directly double-clicking `recite-player.html` as the primary workflow
- They can edit `cards.md` anytime to fix/add/remove cards and re-run the deploy script — the HTML stays unchanged
- Review privacy and copyright before publishing or sharing the deck

## Card Quality Checklist

Before writing the file, verify:
- [ ] Each card has exactly one concept
- [ ] The source material was compressed into score points, not broad prose summary
- [ ] No duplicate or near-duplicate cards
- [ ] `importance` is distributed sensibly (not all 1s or all 3s)
- [ ] Every importance=1 card has at least 1 hint
- [ ] Mnemonics are short and actually helpful (not just restating the title)
- [ ] `content_full` is scannable (lists > paragraphs)
- [ ] IDs are sequential and unique
- [ ] `cards.md` follows the format rules: `---` only as card separator (never inside content), `## N.` header on every card, `> importance:` set on every card, metadata comes before body text
