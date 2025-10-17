# Helm Chart Releases

Documentation for releasing Helm charts in the CANFAR deployments repository.

## Overview

Each Helm chart in this repository is versioned independently:

- Charts follow semantic versioning (`MAJOR.MINOR.PATCH`)
- Release Please automation manages changelog and version bumps
- Each chart has its own release cycle and `CHANGELOG.md`

## CANFAR Release Cycle

The CANFAR Science Platform uses a version format `YYYY.Q` for quarterly releases:

- **2025.1** - Q1 2025 release
- **2025.2** - Q2 2025 release

Between releases, hotfix patches may be released as needed for critical issues.

## Branching Model

- `main` is the integration branch - all work merges via pull requests
- Use conventional commits for automatic changelog generation
- Hotfixes branch from the latest release tag and merge back to `main`

## Release Workflow

### 1. Making Changes

- Create a pull request to `main`
- Use conventional commit messages (e.g., `feat:`, `fix:`, `docs:`)
- Add appropriate labels for changelog categorization
- Ensure all CI checks pass

### 2. Release Please Automation

Release Please automatically:

- Detects changes to Helm charts
- Determines version bump based on conventional commits
- Updates `CHANGELOG.md` and `Chart.yaml`
- Creates a release PR for each affected chart

### 3. Review and Merge

- Review the generated changelog and version bump
- Verify Helm chart values and configuration
- Obtain required approvals
- Merge the release PR to create tags and GitHub releases

### 4. Release

After release PR is merged:

- Git tag is created automatically
- GitHub release is published with changelog

## Chart Structure

Each application chart follows this structure:

```
helm/applications/skaha/
├── Chart.yaml           # Chart metadata and version
├── CHANGELOG.md        # Auto-generated changelog
├── values.yaml         # Default configuration
├── templates/          # Kubernetes manifests
└── README.md          # Auto-generated documentation
```

## Versioning

**Chart Version:**
- Incremented based on chart template/configuration changes
- Independent from application version

**App Version:**
- References the container image version
- Updated when application code changes

Example:
```yaml
# Chart.yaml
version: 1.2.3        # Helm chart version
appVersion: "1.0.4"   # Application image version
```

See [Release Cycle](release-cycle.md) for the complete CANFAR platform release pipeline including container image builds and deployment workflows.
