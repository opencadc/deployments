# CI/CD Pipelines

The deployments repository uses GitHub Actions to automate documentation and code quality tasks.

---

## :material-book-open-variant: Documentation Deployment

!!! info "Workflow: `docs.yml`"
    Automatically builds and deploys MkDocs documentation to GitHub Pages.

**Triggers:**

- Pushes to `main` that modify `docs/**`, `mkdocs.yml`, or `pyproject.toml`
- Manual dispatch

**Steps:**

1. Checkout with full git history
2. Install uv package manager
3. Setup Python and dependencies
4. Deploy to gh-pages branch

**Requirements:**

- `contents: write` permission for pushing to `gh-pages` branch
- Dependencies: `mkdocs-material`, `mkdocs-git-revision-date-localized-plugin`

**Deployment Command:**

```bash
uv run mkdocs gh-deploy --force
```

---

## :material-check-circle: Pre-commit Checks

!!! success "Workflow: `pre-commit.yml`"
    Runs pre-commit hooks to ensure code quality and consistency.

**Triggers:**

- Pull requests to `main`
- Manual dispatch

**What it checks:**

- YAML/JSON syntax and formatting
- File permissions and naming
- Security scanning for hardcoded secrets
- Code formatting and quality

**Local Setup:**

```bash
# Install hooks locally
uv run pre-commit install

# Run manually
uv run pre-commit run -a
```

For detailed information about pre-commit hooks, see [Release Cycle: Quality Checks](release-cycle.md#quality-checks-and-cicd).
