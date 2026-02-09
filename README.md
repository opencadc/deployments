# OpenCADC Deployments

This repository contains Helm charts and CI/CD automation for deploying services at the Canadian Astronomy Data Centre (CADC), including the CANFAR Science Platform.

## Architecture

The repository implements a fully automated release and deployment pipeline:

- **Helm Charts** - Kubernetes deployments for platform services (`helm/applications/`) and shared libraries (`helm/common/`)
- **Automated Releases** - Release-Please manages semantic versioning and changelogs for each chart independently
- **Secure Publishing** - Helm charts are published to OCI registries with keyless signing (Sigstore/Cosign) and build attestations
- **Dependency Management** - Renovate automatically updates dependencies, container images, and chart `appVersion` fields
- **Documentation** - Comprehensive operational guides and runbooks for platform operators

## Managed Charts

<!-- CHART-INVENTORY:START -->
This section is automatically generated. Do not edit manually.

| Chart | Description |
| --- | --- |
| [base](helm/applications/base) | A Helm chart to install base components of the CANFAR Science Platform |
| [science-portal](helm/applications/canfar-next/science-portal) | A Helm chart for Science Portal Next.js application |
| [cavern](helm/applications/cavern) | A Helm chart to install the VOSpace User Storage API (Cavern) |
| [posixmapper](helm/applications/posix-mapper) | A Helm chart to install the UID/GID POSIX Mapper |
| [reg](helm/applications/reg) | IVOA Registry Service Helm Chart |
| [argus](helm/applications/sandbox/argus) | An IVAO TAP Helm chart |
| [bifrost](helm/applications/sandbox/bifrost) | A Helm chart for Kubernetes |
| [sc2meta](helm/applications/sandbox/sc2meta) | A Helm chart for Kubernetes |
| [search](helm/applications/sandbox/search) | A Helm chart for the Search User Interface browser application |
| [stack](helm/applications/sandbox/stack) | A Helm chart for the SC2 Sandbox Stack |
| [torkeep](helm/applications/sandbox/torkeep) | A CAOM-2 Metadata Repository Helm Chart |
| [scienceportal](helm/applications/science-portal) | A Helm chart to install the Science Portal UI |
| [skaha](helm/applications/skaha) | A Helm chart to install the Skaha web service of the CANFAR Science Platform |
| [sshd](helm/applications/sshd) | An SSHD service with SSSD to get users from LDAP |
| [storageui](helm/applications/storage-ui) | A Helm chart to install the User Storage UI |
| [utils](helm/applications/utils) | A library Helm chart for common tasks |
<!-- CHART-INVENTORY:END -->

Charts are managed via [`.release-please-manifest.json`](.release-please-manifest.json) for automated versioning and releases.

## Verification

Helm charts are signed using keyless signing with [Sigstore](https://www.sigstore.dev/) and [Cosign](https://github.com/sigstore/cosign) with [Rekor](https://github.com/sigstore/rekor) transparency logs and [GitHub Attestations](https://github.blog/2023-09-22-github-attestations/) for build provenance.

To verify a chart, at `oci://images.opencadc.org/platform/skaha:1.2.3`, run:

```bash
# Install Cosign
brew install cosign

# Set experimental mode for keyless verification
export COSIGN_EXPERIMENTAL=1
cosign verify --certificate-identity-regexp="https://github.com/opencadc/deployments" --certificate-oidc-issuer="https://token.actions.githubusercontent.com" images.opencadc.org/platform/skaha:1.2.3
```

To verify the provenance of where the chart came from, e.g. the build pipeline, environment variables, etc., run:

```bash
gh auth login
gh attestation verify oci://images.opencadc.org/platform/skaha:1.2.3 --owner opencadc
```


## Adding a New Chart

To add a new Helm chart to the repository:

### 1. Create Chart Structure

```bash
# Create chart directory
mkdir -p helm/applications/<chart-name>
cd helm/applications/<chart-name>

# Initialize chart
helm create . --starter <starter-chart>  # or manually create Chart.yaml, values.yaml, templates/
```

### 2. Configure Chart.yaml

Add the Renovate marker comment before `appVersion` to enable automatic version updates:

```yaml
# Chart.yaml
apiVersion: v2
name: my-chart
description: "Description of my chart"
type: application
version: 0.1.0

# renovate: image=<registry>/<repository>/<image-name>
appVersion: "1.0.0"
```

**Example:**

```yaml
# renovate: image=images.opencadc.org/platform/my-service
appVersion: "1.0.0"
```

This enables Renovate to automatically update `appVersion` when the container image version changes.

### 3. Add README.md.gotmpl

Create a `README.md.gotmpl` template for auto-generated documentation:

```gotmpl
{{ template "chart.header" . }}

{{ template "chart.description" . }}

| Chart | AppVersion | Type |
|:-----:|:----------:|:----:|
|{{ template "chart.version" . }}<!-- x-release-please-version --> | {{ template "chart.appVersion" . }} | {{ template "chart.type" . }} |

{{ template "chart.homepageLine" . }}

{{ template "chart.requirementsSection" . }}

{{ template "chart.valuesSection" . }}
```

The `<!-- x-release-please-version -->` comment is required for Release-Please to update the version in the generated README.md.

### 4. Register Chart for Release Management

Add the chart to `.release-please-manifest.json`:

```json
{
  "helm/applications/<chart-name>": "0.1.0"
}
```

### 5. Pass Pre-commit Checks

```bash
# From repository root
uv run pre-commit run --all-files
```

### 6. Commit and Create PR

```bash
git add helm/applications/<chart-name>
git add .release-please-manifest.json
git commit -m "feat(helm): add <chart-name> chart"
git push origin <branch-name>
```

Once merged, Release-Please will automatically:

- Create a release PR when changes are detected
- Generate/update CHANGELOG.md
- Publish the chart to the OCI registry with keyless signing
- Create GitHub releases with build attestations
