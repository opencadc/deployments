# Science Portal Helm Chart

## Dependencies

- An existing Kubernetes cluster (1.29+).
- An IVOA Registry (See the [Current SKAO Registry](https://spsrc27.iaa.csic.es/reg))
- A working `skaha` web service deployed and registered in the IVOA Registry.

## Install

The Science Portal is a Single Page Application (SPA) with a rich Javascript client and DOM manager.  It uses React to power the various Dashboard elements, and is configurable for different OpenID Providers (OIdP).

### Minimum Helm configuration

See the full set of options in the [values.yaml](https://github.com/opencadc/science-platform/blob/SP-3544/deployment/helm/science-portal/values.yaml).  The deployed Redirect URI (`redirect_uri`) is `/science-portal/oidc-callback`, which handles
receiving the `code` as part of the authorization code flow, and obtaining a token to put into a cookie.

### Run with configured values

```bash
helm repo add science-platform https://images.opencadc.org/chartrepo/science-platform
helm repo update

helm --namespace skaha-system upgrade --install --values my-science-portal-local-values-file.yaml science-portal science-platform/scienceportal

Release "science-portal" has been installed. Happy Helming!
NAME: science-portal
LAST DEPLOYED: Thu Oct 19 11:59:15 2024
NAMESPACE: skaha-system
STATUS: deployed
REVISION: 7
TEST SUITE: None
```

## Authentication & Authorization

A&A is handle by caching the Token Set server side and issuing a cookie to the browser to enable secure retrieval.  See the [Application Authentication Documentation](../../../docs/authentication/).

## Endpoints

The system will be available at the `/science-portal` endpoint, (i.e. https://example.com/science-portal).  Authenticating to the system is mandatory.

<!--
Include the generated README from the Helm chart for reference.
-->
--8<-- "helm/applications/science-portal/README.md"
