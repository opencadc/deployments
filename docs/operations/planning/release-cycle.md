# Release Cycle and Process

## Fixed Quarterly Releases

CANFAR follows a **fixed, quarterly release cycle** (e.g., 2025.1, 2025.2) to provide predictable updates and stable deployments.

## Challenges with Collaboration Support

While quarterly releases provide stability, they present challenges for collaborations that need early access to features:

- **SRCNet Integration**: Updated components (cadc-registry, cavern, prepareData) need to be integrated before official release
- **Research Collaborations**: Some projects require pre-release access to new features

## Current Solution: Edge Images

### For Production Deployments

```bash
helm upgrade canfar opencadc/skaha
```

- Uses official helm charts pointing to release images (e.g., `skaha:1.0.2`)
- Gets latest stable release plus bug fixes only
- No access to unreleased features

### For Pre-Release Testing

To preview new features before official release, manually modify helm charts to use 'edge' images:

```yaml
image:
  repository: images.opencadc.org/platform/skaha
  tag: edge
```

This gives deployers access to the latest development code for testing purposes.

## Feature Flags/Gates (Planned)

Feature flags will be used to control features not yet released.

### Example Workflow

1. Feature flag (or functionality discovery process) is used to support the new code path
2. Code is merged to "edge" branch
3. Image is built and published, overwriting the image labeled with 'edge'
4. Regular `helm upgrade` does **not** get the image with this feature flag
5. Deployers who want this feature must modify the images in their helm charts manually

This approach will provide:
- Early access for collaborations (e.g., SRCNet) to specific features
- Safer testing of new functionality
- Flexibility for pre-release integration
