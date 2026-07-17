---
description: Code review of pending changes following the project rules
allowed-tools: Bash(git status), Bash(git diff *), Bash(git log *), Read, Grep, Glob
---

Review the pending changes (working tree + staged) in this repository:

1. Run `git status` and `git diff` to gather what changed.
2. Check compliance with the project rules:
   - `.claude/rules/code-style.md` (Clean Architecture, formatting only in the domain, parameterized SQL, source code in English)
   - `.claude/rules/security.md` (secrets, CORS, input validation)
   - `.specs/` whenever the change touches specified behavior
3. For report templates: check the 842×595 px dimensions, centering and the absence of number formatting in the template.
4. Report findings ordered by severity (bug > rule violation > improvement), citing `file:line`. If everything is fine, say so explicitly.
