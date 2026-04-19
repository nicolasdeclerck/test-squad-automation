---
name: create-github-issue
description: Create a new GitHub issue — gather context, draft a well-structured ticket (title, body, labels, assignees), confirm with the user, then open it via the GitHub MCP. Use ONLY when the user explicitly asks to create / open / file a new issue or ticket (e.g. "create an issue for X", "open a ticket about Y", "file a bug", "crée un ticket", "ouvre une issue"). Do NOT trigger when the user wants to implement, work on, fix, or resolve an EXISTING issue — that is handled by `implement-github-issue`.
---

# Create a GitHub issue

This skill helps the user file a high-quality GitHub issue from a free-form request. It uses the GitHub MCP tools (`mcp__github__*`). It never writes code, never creates a branch, and never opens a pull request — its single output is a new issue on GitHub.

## When to use it

Trigger this skill **only** when the user explicitly asks to **create a new issue/ticket**. Typical signals:

- "Create an issue for …"
- "Open a ticket about …"
- "File a bug / feature request …"
- "Ouvre / crée une issue / un ticket …"
- "Add this to the backlog as an issue"

### Do NOT trigger this skill when

- The user asks to **implement / work on / pick up / fix / resolve** an existing issue → use `implement-github-issue` instead.
- The user references an existing issue by number or URL without asking to create a new one → likely `implement-github-issue` or a read-only answer.
- The user wants to **comment** on an issue → use `mcp__github__add_issue_comment` directly, no skill needed.
- The user wants to **close / reopen / relabel** an existing issue → use `mcp__github__issue_write` directly, no skill needed.

If the request is ambiguous ("let's track this somewhere"), **ask the user** whether they want a new issue created before invoking this skill.

## Boundary with `implement-github-issue`

| Intent signal                                 | Skill                      |
| --------------------------------------------- | -------------------------- |
| "create / open / file / crée / ouvre" + issue | **create-github-issue**    |
| "implement / work on / fix / resolve" + #ref  | `implement-github-issue`   |
| Both signals in the same request              | Ask the user which one first — normally **create first, implement after**. |

Never chain into `implement-github-issue` automatically after creating the ticket. Ask the user if they want to proceed with implementation as a separate step.

## Required tool

- `mcp__github__issue_write` with method `create` — the only write this skill performs.

Helpful read-only tools to prepare the issue:

- `mcp__github__list_issues` / `mcp__github__search_issues` — check for duplicates.
- `mcp__github__get_label` — verify labels exist on the repo before applying them.
- `mcp__github__get_teams` / `mcp__github__get_me` — resolve assignees if the user names them.
- `Grep` / `Glob` / `Read` — pull concrete file references or line numbers from the local repo to cite in the issue body.

## Workflow

Follow these phases in order. Keep each one short — the goal is a good ticket, not a novel.

### 1. Capture the user's intent

Summarize back to the user in one sentence:

- **Type**: bug, feature, chore, docs, question, etc.
- **Target repository**: default to the current repository (`nicolasdeclerck/skills-assessment`) unless the user names another. **Never** create an issue on a repo outside the authorized scope.
- **Rough subject**: what the issue is about.

If any of the three is unclear, ask **one** clarifying question before continuing.

### 2. Gather context (lightweight)

Do the minimum needed to write a useful issue:

- For a **bug**: reproduction steps, expected vs. actual behaviour, environment, a file:line reference if the user has hinted at where it lives.
- For a **feature**: user-facing goal, motivation, a rough acceptance criteria list.
- For a **chore / refactor / docs**: scope and motivation.

Optionally run one or two `Grep`/`Read` calls to anchor the issue in real file paths — but do not dive deep. If you find yourself reading more than 2–3 files, stop: that's implementation territory, not ticket drafting.

### 3. Check for duplicates

Call `mcp__github__search_issues` with a short query derived from the subject (state `open`). If a plausible duplicate exists:

- Show the user the top 1–3 matches (number, title, state).
- Ask whether to proceed anyway, comment on the existing issue instead, or abort.

### 4. Draft the issue

Produce a draft using `templates/issue-body.md`. Required fields:

- **Title** — imperative, ≤ 70 chars, no issue-number prefix, no trailing period. Examples:
  - `login accepts empty password`
  - `add dark mode toggle to settings`
  - `document postgres migration path`
- **Body** — filled-in template (see below).
- **Labels** — only labels that already exist on the repo. If unsure, leave empty and note it.
- **Assignees** — only if the user named someone explicitly.

Show the full draft to the user (title, body, labels, assignees) and **wait for explicit approval** before creating. Accept small edits in-place; re-show the draft after edits.

### 5. Create the issue

Once approved, call `mcp__github__issue_write` with method `create`:

- `owner` / `repo` — target repository.
- `title` — from the draft.
- `body` — the rendered template.
- `labels` — array of existing label names, or omit.
- `assignees` — array of GitHub logins, or omit.

Return the new issue's URL and number to the user.

### 6. Offer next steps (do not auto-chain)

After creation, ask the user if they want to:

- Implement the issue now → hand off to `implement-github-issue` **only on explicit confirmation**.
- Add extra comments, link related issues, or adjust labels.
- Nothing further — stop.

## Supporting files

- `templates/issue-body.md` — the issue body template, with bug / feature / chore variants.

## Guardrails

- **Scope lock**: only create issues on repositories in the authorized scope. Refuse others and tell the user why.
- **No implementation work**: never create a branch, never edit source files, never open a PR from this skill.
- **No auto-labelling**: only apply labels that already exist on the repo — check with `mcp__github__get_label` or `mcp__github__list_issues` if unsure.
- **No duplicates without acknowledgement**: always run the duplicate check in step 3.
- **Respect the user's wording**: keep the user's technical terms in the title and body; do not rename their feature.
- **One issue per call**: if the user describes multiple distinct problems, propose splitting into separate tickets rather than bundling.
- **Never close or modify unrelated issues** as part of this workflow.
