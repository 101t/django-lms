# Contributing

Thanks for helping improve Django LMS!

1. Fork the repo and create a branch from `master`.
2. Set up the project with `uv sync` (see "Local development" in the README).
3. Make your change. Add or update tests in the app's `tests.py`.
4. Make sure these pass:
   ```bash
   uv run python manage.py test
   uv run ruff check . && uv run ruff format --check .
   uv run python manage.py makemigrations --check --dry-run
   ```
5. Open a pull request describing what changed and why.

Please keep the codebase small and readable: prefer Django's built-in features over new dependencies.
Report security issues privately to the maintainers rather than in public issues.
