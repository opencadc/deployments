# Changelog

## [0.2.0] (unreleased)

- Rename `application.registryEntries` to `application.localAuthorities` (cadc-registry local authority map).
- Rename `application.registryURL` to `application.registryUrls` (array of RegistryClient base URLs).
- Rename `localAuthorities[].standardID` to `standardId` (camelCase).
- Rename `application.gmsID`, `oidcURI`, `resourceID`, `cdpResourceID`, `allowBasicATP` to `gmsId`, `oidcUri`, `resourceId`, `cdpResourceId`, `allowBasicAtp` (Helm values only; Java property names unchanged).
- Deduplicate and de-skaha `values.yaml` exports.standard defaults.
- Merge `library/utils` templates into `common` (`common.*` defines).
- Drop unused `configmap.filesAsConfig` / `publicHostname` helpers.
- Single library dependency for values (`exports.standard`) and shared templates.

## [0.1.0]

- Initial `exports.standard` default values for Tomcat application charts.
