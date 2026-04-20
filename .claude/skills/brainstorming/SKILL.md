---
name: brainstorming
description: Sharpen a vague request through a short Socratic dialogue — one question at a time — and return a concise refined spec (problem, motivation, scope, acceptance criteria, alternatives). Use when the user's request lacks a clear "why", success criteria, or scope, or when another skill (e.g. `create-github-issue`) explicitly hands off to sharpen a request before drafting. Do NOT use for already-concrete requests (precise bug repro, tightly scoped chore, pre-designed feature).
---

# Brainstorming a request into a spec

Help turn a rough idea into a concise, unambiguous spec through a short back-and-forth with the user. The output is a **plain-text refined spec** returned in the chat — not a committed design document.

This skill is a slimmed-down adaptation of the `brainstorming` skill from the `superpowers` plugin (MIT, Jesse Vincent). See `NOTICE.md`.

## When to use

Trigger when **any** of these is true:

- The user's request has no clear user problem or motivation.
- A solution is proposed but no alternatives were considered.
- The scope could fit anywhere between a one-line fix and a multi-week project.
- Another skill hands off (typically `create-github-issue`) asking for the request to be sharpened.

Skip when the request is already concrete: precise repro steps for a bug, a tightly scoped chore, or a feature the user has clearly pre-designed.

## What this skill does NOT do

- It does **not** write code, scaffold projects, or invoke implementation skills.
- It does **not** create files or commit anything. The spec is returned in the chat.
- It does **not** chain into another skill automatically. If invoked by `create-github-issue`, control returns to that skill once the spec is ready.

## Workflow

### 1. Quickly frame the context

One or two sentences summarising what the user said and the repo/area it touches. Use `Read` / `Grep` **only** if a file reference is needed to disambiguate — do not dive into the codebase.

### 2. Ask clarifying questions — one at a time

- **One question per message.** Never bundle multiple questions.
- Prefer **multiple-choice** (A / B / C) over open-ended when possible.
- Focus on: the user problem, who is affected, why now, success criteria, hard constraints, out-of-scope items.
- Stop once you have enough to write a spec the user would recognise. Usually 2–5 questions is plenty.

If the request bundles several unrelated concerns, stop and ask the user whether to **split** into separate requests before continuing.

### 3. Propose 2–3 approaches (only if design choice matters)

Skip this step for pure clarifications (bugs, docs, chores). When there's a real design decision:

- Present 2–3 options with one-line trade-offs.
- Lead with your recommendation and why.
- Let the user pick or redirect.

### 4. Present the refined spec

Render the spec in chat using this shape. Scale each section to the complexity — a few sentences is fine for simple requests.

```
**Problem**       — who is affected and what hurts today
**Motivation**    — why now, what's the cost of not doing it
**Proposed shape**— the chosen approach, in 1–3 sentences
**Acceptance criteria** — 2–5 checkable bullets
**Out of scope**  — things deliberately NOT included
**Alternatives considered** — optional; include when step 3 ran
**Open questions** — anything still uncertain; empty is fine
```

Ask the user to confirm or edit. Re-render after edits. **Wait for explicit approval.**

### 5. Hand back

- If invoked by `create-github-issue`: return the approved spec and stop — the calling skill will turn it into a ticket.
- If invoked directly by the user: ask what they want to do with it (file an issue, start implementing, just keep it as notes).

## Key principles

- **One question at a time** — never overwhelm.
- **Multiple choice preferred** — easier to answer than open-ended.
- **YAGNI** — strip anything the user didn't ask for.
- **Explore alternatives** — when a design choice exists, surface 2–3.
- **Incremental validation** — confirm each section before moving on.
- **Stay short** — a good refined spec fits on one screen.

## Guardrails

- **No implementation work.** Never edit source files, create branches, or open PRs from this skill.
- **No file writes.** The spec lives in the chat.
- **No auto-chaining** to other skills beyond returning to the caller.
- **Respect the user's wording.** Keep their technical terms in the spec.
- **One request per session.** If the user describes several, propose splitting.
