# CHANGELOG for Science Portal UI (Chart 1.0.0)

## [1.1.0](https://github.com/opencadc/deployments/compare/scienceportal-1.0.0...scienceportal-1.1.0) (2025-10-10)


### Features

* add limit range configuration and update docs ([4eaf993](https://github.com/opencadc/deployments/commit/4eaf993b33da03033d6fa83638791fea61d3b088))
* add tolerations to apis and uis to allow fine grained node deployment ([a2ba229](https://github.com/opencadc/deployments/commit/a2ba2291ffc4cbb41cf47b0d6f1376c8ec64d3d7))
* new portal update for storage info ([386a4b7](https://github.com/opencadc/deployments/commit/386a4b738bf8e87bccdf5d52e458bd679520f87c))
* new portal update for storage info ([9a5f081](https://github.com/opencadc/deployments/commit/9a5f08103aaa6821f18e718536880c26cbb1d10a))
* support pod security context ([0b1cb74](https://github.com/opencadc/deployments/commit/0b1cb7490c93bc66f7df37dd7a82ff1ae2c9b4a3))
* use release namespace ([16cc82a](https://github.com/opencadc/deployments/commit/16cc82aff143a13e5913d27e53d9d33195b5caec))


### Bug Fixes

* add redis updates for cve fix and skaha limit range object ([e8c02c0](https://github.com/opencadc/deployments/commit/e8c02c0e780d7eeebceed6c237e409d5fc84dba5))
* add science portal chart ([19cec86](https://github.com/opencadc/deployments/commit/19cec867d09b0fc62829234fc499e3580f62d33b))
* add science portal chart ([ab1d891](https://github.com/opencadc/deployments/commit/ab1d8915b1ffaa3f2ca119d0e92abec605049462))
* add storage ui chart with security fixes ([9d3af7c](https://github.com/opencadc/deployments/commit/9d3af7c8b1ff197adfade1615a7b0fc1868dbdff))
* add storage ui chart with security fixes ([016f3cc](https://github.com/opencadc/deployments/commit/016f3cced6d4925f5fddbb7f581d96a459ba4765))
* add timeouts to kill warnings ([9658a11](https://github.com/opencadc/deployments/commit/9658a117bafefcb41f56e3f5ed2c97515e3339be))
* disable specific experimental features ([33586a6](https://github.com/opencadc/deployments/commit/33586a676b80696dcd89c75cd09b1e002e3b8c82))
* documentation link updates ([70411d8](https://github.com/opencadc/deployments/commit/70411d8afdc2382bbf81663da3f65465417f7873))
* documentation link updates ([7264452](https://github.com/opencadc/deployments/commit/72644529e631bdb97efd86926f99812b2eaa477c))
* fix for helm versions ([543bd8e](https://github.com/opencadc/deployments/commit/543bd8ee065b4ed07c37108c2efdc0faf54babbb))
* properly set the experimental feature if configured ([f9843a2](https://github.com/opencadc/deployments/commit/f9843a22c6f7d69e1f9c001643ccd9834aad8f5b))
* specific experimental feature settings ([223f48b](https://github.com/opencadc/deployments/commit/223f48b771732c3f0147a493b92f294be3035d69))
* use proper indent ([86fe85a](https://github.com/opencadc/deployments/commit/86fe85a95eab9615085104d9ae16c4882d79e6af))
* version revert to remove accidentally released portal change and fix client secret setting ([73f9639](https://github.com/opencadc/deployments/commit/73f96398de23d1f3363f462b71f1d7399a8b33a6))
* version revert to remove accidentally released portal change and… ([ce78285](https://github.com/opencadc/deployments/commit/ce782855d1e1100a73fc1d116e5b867d7f78e737))

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
