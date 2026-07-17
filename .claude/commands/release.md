---
description: Prepares a release - version bump in pyproject.toml and standardized commit
argument-hint: [patch|minor|major]
allowed-tools: Read, Edit, Bash(git *)
---

Prepare a backend release (bump type: $ARGUMENTS — default: patch):

1. Read the current version in `backend/pyproject.toml`.
2. Compute the new version (project pattern: `0.1.X` series, patch bump).
3. Update the `version` field in `pyproject.toml`.
4. Confirm with `git diff` that only the version changed and commit:
   `chore: Bump version to {new_version} in pyproject.toml`
   (English message, semantic tag — see `.claude/rules/git-workflow.md`).
5. Report the previous version, the new one and the commit hash. Do not push without an explicit request.
