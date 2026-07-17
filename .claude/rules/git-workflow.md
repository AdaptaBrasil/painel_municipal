# Git Workflow

- Commit messages **always in English**, with a semantic tag: `feat:`, `fix:`, `style:`, `docs:`, `refactor:`, `chore:`, `test:`.
- Short imperative/descriptive subject; details in the body when needed.
- One commit per logical change — do not mix refactors with features.
- Main branch: `master`. Working directly on master is accepted in this project (single maintainer), but large features should use a dedicated branch.
- Never commit: `.env`, database dumps, generated PDFs, heavy `local_data/` content.
- Release: version bump in `backend/pyproject.toml` (`0.1.X` pattern) in its own commit (`feat:` or `chore:`).
