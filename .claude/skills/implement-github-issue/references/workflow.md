# Workflow — edge cases

This document covers situations the main `SKILL.md` workflow does not handle directly.

## Trivial issues (typos, one-line fixes)

If the issue is a typo, a comment fix, or a clearly-scoped one-line change:

- Skip the explicit plan-approval step.
- Still load the issue, open a branch, open a PR linking the issue.
- Keep the commit message and PR body short but correct.

## Ambiguous or stale issues

If the issue:

- Was opened more than 12 months ago with no recent activity, **or**
- Has contradictory comments (e.g. discussion changed the scope), **or**
- References files/APIs that no longer exist,

then **pause** and ask the user for clarification before planning. Propose what you think the current intent is and wait for confirmation.

## Multi-issue PR

If a single change naturally closes several issues:

- Reference all of them in the PR body: `Fixes #12`, `Fixes #13`, `Closes #14` (one per line — GitHub only parses separate keywords).
- Comment on each issue with a link to the PR.
- Mention in the PR description why they are bundled.

Prefer **one PR per issue** when issues are logically independent.

## Stacked / dependent PRs

If the work depends on another PR that isn't merged yet:

- Branch off the dependency's branch, not `main`.
- In the PR body, add `Depends on #<PR number>` and mark the PR as **draft** until the base is merged.
- After the base merges, rebase onto `main` and mark ready for review.

## Draft PRs

Open as draft when:

- You want CI feedback before finishing.
- The work will take multiple sessions and you want early reviewer input.
- Acceptance criteria are still being negotiated with the issue author.

Use `mcp__github__create_pull_request` with `draft: true`.

## Hotfixes

For issues labelled `hotfix` / `critical` / `P0`:

- Branch off the current release branch if one exists (not `main`).
- Keep the diff minimal — no refactors.
- Add `hotfix` to the PR labels.
- Ping the on-call reviewer in the PR body.

## Follow-up work

If during implementation you discover additional problems that are **out of scope**:

- Do **not** fix them in the same PR.
- Note them in the PR body under a `## Follow-ups` section.
- Offer to open separate issues after the PR is merged.

## Reverting a merged PR

If the user asks to revert a merged PR that closed an issue:

- Open the revert PR with `Reopens #<n>` in the body (GitHub does not auto-reopen, so also manually reopen via `issue_write` after merge).
- Add a comment on the original issue explaining why the fix was reverted.

## Handling review feedback

When subscribed to PR activity:

- For each review comment, decide: (a) apply the suggestion, (b) push back with reasoning, or (c) ask the user.
- For CI failures, read the logs, diagnose the root cause, fix, and push a new commit.
- Never force-push on a PR under review unless explicitly allowed — prefer fixup commits.
