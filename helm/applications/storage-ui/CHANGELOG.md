# Storage User Interface Helm Chart (0.6.0)

## [0.8.0](https://github.com/opencadc/deployments/compare/storageui-0.7.0...storageui-0.8.0) (2025-10-10)


### Features

* add tolerations to apis and uis to allow fine grained node deployment ([a2ba229](https://github.com/opencadc/deployments/commit/a2ba2291ffc4cbb41cf47b0d6f1376c8ec64d3d7))
* allow configuration of manage group links ([d2a4288](https://github.com/opencadc/deployments/commit/d2a4288318b66244484ab3195cace659ffc38f41))
* allow setting images for those defaulting to docker io ([da0d2e7](https://github.com/opencadc/deployments/commit/da0d2e7fbcf90639adc83a47b0517de827929399))
* allow setting images for those defaulting to docker io ([97574c2](https://github.com/opencadc/deployments/commit/97574c274c1bf459951d21edbcf539a0abfe0398))


### Bug Fixes

* add redis updates for cve fix and skaha limit range object ([e8c02c0](https://github.com/opencadc/deployments/commit/e8c02c0e780d7eeebceed6c237e409d5fc84dba5))
* add storage ui chart with security fixes ([9d3af7c](https://github.com/opencadc/deployments/commit/9d3af7c8b1ff197adfade1615a7b0fc1868dbdff))
* add storage ui chart with security fixes ([016f3cc](https://github.com/opencadc/deployments/commit/016f3cced6d4925f5fddbb7f581d96a459ba4765))
* fix duplicate entries ([9dc019f](https://github.com/opencadc/deployments/commit/9dc019f5067c59053b87724313b80e18fdc9ab12))
* fix duplicate entries ([eba5822](https://github.com/opencadc/deployments/commit/eba5822eaf3004dae69dfe0612bc9b8e8e1a619d))
* fix release namespace storage ui chart ([76f7181](https://github.com/opencadc/deployments/commit/76f71813003cb95a89de3332f59a1387068dbee0))
* update version for vulnerability fix ([9b2c7e4](https://github.com/opencadc/deployments/commit/9b2c7e44de3390a1c5c5215cce4202b4b588ee8a))

## 2025.05.20 (0.6.0)
- Add configuration for Manage Groups link
- Deal with vulnerability in JSON library

## 2025.04.15 (0.5.1)
- Add `tolerations` feature for `storage` UI.  Redis values can be added in the `redis` sub-chart stanza.
  - See https://github.com/opencadc/deployments/issues/29

## January 13, 2025 (0.5.0)
- Fixed issue with duplicate entries in paginated enabled backends
- Linter fixes

## December 11, 2024 (0.4.0)
- Added support for `securityContext`
- Added support to rename application to change endpoint (`applicationName`)

## December 3, 2024 (0.3.0)
* Add batch download options
* Small optimizations and fixes

## June 24, 2024 (0.2.3)
* Fix to use tokens for APIs on a different host.

## April 5, 2024 (0.1.7)
* Add feature to set Kubernetes secret to declare OpenID Connect client secret to avoid setting it explicitly

## January 12, 2024 (0.1.3)
* OpenID Connect compliant with Authorization Code flow
* Feature flag to disable some features (Batch download/upload, ZIP Download, Create External Links, Supports Paginated downloads)
