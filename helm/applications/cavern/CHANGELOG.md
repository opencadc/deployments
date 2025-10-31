# CHANGELOG for Cavern User Storage (Chart 0.7.1)

## [0.8.0](https://github.com/shinybrar/deployments/compare/cavern-0.7.1...cavern-0.8.0) (2025-10-29)


### Features

* add readiness and liveness probes ([f777987](https://github.com/shinybrar/deployments/commit/f7779874164faec536368b8871a5eb2438cd2fef))
* add support for oidc user allocation through cavern api ([0544710](https://github.com/shinybrar/deployments/commit/0544710a6b0978da21448cbe401832bc14beff9a))
* add support for oidc user allocation through cavern api ([8bc17e3](https://github.com/shinybrar/deployments/commit/8bc17e37560fa9057a60561a1567eb0a48271c1c))
* add tls yaml support for configuration of user session ingress ([d9cfe73](https://github.com/shinybrar/deployments/commit/d9cfe7364652f241254bc3c490e7c59b58de16ff))
* add tls yaml support for configuration of user session ingressroutes ([fdb924e](https://github.com/shinybrar/deployments/commit/fdb924e31a8e1c808d92017bc670eae7984b5dc3))
* add tolerations to apis and uis to allow fine grained node deployment ([a2ba229](https://github.com/shinybrar/deployments/commit/a2ba2291ffc4cbb41cf47b0d6f1376c8ec64d3d7))
* allow setting images for those defaulting to docker io ([da0d2e7](https://github.com/shinybrar/deployments/commit/da0d2e7fbcf90639adc83a47b0517de827929399))
* allow setting images for those defaulting to docker io ([97574c2](https://github.com/shinybrar/deployments/commit/97574c274c1bf459951d21edbcf539a0abfe0398))
* **helm-docs:** migrated existing readme to docs, and auto-generated new chart readme, based on values.yml files ([fc2311f](https://github.com/shinybrar/deployments/commit/fc2311f11767056b3cc612f45af6e1e87e470ea3))
* support admin api keys for seamless trusted admin access mainly for allocations ([e40e074](https://github.com/shinybrar/deployments/commit/e40e0741488c9b251b44216592acb2b329375e74))
* support admin api keys for seamless trusted admin access mainly… ([114f8eb](https://github.com/shinybrar/deployments/commit/114f8eb42ecf9895325aaa942e3aff34fef163b4))


### Bug Fixes

* default values ([0603626](https://github.com/shinybrar/deployments/commit/0603626dd52705bf7308783e167d1d10382c4b8e))
* fix cavern chart version ([efc54aa](https://github.com/shinybrar/deployments/commit/efc54aaabf5b1ed1f73181afe721f7c97bddf620))
* **helm:** added chart lock files ([e81b72d](https://github.com/shinybrar/deployments/commit/e81b72d06dacf2a2c797afc5368db81f57c95bc1))
* **helm:** maintainer updates ([6af7785](https://github.com/shinybrar/deployments/commit/6af7785e0b840d4b58224f114caa20ef255cd473))
* **helm:** updated maintainers ([67803b1](https://github.com/shinybrar/deployments/commit/67803b18ec5e2762f0942451894e4c9b8c7ee2f9))
* **maintainers:** now need atleast 15 commits in the last 12 months to be considered a maintainer ([02954e4](https://github.com/shinybrar/deployments/commit/02954e4e190774cf4756e9b3f90594eac2a80499))
* make probes configurable ([a8dc074](https://github.com/shinybrar/deployments/commit/a8dc07461506c5fcd5ff0a1c9fc07e4419052ccd))
* make probes configurable ([54737d4](https://github.com/shinybrar/deployments/commit/54737d4eb884c496a966daa058992833b97b8cfe))
* **pre-commit:** added auto-generated helm-maintainers section to all helm charts ([882dfb9](https://github.com/shinybrar/deployments/commit/882dfb9f2cf2f0d1b3615d7768b92a2f39c122b8))
* **pre-commit:** end-of-file-fixer ([1d658c7](https://github.com/shinybrar/deployments/commit/1d658c75c74faedd7293d5151be51df295a1ddd9))
* **pre-commit:** removed helm-docs version footer, since its disabled by default in go install and was causing ci issues ([6d84426](https://github.com/shinybrar/deployments/commit/6d844263ef0af30047f09e47d6c0c63ae7d1c1c9))
* **pre-commit:** trailing-whitespaces ([178468c](https://github.com/shinybrar/deployments/commit/178468c8082ca69a395ebc5e185a2186afbb3335))
* **release:** helm-docs now add the release-please slug, renovate now updates AppVersion, deprecated requirement for maintainers in helm charts, updated release please config, updated release-matrix logic to properly create downstream payloads for releasing charts ([2c2b931](https://github.com/shinybrar/deployments/commit/2c2b9313c469475bd2b1f6bcfdb3b041a0f0f715))
* removed typo ([55f2570](https://github.com/shinybrar/deployments/commit/55f25706d0e3cc63aca0de5b3697bbdaa35c1352))
* review rework ([202356b](https://github.com/shinybrar/deployments/commit/202356b1c431837d8919e17fc0487c59253b2aac))
* rework ordering in values file ([e4289e9](https://github.com/shinybrar/deployments/commit/e4289e9e588bbcc20a1b0d3ac1629cea0a3a322d))
* update cavern chart to fix tokens ([152ce7c](https://github.com/shinybrar/deployments/commit/152ce7c2bcfd0e7e9c41bf33364384498e7ab304))
* update cavern chart to fix tokens ([f386d67](https://github.com/shinybrar/deployments/commit/f386d6738d78affc49ff398157876eb910dd7600))
* update cavern to 0_8_3 to fix npe ([00530d6](https://github.com/shinybrar/deployments/commit/00530d66364121efb6765ffecc6b2408170cef98))
* update cavern to 0_8_3 to fix npe ([9eaa434](https://github.com/shinybrar/deployments/commit/9eaa4344a6f17cff65af9baf666a5fdbe97fbe65))
* use staged images to avoid docker io repository rate limits ([48325f8](https://github.com/shinybrar/deployments/commit/48325f87198281b97372b0000c8eb277530460a6))
* use staged images to avoid docker io repository rate limits ([8a12285](https://github.com/shinybrar/deployments/commit/8a122853ed1917cc3679ce9655ea8ffbe8dba320))

## 2025.09.22 (0.7.1)
- Make liveness and readiness probes configurable.

## 2025.09.09 (0.7.0)
- Feature: Support `admin-api-key` (`.deployment.cavern.adminAPIKeys`) for trusted admin access.

## 2025.08.21 (0.6.7)
- Fix: Wee regression with the JWSK feature.

## 2025.07.29 (0.6.6)
- Fix: `NullPointerException` in `cavern` service.
- Feature: Add JWSK (JWT Set Key) support for OIDC authentication.

## 2025.06.17 (0.6.5)
- Small feature to allow user allocation on behalf of another user's JWT.  This is support for the OIDC scenario.

## 2025.05.07 (0.6.4)
- Update to `cavern` 0.8.1 image.
- Added `deployment.cavern.uws.db.image` to specify PostgreSQL image.

## 2025.04.15 (0.6.1)
- Add `tolerations` feature for `cavern` API and supprting PostgreSQL deployment.
  - See https://github.com/opencadc/deployments/issues/29

## 2025.01.09 (0.6.0)
- Small fix to remove unnecessary init container for Cavern
- Small fix to remove public access to /home folder (`cavern` 0.8.0)

## 2024.10.08
- Update to omit PostgreSQL in favour of an existing database.

## 2024.10.03 (0.4.7)
- Small bug fix to properly ask the OIDC Discovery document for the userinfo endpoint.

## 2024.09.18 (0.4.6)
- Bug fix for setting quotas

## 2024.09.13 (0.4.5)
- Bug fix for database initialization

## 2024.05.27 (0.4.0)
- Enforcing some values to be set by the deployer.
- Fix for Quota reporting
- Fix for folder size reporting
- Added `extraHosts` mapping for manual DNS entries
- Added `extraConfigData` to add to the Cavern `ConfigMap`.

## 2024.03.12 (0.3.0)
- Bug fixes in allocation
- Bug fixes in read permission with sub-paths

## 2023.11.29 (0.2.0)
- Fix to support creating links in the User Interface properly
- Support for pre-authorized URL key generation
- Added `applicationName` configuration to rename the underlying WAR file to serve from another endpoint
- Code cleanup
