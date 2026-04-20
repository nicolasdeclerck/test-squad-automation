# Attribution

This `brainstorming` skill is a slimmed-down adaptation of the `brainstorming`
skill from the **superpowers** plugin by Jesse Vincent.

- Upstream: https://github.com/obra/superpowers
- Upstream file: `skills/brainstorming/SKILL.md`
- License: MIT

Changes from the upstream version:

- Scope narrowed to "sharpen a request into a short spec" (not a full design
  process before any creative work).
- Removed the visual companion (browser-based mockup tool) and all
  associated scripts.
- Removed the hand-off to the `writing-plans` skill — this skill returns the
  spec in chat and stops (or hands back to `create-github-issue` when called
  from there).
- Removed the on-disk design-doc step (`docs/superpowers/specs/...`).
- Simplified checklist and spec template.

## Upstream license

```
MIT License

Copyright (c) 2025 Jesse Vincent

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```
