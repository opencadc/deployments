# Contributing to CANFAR Deployments

Thank you for your interest in contributing to the CANFAR Science Platform infrastructure! This repository manages Helm charts, Kubernetes configurations, and deployment automation for the CANFAR platform.

!!! tip "Quick Links"
    - **[Release Cycle Guide](operations/release-cycle.md)** - Complete release pipeline and workflows
    - **[Code of Conduct](https://github.com/opencadc/.github/blob/main/CODE_OF_CONDUCT.md)** - Community guidelines
    - **[Report Issues](https://github.com/opencadc/deployments/issues)** - Bug reports and feature requests

---

## Getting Started

### Prerequisites

- **uv** package manager - [Installation guide](https://docs.astral.sh/uv/getting-started/installation/)
- **Git** with conventional commits knowledge
- **Helm** (for chart development)
- **Kubernetes** access (for testing deployments)

### Setup

!!! example "Initial Setup Steps"

    1. **Fork and clone the repository:**
       ```bash
       git clone https://github.com/YOUR_USERNAME/deployments.git
       cd deployments
       ```

    2. **Install pre-commit hooks:**
       ```bash
       uv run pre-commit install
       ```

    3. **Create a feature branch:**
       ```bash
       git checkout -b fix/your-issue
       # or
       git checkout -b feat/your-feature
       ```

---

## How to Contribute

### :material-bug: Reporting Bugs

Found a bug? [Open an issue](https://github.com/opencadc/deployments/issues/new) with:

- Clear description of the problem
- Steps to reproduce
- Expected vs actual behavior
- Environment details (cluster, helm version, etc.)

### :material-wrench: Fixing Bugs

!!! success "Bug Fix Workflow"

    1. Create a descriptive branch:
       ```bash
       git checkout -b fix/session-timeout
       ```

    2. Make changes and commit:
       ```bash
       git commit -m "fix: resolve session timeout in skaha"
       ```

    3. Push and create PR:
       ```bash
       git push origin fix/session-timeout
       ```

:octicons-arrow-right-24: See [Bug Fix Scenario](operations/release-cycle.md#scenario-1-fixing-a-bug) for release process details.

### :material-plus-circle: Adding Features

!!! success "Feature Development Workflow"

    1. Create a feature branch:
       ```bash
       git checkout -b feat/gpu-support
       ```

    2. Implement and commit:
       ```bash
       git commit -m "feat: add GPU resource allocation support"
       ```

    3. Push and create PR

:octicons-arrow-right-24: See [Feature Scenario](operations/release-cycle.md#scenario-2-adding-a-feature-for-next-release) for release details.

---

## Commit Message Format

!!! info "Conventional Commits"
    We use [Conventional Commits](https://www.conventionalcommits.org/) for automatic changelog generation.

**Commit Types:**

| Type | Description | Release Impact |
|------|-------------|----------------|
| `feat:` | New features | Minor version bump |
| `fix:` | Bug fixes | Patch version bump |
| `docs:` | Documentation changes | No version bump |
| `chore:` | Maintenance tasks | No version bump |
| `ci:` | CI/CD changes | No version bump |

**Examples:**

```bash
git commit -m "feat: add limit range configuration to skaha chart"
git commit -m "fix: correct redis connection string in cavern"
git commit -m "docs: update helm chart deployment instructions"
```

---

## Pre-commit Checks

!!! warning "Automatic Validation"
    Pre-commit hooks run automatically before each commit to ensure code quality.

**What's checked:**

- Helm chart linting and validation
- YAML/JSON syntax
- Security scans (gitleaks)
- Conventional commit format

**Run manually:**

```bash
uv run pre-commit run -a
```

If checks fail on your PR, follow the automated guidance to fix issues locally.

---

## Pull Request Process

!!! note "PR Checklist"

    1. ✅ Ensure all pre-commit checks pass
    2. ✅ Update documentation if needed
    3. ✅ Reference related issues in PR description
    4. ✅ Wait for review from maintainers
    5. ✅ Address any feedback
    6. ✅ Maintainer will merge once approved

---

## Release Process

**Automated versioning based on commit types:**

- **Patch release** (`1.0.2` → `1.0.3`) - Bug fixes
- **Minor release** (`1.0.3` → `1.1.0`) - New features
- **Major release** (`1.1.0` → `2.0.0`) - Breaking changes

Release Please automates version bumping and changelog generation.

:octicons-book-24: **[Complete Release Documentation](operations/release-cycle.md)**

---

## Questions?

!!! question "Need Help?"

    - :fontawesome-brands-discord: **Discord**: [CANFAR Community](https://discord.gg/vcCQ8QBvBa)
    - :material-email: **Email**: support@canfar.net
    - :fontawesome-brands-github: **Issues**: [GitHub Issues](https://github.com/opencadc/deployments/issues)

---

## License

By contributing, you agree that your contributions will be licensed under the same license as the project (AGPL-3.0).
