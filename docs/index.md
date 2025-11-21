# CANFAR Deployments

Welcome to the operational documentation for deploying and maintaining the CANFAR Science Platform. This repository contains Helm charts, Kubernetes configurations, CI/CD automation, and operations runbooks that power the platform infrastructure.

## What You'll Find Here

This documentation is designed for **platform operators, DevOps engineers, and infrastructure maintainers** who deploy, configure, and manage CANFAR services.

<div class="grid cards" markdown>

- :material-kubernetes: **Helm Charts**

    Reusable deployment templates for CANFAR services with configurable values and environment overlays.

- :material-rocket-launch: **Release Automation**

    Automated CI/CD pipelines using GitHub Actions and Release Please for Helm chart versioning.

- :material-file-document: **Operations Runbooks**

    Step-by-step procedures for releases, rollbacks, monitoring, and troubleshooting production deployments.

- :material-cog: **Configuration Management**

    Environment-specific overlays, secrets management, and Kubernetes resource definitions for staging and production.

- :material-book-open-variant: **Documentation**

    Automated MkDocs site deployment with operations guides and platform runbooks.

- :material-shield-check: **Code Quality**

    Pre-commit hooks, linting, and security scanning for infrastructure-as-code.

</div>

## Quick Links

- [**Helm Charts Documentation**](helm/index.md) - Explore reusable Helm charts for CANFAR services
- [**CI/CD Pipelines**](operations/ci-cd.md) - Understand GitHub Actions workflows for documentation and code quality
- [**Release Process**](operations/release-process.md) - Follow the Helm chart release process and CANFAR platform schedule
- [**GitHub Repository**](https://github.com/opencadc/deployments/) - Browse source code, Helm charts, and configurations

## Getting Started

If you're new to CANFAR deployments:

1. Familiarize yourself with the [Helm Charts Documentation](helm/index.md) to understand service deployments
1. Review the [Release Process](operations/release-process.md) to understand our deployment workflow
1. Explore the [CI/CD Pipelines](operations/ci-cd.md) documentation to see how automation works
1. Check the [GitHub repository](https://github.com/opencadc/deployments/) for Helm charts and configuration files

## Contributing

This is an operational repository for CANFAR platform infrastructure. Changes follow the standard pull request workflow with Release Please automation for versioning and changelog generation.

For questions or support, contact the CADC operations team or visit the [main CANFAR documentation](https://www.opencadc.org/canfar/).
