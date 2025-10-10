# Operations

Operational guides and runbooks for managing CANFAR platform infrastructure, releases, and deployments.

## Overview

This section provides comprehensive documentation for platform operators managing CANFAR deployments. Whether you're releasing new versions, troubleshooting issues, or maintaining infrastructure, these guides will help you follow best practices and ensure reliable operations.

<div class="grid cards" markdown>

- [:material-pipe: __CI/CD Pipelines__ <small>GitHub Actions workflows</small>](ci-cd.md)
- [:material-rocket-launch-outline: __Release Process__ <small>Release playbook and procedures</small>](release-process.md)

</div>

## Key Responsibilities

### Release Management

- Coordinate releases using Release Please automation
- Review and merge release PRs with proper approvals
- Monitor post-release workflows and verify deployments
- Manage hotfixes and rollback procedures when needed

### Infrastructure Operations

- Deploy Helm charts and configuration overlays
- Manage environment-specific configurations (staging, production)
- Monitor platform health and respond to incidents
- Maintain secrets and access controls

### CI/CD Maintenance

- Keep GitHub Actions workflows up to date
- Monitor workflow runs and troubleshoot failures
- Update documentation and configuration files

## Tools & Technologies

The CANFAR deployment infrastructure relies on:

- **Kubernetes** - Container orchestration platform
- **Helm** - Package manager for Kubernetes applications
- **GitHub Actions** - CI/CD automation and workflows
- **Release Please** - Automated release management and changelog generation
- **MkDocs Material** - Documentation site generation
- **uv** - Python package and dependency management

## Getting Help

For operational support or questions:

- Check the relevant runbook in this documentation
- Review recent GitHub Actions workflow runs for error logs
- Contact the CADC operations team
- Consult the [main CANFAR documentation](https://www.opencadc.org/canfar/)

## Best Practices

1. **Always follow the release checklist** - Skip no steps to ensure consistent, reliable releases
2. **Test in staging first** - Validate changes in staging before promoting to production
3. **Monitor post-deployment** - Watch metrics and logs after every deployment
4. **Document incidents** - Capture lessons learned and update runbooks
5. **Keep secrets secure** - Rotate credentials regularly and limit access
6. **Maintain audit trails** - All changes go through pull requests with proper reviews