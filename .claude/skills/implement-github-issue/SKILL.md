---
name: implement-github-issue
description: Guide end-to-end for implementing an existing GitHub issue — load the issue, understand the code, plan, implement on a dedicated branch, open a PR that links back to the issue, and update the issue. Use whenever the user asks to "work on", "implement", "pick up", "fix" or "resolve" a GitHub issue, or references an issue by number/URL (e.g. "implement #42", "owner/repo#123", "https://github.com/owner/repo/issues/42").
---

# Implement a GitHub issue

This skill turns a GitHub issue into a merged pull request following a disciplined, reviewable workflow. It is designed for the GitHub MCP tools (`mcp__github__*`).

## When to use it

Trigger this skill when the user:

- Asks to implement / work on / pick up / fix / resolve a GitHub issue.
- References an issue by number (`#42`), short ref (`owner/repo#42`), or URL.
- Says things like "start this ticket", "let's tackle this issue", "take this one".

Do **not** trigger this skill for:

- Creating a new issue (different workflow).
- Pure questions about an issue that don't involve code changes.
- Quick read-only triage.

## Required tools

Use the GitHub MCP tools. Do not attempt to use `gh` CLI. Key tools:

- `mcp__github__issue_read` — load the issue, comments, labels.
- `mcp__github__search_code` / `Grep` / `Glob` — locate relevant code.
- `mcp__github__create_pull_request`, `mcp__github__update_pull_request` — open/update PR.
- `mcp__github__add_issue_comment` — post progress comments.
- `mcp__github__issue_write` — transition labels/state if the user wants it closed.

## Workflow

Follow these phases **in order**. Do not skip phases without the user's agreement.

### 1. Load the issue

Always start here. Never implement from memory of the issue.

1. Call `mcp__github__issue_read` with method `get` for the target issue.
2. Also read comments (method `get_comments`) — decisions and clarifications often live there.
3. Extract and summarize for the user:
   - **Goal** (one sentence)
   - **Acceptance criteria** (bullet list — infer them if not explicit)
   - **Scope boundaries** (what's explicitly out of scope)
   - **Labels** (`bug`, `feature`, `good-first-issue`, etc.) — they inform branch prefix and PR type
   - **Linked PRs or issues** — check for prior art or duplicates
   - **Assignees / reviewers** requested

If the issue is ambiguous or contradictory, **stop and ask** before writing code.

### 2. Understand the code

Before planning, explore the codebase:

1. Use `Grep`/`Glob` to find the files, functions, or modules mentioned in the issue.
2. Read those files fully (not just snippets) — understand surrounding code.
3. Identify tests that cover the affected area.
4. Note any project conventions (CLAUDE.md, CONTRIBUTING.md, lint config, commit style).

### 3. Plan and confirm

Produce a **short, concrete plan** and share it with the user before coding:

- Files to create/modify (with paths).
- High-level approach per file.
- Tests to add or update.
- Risks / open questions.
- Commands to verify locally (build, test, lint).

**Wait for explicit user approval** unless the issue is trivial (typo, one-line fix) and the user asked to proceed autonomously. See `references/workflow.md` for edge cases.

### 4. Prepare the branch

1. Create a branch from the default branch using the naming convention in `references/conventions.md`.
   - Format: `<type>/<issue-number>-<kebab-slug>` (e.g. `fix/42-null-pointer-login`, `feat/108-dark-mode`).
2. If a branch already exists for the user's session (check current branch), stay on it — don't switch.
3. Never commit directly to `main`/`master`.

### 5. Implement

- Make the minimum change that satisfies the acceptance criteria. No drive-by refactors.
- Commit in logical units with messages following `references/conventions.md`.
- Run tests, linters, and type-checkers after each meaningful change.
- If you discover the plan is wrong, **pause and revise the plan with the user** — don't silently pivot.

### 6. Verify

Before opening a PR:

- All acceptance criteria met (re-read the issue).
- Tests pass locally.
- Linter / formatter / type-checker clean.
- No stray debug prints, commented-out code, or TODOs you introduced.
- Diff reviewed by you as if you were the reviewer.

### 7. Open the pull request

1. Push the branch: `git push -u origin <branch>`.
2. Create the PR with `mcp__github__create_pull_request`:
   - **Title**: short, imperative, under 70 chars. Include issue number if convention allows.
   - **Body**: use `templates/pr-description.md`. Must contain `Fixes #<number>` (or `Closes #<number>`) so GitHub auto-closes the issue on merge.
   - Target the default branch.
   - Request reviewers from the issue's assignees or the suggested reviewers in CODEOWNERS if present.
3. Do **not** merge the PR yourself unless the user explicitly asks.

### 8. Update the issue

Post a progress comment on the issue using `templates/issue-progress-comment.md`:

- Link to the PR.
- Summarize what was done.
- Flag any remaining sub-tasks or follow-ups.

Do not close the issue manually — let the PR close it on merge via `Fixes #<n>`.

### 9. Offer PR-activity subscription

After the PR is open, proactively ask the user if they want the session to subscribe to PR activity (CI, review comments) via `subscribe_pr_activity`, so you can react to review feedback and CI failures.

## Supporting files

- `references/workflow.md` — edge cases, multi-issue PRs, draft PRs, stacked PRs, hotfixes.
- `references/conventions.md` — branch naming, commit messages, PR titles, labels.
- `templates/pr-description.md` — PR body template.
- `templates/issue-progress-comment.md` — progress-comment template.

## Guardrails

- **Never force-push** to `main`/`master` or to a branch you don't own.
- **Never close an issue directly** — always via the PR.
- **Never push without committing first**, and never commit secrets.
- **Never skip hooks** (`--no-verify`) to make a commit succeed — fix the root cause.
- If the issue has `wontfix`, `duplicate`, or `needs-triage` labels, **stop and confirm** with the user.
- If the PR would touch more than ~500 lines, flag it and propose splitting.
