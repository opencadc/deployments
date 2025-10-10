# Release Process

Documentation for releasing Helm charts and platform configuration for the CANFAR Science Platform.

## CANFAR Release Cycle

The CANFAR Science Platform uses a version format `YYYY.Q` for quarterly releases:

- **2025.1** - Q1 2025 release
- **2025.2** - Q2 2025 release

Between releases, **hotfix patches** may be released as needed for critical issues.

## Helm Chart Releases

Each Helm chart in this repository is versioned independently:

- Charts follow semantic versioning (`MAJOR.MINOR.PATCH`)
- Release Please automation manages changelog and version bumps
- Each chart has its own release cycle and `CHANGELOG.md`

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

### 4. Deployment

After release PR is merged:

- Git tag is created automatically
- GitHub release is published with changelog
- Deploy to staging environment first
- Run validation and smoke tests
- Deploy to production after successful validation

## Hotfix Process

For critical issues requiring immediate patches:

1. Create `hotfix/<issue>` branch from affected release tag
2. Apply fix and create PR to `main`
3. Release Please generates patch release PR
4. Follow standard review and merge process
5. Deploy hotfix after testing

## Pre-deployment Checklist

Before deploying a Helm chart release:

- ✅ Review CHANGELOG for all changes
- ✅ Verify chart values match intended configuration
- ✅ Check for breaking changes or migrations
- ✅ Ensure dependent services are compatible
- ✅ Prepare rollback plan

## Rollback Strategy

If issues are detected after deployment:

1. Roll back to previous Helm chart version
2. Document issue and root cause
3. Create hotfix branch to address problem
4. Follow hotfix process for patch release
