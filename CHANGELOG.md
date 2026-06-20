# Changelog

All notable changes to this project will be documented in this file.

## 0.2.0 - 2026-06-20

- **Markdown authoring format.** LLMs now write `cards.md` (structured markdown) instead of `cards.json` directly. A new `md2cards.py` converter produces valid JSON, eliminating quoting errors (Chinese/English quotation marks, unescaped quotes) completely.
- `deploy-player-kit.py` now auto-detects `cards.md` and runs the converter before copying player files. Use `--force` to regenerate `cards.json` from an updated `cards.md`.
- Updated SKILL instructions to reflect the markdown-first workflow.

## 0.1.0 - 2026-06-20

- Initial public release.
- Added standalone `recite-player.html` Leitner-style memorization player.
- Added Python-based local launcher `serve.py`.
- Added Windows and Unix startup scripts.
- Added default `cards.json` demo deck and `cards.template.json` backup template.
- Added sample decks under `example-cards/`.
- Added `recite-coach` and `card-generator` skill instructions.
