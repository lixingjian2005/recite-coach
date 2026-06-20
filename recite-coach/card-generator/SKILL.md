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
│ Score points → cards.json       │
│ One concept per card:           │
│ Q + A + mnemonic + hints        │
└──────────────┬──────────────────┘
               │ cards.json
               ▼
       local player launcher
```

## Quick Start

1. Receive user's uploaded file (PDF/TXT/Markdown) or pasted text
2. **Ask:** Is the material already a concise score-point memorization list, or does it need extraction from a longer source?
   - If it needs extraction → go through **Phase 1** first, then **Phase 2**
   - If already concise → skip to **Phase 2** directly
3. Show the final card preview (first 3 cards + summary stats), get user confirmation
4. Write `cards.json` to the project directory

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

### Output: `cards.json`

```json
{
  "title": "卡片集标题",
  "newItemsPerSession": 3,
  "items": [
    {
      "id": 1,
      "title": "What is X?",
      "importance": 1,
      "content_full": "X is ...\n\nKey points:\n(1) ...\n(2) ...",
      "mnemonic": "一三五记心中",
      "hints": ["Hint 1", "Hint 2"]
    }
  ]
}
```

- `id`: sequential integer starting from 1
- `newItemsPerSession`: how many new cards to introduce per batch. Default 3. Use 2 for very dense/difficult material, 3-4 for lighter material.

### Workflow

1. **Parse** the score points from Phase 1 (or user's direct input)
2. **Generate cards** following the rules above
3. **Show preview** — first 3 cards fully rendered + summary stats:
   - Total cards: N
   - Importance breakdown: 1: X, 2: Y, 3: Z
   - Title: "XXX"
4. **Ask for confirmation** — user can request edits before writing the file
5. **Write** to `cards.json` (or user-specified filename) using the Write tool

### After generation

Tell the user:
- File saved to: `cards.json`
- To use: put `cards.json` in the project root next to `serve.py`
- Launch with `start.bat`, `start.vbs`, `./start.sh`, or `python serve.py`
- Do not recommend directly double-clicking `recite-player.html` as the primary workflow
- They can edit the JSON anytime to fix/add/remove cards — the HTML stays unchanged
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
- [ ] The JSON is valid (no trailing commas, proper escaping)
