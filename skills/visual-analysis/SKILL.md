---
name: visual-analysis
description: >-
  Present standalone architecture reviews, complex plans, data comparisons, or
  multi-finding reports as a Cursor Canvas in the GUI (IDE surface). Uses theme
  tokens, built-in charts and structure diagrams, restrained icons. Not loaded
  in CLI/headless; those surfaces follow plugin reporting policy, not this skill.
metadata:
  surfaces:
    - ide
environments:
  - local
---

# Visual analysis

Use when the deliverable is a **standalone analytical artifact** the user will revisit — not inline chat filler.

**Good fits:** architecture reviews, phased implementation plans, data or metrics comparisons, verification summaries with many findings, trade-off matrices.

**Not for:** code fixes, single answers, or work whose deliverable is a PR or file edit.

This skill is scoped to the IDE (`metadata.surfaces: [ide]`, `environments: [local]`). Do not assume it is loaded or executed in CLI/headless sessions.

## GUI: Canvas output

When Canvas is available, produce a `.canvas.tsx` independently from the analysis — the canvas *is* the deliverable, not a screenshot of chat.

1. Create one `.canvas.tsx` file in the workspace canvases directory (Cursor-managed path under `~/.cursor/projects/<workspace>/canvases/`).
2. Import **only** from `cursor/canvas` — no npm packages or relative imports.
3. Default-export the root component; embed data inline (no `fetch`).
4. Use **`useHostTheme()`** for colors — no hardcoded hex.
5. Prefer built-in primitives: cards, sections, tables, callouts, charts, DAG/mermaid-style diagrams where they clarify structure.
6. **Restrained icons** — only when they aid scanning; no decorative emoji or gradient chrome.
7. Label every chart: title, axes with units, legend when multiple series, source/time range caption.
8. Omit empty sections — no placeholder "TODO" panels.

Do **not** duplicate Cursor's canvas SDK reference here. When you need exact component props, read the SDK type declarations under `~/.cursor/skills-cursor/canvas/sdk/` before writing.

## When Canvas is not used

This skill does not run a CLI/headless fallback of its own.

- **Skill not loaded** (CLI / headless): parent orchestration rules and the plugin README prescribe an equivalent structured-markdown report. Follow that policy; do not claim this skill executed or that a canvas was created.
- **IDE, Canvas unavailable:** fall back to the same structured text (headings, tables, lists). State that Canvas was unavailable and the text is the equivalent.

Equivalent shape:

```markdown
## Verdict
…

## Findings
| Area | Severity | Note |
…

## Diagram (text)
…
```

## Tone

Reader-facing, flat, minimal. Lead with the headline finding; details follow.
