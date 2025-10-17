# Release Cycle and Process

## Fixed Quarterly Releases

CANFAR follows a **fixed, quarterly release cycle** (e.g., 2025.1, 2025.2) to provide predictable updates and stable deployments.

## Release Pipeline Overview

The CANFAR release pipeline follows this flow:

```
Source Code -> Container Images -> Harbor Registry -> Helm Charts -> Deployment
```

### 1. Source Code

Application source code lives in component repositories:
- **skaha**: Session management and batch processing
- **cavern**: Storage services
- **science-portal**: Web UI
- **posix-mapper**: User mapping service

Each repository follows conventional commits for automatic changelog generation.

### 2. Container Images

When code is merged to `main`:

**Production Images (Release Tags)**
```bash
# Tagged with semantic versions
images.opencadc.org/platform/skaha:1.0.2
images.opencadc.org/platform/cavern:0.7.1
```

**Edge Images (Pre-release)**
```bash
# Tagged with 'edge' for latest development code
images.opencadc.org/platform/skaha:edge
images.opencadc.org/platform/cavern:edge
```

Images are built via CI/CD and pushed to Harbor.

### 3. Harbor Registry

Container images are stored in the Harbor registry at `images.opencadc.org`:

- **Organization**: `platform/` for core services
- **Versioning**: Semantic versioning tags (e.g., `1.0.2`)
- **Pre-release**: `edge` tag for development builds
- **Access**: Authentication required for pushing images

### 4. Helm Charts

Helm charts in the [opencadc/deployments](https://github.com/opencadc/deployments/) repository define how services are deployed to Kubernetes:

```yaml
# Example: helm/applications/skaha/values.yaml
image:
  repository: images.opencadc.org/platform/skaha
  tag: "1.0.2"  # Pinned to specific release
```

Charts follow semantic versioning independently from application images:
- Chart version: `1.2.3` (Helm chart changes)
- App version: `1.0.2` (Application image version)

### 5. Deployment

Deployers use helm charts to install services:

```bash
# Production: uses release images
helm upgrade skaha opencadc/skaha

# Pre-release testing: manually override to edge
helm upgrade skaha opencadc/skaha \
  --set image.tag=edge
```

## Working with Different Scenarios

### Scenario 1: Fixing a Bug

!!! success "Bug Fix Workflow"
    **Patch release for the current version**

**Steps:**

1. **Create a PR with conventional commit**
   ```bash
   git checkout -b fix/session-timeout
   # Make changes
   git commit -m "fix: resolve session timeout issue"
   # Pre-commit hooks run automatically (if installed)
   git push origin fix/session-timeout
   ```

2. **After PR is merged to `main`**
   - CI builds a new image with `edge` tag
   - Release Please detects the `fix:` commit
   - Creates/updates a release PR with a patch version bump (e.g., `1.0.2` → `1.0.3`)

3. **When the release PR is merged**
   - Git tag is created (e.g., `v1.0.3`)
   - CI builds and pushes image with version tag: `images.opencadc.org/platform/skaha:1.0.3`
   - Helm chart's appVersion is updated to `1.0.3`

4. **Deployment**
   ```bash
   helm upgrade skaha opencadc/skaha
   ```

---

### Scenario 2: Adding a Feature for Next Release

!!! tip "Feature Development Workflow"
    **Minor release for the upcoming quarterly release (e.g., 2025.2)**

**Steps:**

1. **Create a PR with feature commit**
   ```bash
   git checkout -b feat/gpu-sessions
   # Implement feature
   git commit -m "feat: add GPU session support"
   # Pre-commit hooks run automatically (if installed)
   git push origin feat/gpu-sessions
   ```

2. **After PR is merged**
   - Image is built with `edge` tag immediately
   - Release Please queues a minor version bump (e.g., `1.0.3` → `1.1.0`)
   - Feature is available for testing via edge images

3. **Pre-release testing**
   ```bash
   # Deploy with edge image to test feature
   helm upgrade skaha opencadc/skaha --set image.tag=edge
   ```

4. **At quarterly release time**
   - Release Please PR is merged
   - Version tag created (e.g., `v1.1.0`)
   - Official release includes the feature

---

### Scenario 3: Adding a Feature for Future Release

!!! question "Future Feature Development"
    **For features not ready for the next quarterly release**

**Current Approach:**

Features merged to `main` will appear in `edge` images and be included in the next release.

**Future Enhancement: Feature Flags**

Feature flags are being considered to provide finer control over when features become available:

- Features could be merged with flags that control activation
- Deployers could selectively enable features via configuration
- Features would remain disabled by default until ready for general release

**This would allow:**

- Early access for specific collaborations (e.g., SRCNet)
- Safe testing in production without affecting all users
- Gradual rollout of new functionality

!!! note
    Implementation details are still being determined. For the latest on feature flag support, contact the CANFAR development team.

## Quality Checks and CI/CD

Before code is merged, automated checks ensure quality and consistency across the codebase.

### Pre-commit Hooks

The deployments repository uses pre-commit hooks to validate changes before they're committed:

<div class="grid cards" markdown>

- :material-kubernetes: **Helm Chart Validation**

    - Chart syntax and best practices (`helmlint`)
    - Auto-generated documentation (`helm-docs`)
    - Maintainer information updates
    - Chart inventory refresh

- :material-code-braces: **Code Quality**

    - Trailing whitespace removal
    - File formatting consistency
    - Syntax validation (JSON, YAML, TOML, XML)
    - Executable shebang validation

- :material-shield-lock: **Security Scanning**

    - Hardcoded secrets detection (`gitleaks`)
    - Private key detection
    - Credential leak prevention

- :material-message-check: **Commit Standards**

    - Conventional commit format (`commitizen`)
    - Automatic changelog generation
    - Version bump determination

</div>

### Developer Setup

Install pre-commit hooks locally for automatic validation:

```bash
# One-time setup - runs hooks before each commit
uv run pre-commit install

# Manually run all hooks
uv run pre-commit run -a

# Run hooks on all files
uv run pre-commit run --all-files
```

### GitHub Actions Integration

When you open a pull request, GitHub Actions automatically:

1. Runs all pre-commit checks
2. Provides helpful feedback if checks fail:
   - Instructions to reproduce locally
   - Links to relevant documentation
   - Commands to fix common issues
3. Celebrates successful checks ✨

If pre-commit checks fail on your PR, follow the guidance in the automated comment to fix issues locally before pushing again.

## Versioning Strategy

**Application Images:**
- Follow semantic versioning: `MAJOR.MINOR.PATCH`
- `MAJOR`: Breaking changes
- `MINOR`: New features (backward compatible)
- `PATCH`: Bug fixes

**Helm Charts:**
- Versioned independently from applications
- Track infrastructure/configuration changes
- Each chart has its own `CHANGELOG.md`

**Example:**
```yaml
# Chart.yaml
version: 1.2.3        # Helm chart version
appVersion: "1.0.4"   # Application image version
```

## Edge Images for Pre-Release Testing

Edge images provide access to the latest development code:

**For Production:**
```bash
helm upgrade canfar opencadc/skaha
# Uses: images.opencadc.org/platform/skaha:1.0.4
```

**For Pre-Release Testing:**
```yaml
# custom-values.yaml
image:
  tag: edge

# Deploy
helm upgrade canfar opencadc/skaha -f custom-values.yaml
# Uses: images.opencadc.org/platform/skaha:edge
```

⚠️ **Warning:** Edge images are rebuilt frequently and may contain unstable features. Use only for testing purposes.
