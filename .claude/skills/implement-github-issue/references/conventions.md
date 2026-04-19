# Conventions

These are the default conventions. If the repository has a `CONTRIBUTING.md`, `CLAUDE.md`, or observable patterns in recent commits/PRs that contradict these defaults, **follow the repository's conventions instead**.

## Branch naming

Format: `<type>/<issue-number>-<kebab-slug>`

| Type    | When to use                             | Example                                |
| ------- | --------------------------------------- | -------------------------------------- |
| `feat`  | New user-facing feature                 | `feat/108-dark-mode-toggle`            |
| `fix`   | Bug fix                                 | `fix/42-null-pointer-login`            |
| `chore` | Tooling, CI, deps, no behaviour change  | `chore/77-bump-eslint-9`               |
| `docs`  | Documentation only                      | `docs/53-clarify-install-steps`        |
| `refactor` | Internal refactor, no behaviour change | `refactor/91-extract-auth-service`   |
| `test`  | Adding or fixing tests only             | `test/66-cover-password-reset`         |
| `perf`  | Performance improvement                 | `perf/120-memoize-product-list`        |

Rules:

- Slug: lowercase, dashes only, ~3–6 words, no stop words.
- Never include ticket titles verbatim — summarize.
- If the repo uses a different prefix scheme (e.g. `username/...`), follow it.

## Commit messages

Use Conventional Commits unless the repo clearly uses another style:

```
<type>(<optional-scope>): <imperative summary>

<optional body explaining the *why*, wrapped at 72 chars>

Refs #<issue-number>
```

- `<type>` matches the branch type (`feat`, `fix`, …).
- Summary: imperative mood, lowercase, no trailing period, ≤ 72 chars.
- Body: explain *why*, not *what* (the diff shows the what).
- Footer: `Refs #<n>` on every commit; `Fixes #<n>` only on the commit that resolves the issue (or in the PR body).

Examples:

```
fix(auth): reject empty password on login

The login handler accepted an empty string because the presence check
ran before trim(). Users could bypass the length rule by sending
whitespace-only passwords.

Refs #42
```

```
feat(ui): add dark mode toggle to settings

Refs #108
```

## Pull request titles

Same rules as commit summaries:

- Imperative, lowercase, ≤ 70 chars.
- Prefix with type if the repo uses Conventional PR titles.
- Do **not** embed the issue number in the title unless the repo convention requires it — the PR body handles linking.

Good: `fix(auth): reject empty password on login`
Bad: `Fixed bug where login accepted empty password (fixes #42)`

## Labels

Apply labels that match the issue:

- Carry over `bug` / `enhancement` / `documentation` from the issue.
- Add `ready-for-review` when leaving draft state, if the repo uses it.
- Add `needs-tests` if you deliberately deferred test coverage (and flag in PR body).

## Reviewers

- Request reviewers from the issue's assignees first.
- Fall back to `CODEOWNERS` entries for the touched paths.
- If neither exists, leave unassigned and mention it in the PR body.

## Line-count targets

- Aim for < 400 changed lines per PR.
- At 400–800 lines, flag it and justify.
- Over 800 lines, propose splitting before opening.
