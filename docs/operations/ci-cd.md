# CI/CD Pipelines

The deployments repository uses GitHub Actions to automate routine tasks.

## Documentation Deployment (`docs.yml`)

- Triggers on pushes to `main` that touch `docs/**` or `mkdocs.yml`, and can be run manually.
- Installs MkDocs with the Material theme and publishes the rendered site to the `gh-pages` branch using `mkdocs gh-deploy --force`.
- Requires `contents: write` permission for the workflow to push updates.

## Release Automation (`release-please.yml`)

- Runs on a weekly schedule, on demand, and whenever `main` changes.
- Uses Google's Release Please action in manifest mode to open a release PR.
- When the PR merges it tags the repo, updates `CHANGELOG.md`, and publishes GitHub release notes.

## Release Images (`release-images.yml`)

- Fires on the `published` release event or manually.
- Resolves build settings from `release-images.json` via `scripts/generate_release_matrix.py`.
- Builds each Docker image with Buildx, pushes to `images.canfar.net`, and signs the digests with Cosign.
- Supports multi-platform builds by specifying `platforms` in the configuration file.

## Adding New Images

1. Drop a Dockerfile into the repository (for example `configs/example/Dockerfile`).
2. Append a new entry to `release-images.json` specifying the registry, context, dockerfile path, and optional static tags (for example `latest`).
3. Verify the image builds locally with the desired build arguments.
4. Commit the changes and ensure the release pipeline completes successfully after the next tagged release.

## Secrets

The image publishing workflow expects these repository secrets to exist:

- `CANFAR_HARBOR_ROBOT_PUBLISHER_USERNAME`
- `CANFAR_HARBOR_ROBOT_PUBLISHER_SECRET`

If the secrets change, rotate them in GitHub before cutting the next release.
