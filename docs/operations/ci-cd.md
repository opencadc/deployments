# CI/CD Pipelines

The deployments repository uses GitHub Actions to automate documentation and code quality tasks.

## Documentation Deployment (`docs.yml`)

Automatically builds and deploys the MkDocs documentation site to GitHub Pages.

### Triggers

- Pushes to `main` that modify `docs/**`, `mkdocs.yml`, or `pyproject.toml`
- Manual dispatch with required reason field

### Workflow Steps

1. **Checkout**: Fetches full git history (required for git-revision-date plugin)
2. **Install uv**: Sets up the uv package manager
3. **Setup Python**: Installs Python using uv
4. **Install dependencies**: Runs `uv sync` to install all dependencies from `pyproject.toml`
5. **Deploy**: Runs `uv run mkdocs gh-deploy --force` to build and publish to `gh-pages` branch

### Requirements

- `contents: write` permission for pushing to `gh-pages` branch
- Dependencies managed in `pyproject.toml`:
  - `mkdocs-material` - Material theme for MkDocs
  - `mkdocs-git-revision-date-localized-plugin` - Git revision dates in docs

## Pre-commit Checks (`pre-commit.yml`)

Runs pre-commit hooks on all files to ensure code quality and consistency.

### Triggers

- Pull requests to `main`
- Manual dispatch

### What it checks

- YAML syntax and formatting
- JSON formatting
- File permissions and naming
- Security scanning for hardcoded secrets
- Python code quality (if applicable)
