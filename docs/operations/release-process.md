# Release Process

> Captures the release playbook agreed upon during the CANFAR deployment retrospective. Follow this checklist whenever we cut a release so platform configuration, container images, and documentation move forward together.

## Goals

- Ship predictable releases with clear ownership and audit trails.
- Keep Helm charts, Kubernetes overlays, and related container images in lock-step.
- Capture validation evidence (tests, environment sign-off, deployment notes) directly in GitHub.

## Roles

| Role | Responsibilities |
| --- | --- |
| **Release Steward** | Drives the checklist, owns the Release Please PR, coordinates sign-off. |
| **Component Owners** | Review service-specific changes, validate configuration diffs, update docs. |
| **Operations** | Deploys tagged artifacts to staging/production, monitors telemetry, handles rollbacks. |
| **Communications** | Publishes stakeholder updates and customer-facing announcements. |

## Cadence & Branching Model

- `main` remains the integration branch; all work merges via pull requests.
- Releases follow semantic versioning (`MAJOR.MINOR.PATCH`).
- Release automation relies on **Release Please**. When merged, the Release Please PR tags the repo and publishes the GitHub release notes.
- Hotfixes branch from the latest release tag, then merge back into `main` through a fast-follow patch release.

## Pre-release Checklist

1. ✅ Confirm PR labels are accurate (`type:*`, `documentation`, `breaking-change`, etc.).
2. ✅ Ensure environment overlays and Helm values are up to date with the intended rollout.
3. ✅ Verify `configs/` and `helm/` tests or linters pass in CI.
4. ✅ Review open issues labeled `release-blocker` or `production-impact` and close or defer them.
5. ✅ Draft release notes sections (Highlights, Infrastructure Changes, Known Issues).
6. ✅ Validate `release-images.json` reflects the container images that should be rebuilt.

## Creating a Release

1. Dispatch or wait for the scheduled **Release Please** workflow.
2. Review the generated pull request:
   - Confirm the semver bump matches the scope of changes.
   - Ensure the changelog entry is clear and complete.
   - Double-check that configuration-only changes are represented accurately.
3. Obtain all required approvals (Release Steward plus relevant component owners).
4. Merge the Release Please PR to publish the release tag and GitHub release notes.

## Post-tag Automation

Once the tag exists, the following workflows activate automatically:

| Workflow | Purpose |
| --- | --- |
| `release-images.yml` | Builds and pushes the container images defined in `release-images.json`. Each image receives the release tag plus any static tags (for example `latest`). |
| `docs.yml` | Rebuilds and deploys this MkDocs site to `gh-pages`. |

If a job fails, pause the rollout, remediate the issue, then re-run the job from the GitHub Actions UI to ensure consistency between the tagged source and published artifacts.

## Post-release Verification

1. Monitor the `Release Images` workflow for success and review build provenance.
2. Deploy the updated Helm charts or configuration overlays to staging, then production.
3. Run smoke tests covering login, storage access, workload scheduling, and monitoring dashboards.
4. Update stakeholder channels (status page, release notes, operations chat) with deployment status.
5. Capture lessons learned or follow-ups in the retrospective tracking issue and update this document if the process changes.

## Rollback & Hotfix Strategy

- If a regression is detected, roll back to the previous deployment and revert the release tag if necessary.
- Create a `hotfix/<issue>` branch from the impacted tag, apply the fix, and let Release Please generate the follow-up patch release PR.
- Re-run `release-images.yml` for the patched tag to guarantee the container registry is consistent.

## Reference

- `release-images.json` — declarative list of container build definitions.
- `.github/workflows/release-please.yml` — schedules Release Please automation.
- `.github/workflows/release-images.yml` — publishes container images on release tags.
- `.github/workflows/docs.yml` — deploys the MkDocs documentation to GitHub Pages.

Keep this playbook current by reviewing it after each retrospective.
