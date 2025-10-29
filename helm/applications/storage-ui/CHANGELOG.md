# Storage User Interface Helm Chart (0.6.0)

## [0.8.0](https://github.com/opencadc/deployments/compare/storageui-0.7.0...storageui-0.8.0) (2025-10-29)


### Features

* add tolerations to apis and uis to allow fine grained node deployment ([a2ba229](https://github.com/opencadc/deployments/commit/a2ba2291ffc4cbb41cf47b0d6f1376c8ec64d3d7))
* allow configuration of manage group links ([d2a4288](https://github.com/opencadc/deployments/commit/d2a4288318b66244484ab3195cace659ffc38f41))
* allow setting images for those defaulting to docker io ([da0d2e7](https://github.com/opencadc/deployments/commit/da0d2e7fbcf90639adc83a47b0517de827929399))
* allow setting images for those defaulting to docker io ([97574c2](https://github.com/opencadc/deployments/commit/97574c274c1bf459951d21edbcf539a0abfe0398))
* **helm-docs:** migrated existing readme to docs, and auto-generated new chart readme, based on values.yml files ([fc2311f](https://github.com/opencadc/deployments/commit/fc2311f11767056b3cc612f45af6e1e87e470ea3))


### Bug Fixes

* add redis updates for cve fix and skaha limit range object ([e8c02c0](https://github.com/opencadc/deployments/commit/e8c02c0e780d7eeebceed6c237e409d5fc84dba5))
* add storage ui chart with security fixes ([9d3af7c](https://github.com/opencadc/deployments/commit/9d3af7c8b1ff197adfade1615a7b0fc1868dbdff))
* add storage ui chart with security fixes ([016f3cc](https://github.com/opencadc/deployments/commit/016f3cced6d4925f5fddbb7f581d96a459ba4765))
* fix duplicate entries ([9dc019f](https://github.com/opencadc/deployments/commit/9dc019f5067c59053b87724313b80e18fdc9ab12))
* fix duplicate entries ([eba5822](https://github.com/opencadc/deployments/commit/eba5822eaf3004dae69dfe0612bc9b8e8e1a619d))
* fix release namespace storage ui chart ([76f7181](https://github.com/opencadc/deployments/commit/76f71813003cb95a89de3332f59a1387068dbee0))
* **helm:** storage-ui ([ef0dcc0](https://github.com/opencadc/deployments/commit/ef0dcc0907e24cbc06a61728a93c79ce63a62202))
* **helm:** updated maintainers ([e0aee2a](https://github.com/opencadc/deployments/commit/e0aee2a45b84437f0dda7ad86fb1b7a3853b7c6b))
* **maintainers:** now need atleast 15 commits in the last 12 months to be considered a maintainer ([02954e4](https://github.com/opencadc/deployments/commit/02954e4e190774cf4756e9b3f90594eac2a80499))
* new helm deployments to include new redis image ([23b300d](https://github.com/opencadc/deployments/commit/23b300d58a1de07ad5ff7c21155b0976fd338518))
* new helm deployments to include new redis image ([efd4424](https://github.com/opencadc/deployments/commit/efd442462b42bcc56b199c2813e5347fcf105e60))
* **pre-commit:** added auto-generated helm-maintainers section to all helm charts ([882dfb9](https://github.com/opencadc/deployments/commit/882dfb9f2cf2f0d1b3615d7768b92a2f39c122b8))
* **pre-commit:** end-of-file-fixer ([1d658c7](https://github.com/opencadc/deployments/commit/1d658c75c74faedd7293d5151be51df295a1ddd9))
* **pre-commit:** trailing-whitespaces ([178468c](https://github.com/opencadc/deployments/commit/178468c8082ca69a395ebc5e185a2186afbb3335))
* update version for vulnerability fix ([9b2c7e4](https://github.com/opencadc/deployments/commit/9b2c7e44de3390a1c5c5215cce4202b4b588ee8a))
* updated readmes with the schema for registryURL ([bf7ea95](https://github.com/opencadc/deployments/commit/bf7ea95b02d1a52af4471e5e53e309a624c969b4))
* updated readmes with the schema for registryURL ([5c717a5](https://github.com/opencadc/deployments/commit/5c717a5e2d0e29b30983bfe3f87ae63f9870a050))

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
