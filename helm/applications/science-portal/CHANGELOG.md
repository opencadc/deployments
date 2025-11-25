# CHANGELOG for Science Portal UI (Chart 1.1.1)

## 2025.11.25 (1.1.1)
- Use `Release.Namespace` for installation rather than separate `namespace` value.

## 2025.11.17 (1.0.4)
- Fix: Remove running instances counts due to severe ineffieciency.
- Fix: Use `view=interactive` to only query inteactive sessions for the UI.

## 2025.10.31 (1.0.3)
- Feature: Add experimental slider feature gate
  - Add `experimentalFeatures.slider` section to `values.yaml` to enable/disable the slider feature.

## 2025.10.27 (1.0.2)
- Add configuration for default project to pre-select in the pull-down menu.

## 2025.09.09 (1.0.0)
- Official release
- Add Cavern portal information
- Fixed vs flex sessions

## 2025.08.21 (0.7.1)
- Fix: New documentation links

## 2025.06.20 (0.7.0)
- Small fix to enable experimental features in the `values.yaml` file.

## 2025.06.17 (0.6.4)
- Small fix for deploying with an existing secret for the client.
- **EXPERIMENTAL**: Added `experimentalFeatures` to feature-flag user storage quota display.

## 2025.05.09 (0.6.0)
- Add support for Firefly sessions
- Drop suport for JDK 1.8.

## 2025.04.15 (0.5.1)
- Add `tolerations` feature for `science-portal` UI.  Redis values can be added in the `redis` sub-chart stanza.
  - See https://github.com/opencadc/deployments/issues/29

## 2024.12.11 (0.5.0)
- Added support for `securityContext`
- Added support to rename application to change endpoint (`applicationName`)

## 2024.12.04 (0.4.0)
- Select by project enabled to constrain images in pull-down menu
- Add Advanced tab to enable proprietary image support

## 2024.09.05 (0.2.11)
- Fix screen blanking when image selection not yet loaded
- Remove all (or most) warnings in Browser Console

## 2024.06.24 (0.2.7)
- Fix to use tokens for APIs on a different host.

## 2023.12.11 (0.2.2)
- OpenID Connect login support

## 2023.11.25 (0.1.2)
- Properly report a missing configuration for a Skaha API
- Application version correction to make in line with `main` branch

## 2023.11.02 (0.1.1)
- Fix remote registry lookup from JavaScript in favor of server side processing (Bug)
- Code cleanup
