# Contributing

Contributions are welcome.

## Useful Areas

- Improve the HTML player UI or scheduling behavior.
- Add small public-domain or original example decks.
- Improve card-generation guidance in `recite-coach/` (card-generator SKILL.md, the `cards.md` markdown format, or the `md2cards.py` converter).
- Fix launcher behavior across Windows, macOS, and Linux.
- Improve documentation and setup notes.

## Deck Guidelines

Example decks should be safe to publish:

- Use original content, public-domain content, or short educational examples.
- Do not submit private notes, copyrighted textbook excerpts, exam dumps, or personal study progress.
- Keep cards compact and scannable.
- Use sequential integer IDs starting from 1.

## Local Private Files

Private decks should use names like:

- `my-course.local.md` (authoring format) / `my-course.local.json` (generated)
- `private-exam-notes.md` / `private-exam-notes.json`

These are ignored by the default `.gitignore`.
