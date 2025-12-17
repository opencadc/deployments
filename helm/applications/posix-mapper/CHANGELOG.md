# CHANGELOG for POSIX Mapper (0.5.0)

## [0.6.0](https://github.com/opencadc/deployments/compare/posixmapper-0.5.0...posixmapper-0.6.0) (2025-12-17)


### Features

* add documentation for setting up postgresql first ([16afef3](https://github.com/opencadc/deployments/commit/16afef338db3f332b912f82964138649ba6f8266))
* add tolerations to apis and uis to allow fine grained node deployment ([a2ba229](https://github.com/opencadc/deployments/commit/a2ba2291ffc4cbb41cf47b0d6f1376c8ec64d3d7))
* allow setting images for those defaulting to docker io ([da0d2e7](https://github.com/opencadc/deployments/commit/da0d2e7fbcf90639adc83a47b0517de827929399))
* allow setting images for those defaulting to docker io ([97574c2](https://github.com/opencadc/deployments/commit/97574c274c1bf459951d21edbcf539a0abfe0398))
* first pass for skaha and science portal ([857a94e](https://github.com/opencadc/deployments/commit/857a94ebb433bbf93749c046880d1b9a7fff196c))
* **helm-docs:** migrated existing readme to docs, and auto-generated new chart readme, based on values.yml files ([fc2311f](https://github.com/opencadc/deployments/commit/fc2311f11767056b3cc612f45af6e1e87e470ea3))
* remove default postgresql database install and require provided database configuration changes ([8934276](https://github.com/opencadc/deployments/commit/89342764809e5e7e3fd1f838ed1568b1a7a35b25))
* remove default postgresql database install and require provided… ([a655f7d](https://github.com/opencadc/deployments/commit/a655f7d60a8b847301f37c852111d0423b962d97))
* use release namespace as namespace and add documentation ([ca29655](https://github.com/opencadc/deployments/commit/ca29655dd77855fa0204fff41bff55dea9bfac8f))


### Bug Fixes

* Enable multiple registry entries for the helm chart (--registry client) ([9c5ead6](https://github.com/opencadc/deployments/commit/9c5ead6aa8955bd7537dbbc186abedb0eb8db415))
* fix for default gid with new users ([62353ac](https://github.com/opencadc/deployments/commit/62353acc875e7606650579e3519f180192e467b7))
* fix for default gid with new users ([c8faa2d](https://github.com/opencadc/deployments/commit/c8faa2d32d2c98456ea1e4b2231f39f85aa2ee0f))
* **helm:** maintainer updates ([6af7785](https://github.com/opencadc/deployments/commit/6af7785e0b840d4b58224f114caa20ef255cd473))
* **helm:** updated maintainers ([67803b1](https://github.com/opencadc/deployments/commit/67803b18ec5e2762f0942451894e4c9b8c7ee2f9))
* **maintainers:** now need atleast 15 commits in the last 12 months to be considered a maintainer ([02954e4](https://github.com/opencadc/deployments/commit/02954e4e190774cf4756e9b3f90594eac2a80499))
* **merge:** conflict ([8c14f17](https://github.com/opencadc/deployments/commit/8c14f1738feba41cd6ae78812b77661e543a2617))
* move security context for readability and add notes ([bc39ae8](https://github.com/opencadc/deployments/commit/bc39ae85ebf4e653538ad9b37c3360335cdf4e77))
* **pre-commit:** added auto-generated helm-maintainers section to all helm charts ([882dfb9](https://github.com/opencadc/deployments/commit/882dfb9f2cf2f0d1b3615d7768b92a2f39c122b8))
* **pre-commit:** end-of-file-fixer ([1d658c7](https://github.com/opencadc/deployments/commit/1d658c75c74faedd7293d5151be51df295a1ddd9))
* **pre-commit:** fixes ([e750d75](https://github.com/opencadc/deployments/commit/e750d75083368e66196265cd3414e8608d21d6c4))
* **pre-commit:** linting ([783fbdb](https://github.com/opencadc/deployments/commit/783fbdb3cbc9a64f6ec0c0f28635c4600320b326))
* **pre-commit:** removed helm-docs version footer, since its disabled by default in go install and was causing ci issues ([6d84426](https://github.com/opencadc/deployments/commit/6d844263ef0af30047f09e47d6c0c63ae7d1c1c9))
* **pre-commit:** trailing-whitespaces ([178468c](https://github.com/opencadc/deployments/commit/178468c8082ca69a395ebc5e185a2186afbb3335))
* **release:** helm-docs now add the release-please slug, renovate now updates AppVersion, deprecated requirement for maintainers in helm charts, updated release please config, updated release-matrix logic to properly create downstream payloads for releasing charts ([2c2b931](https://github.com/opencadc/deployments/commit/2c2b9313c469475bd2b1f6bcfdb3b041a0f0f715))
* revert postgres version change ([4429b06](https://github.com/opencadc/deployments/commit/4429b063213c0defff812bf3d0c3d018e04154a0))
* review rework ([740aeca](https://github.com/opencadc/deployments/commit/740aeca0d5bc195b89708be97d2bcf9d70d71ecb))
* updated all the cadc-registry properties to enable a list of registries. ([bc6c474](https://github.com/opencadc/deployments/commit/bc6c474311ab548164b280a0ab86477e3e86c5ec))
* updated readmes with the schema for registryURL ([bf7ea95](https://github.com/opencadc/deployments/commit/bf7ea95b02d1a52af4471e5e53e309a624c969b4))
* updated readmes with the schema for registryURL ([5c717a5](https://github.com/opencadc/deployments/commit/5c717a5e2d0e29b30983bfe3f87ae63f9870a050))
* Updated to enable list of registries or a single value for registryURL ([f5eb435](https://github.com/opencadc/deployments/commit/f5eb435ad9d6b7d02638f9e9343c1c03c84d10f3))
* use staged images to avoid docker io repository rate limits ([48325f8](https://github.com/opencadc/deployments/commit/48325f87198281b97372b0000c8eb277530460a6))
* use staged images to avoid docker io repository rate limits ([8a12285](https://github.com/opencadc/deployments/commit/8a122853ed1917cc3679ce9655ea8ffbe8dba320))

## [0.6.0](https://github.com/shinybrar/deployments/compare/posixmapper-0.5.0...posixmapper-0.6.0) (2025-10-30)


### Features

* add documentation for setting up postgresql first ([16afef3](https://github.com/shinybrar/deployments/commit/16afef338db3f332b912f82964138649ba6f8266))
* add tolerations to apis and uis to allow fine grained node deployment ([a2ba229](https://github.com/shinybrar/deployments/commit/a2ba2291ffc4cbb41cf47b0d6f1376c8ec64d3d7))
* allow setting images for those defaulting to docker io ([da0d2e7](https://github.com/shinybrar/deployments/commit/da0d2e7fbcf90639adc83a47b0517de827929399))
* allow setting images for those defaulting to docker io ([97574c2](https://github.com/shinybrar/deployments/commit/97574c274c1bf459951d21edbcf539a0abfe0398))
* breaking change to remove storage hostpath spec ([12a843c](https://github.com/shinybrar/deployments/commit/12a843c99eab08baeb359d1531ff8452df458c0f))
* **helm-docs:** migrated existing readme to docs, and auto-generated new chart readme, based on values.yml files ([fc2311f](https://github.com/shinybrar/deployments/commit/fc2311f11767056b3cc612f45af6e1e87e470ea3))
* remove default postgresql database install and require provided database configuration changes ([8934276](https://github.com/shinybrar/deployments/commit/89342764809e5e7e3fd1f838ed1568b1a7a35b25))
* remove default postgresql database install and require provided… ([a655f7d](https://github.com/shinybrar/deployments/commit/a655f7d60a8b847301f37c852111d0423b962d97))
* use release namespace as namespace and add documentation ([ca29655](https://github.com/shinybrar/deployments/commit/ca29655dd77855fa0204fff41bff55dea9bfac8f))


### Bug Fixes

* add posix mapper chart with extra security context support ([618c1f7](https://github.com/shinybrar/deployments/commit/618c1f77aeb438f9fd2877c86c8cae06bd0d244f))
* add posix mapper chart with extra security context support ([86c13c7](https://github.com/shinybrar/deployments/commit/86c13c7d93c0a28e4ee821ed516a94f392304c65))
* append security constraints for posix mapper postgres ([6cc8ee6](https://github.com/shinybrar/deployments/commit/6cc8ee6940ee686b427dd98c4c55868a7ea7997f))
* append security constraints for posix mapper postgres ([ca1ef28](https://github.com/shinybrar/deployments/commit/ca1ef28d901c44e2196003745694bd7bc22ed665))
* fix for default gid with new users ([62353ac](https://github.com/shinybrar/deployments/commit/62353acc875e7606650579e3519f180192e467b7))
* fix for default gid with new users ([c8faa2d](https://github.com/shinybrar/deployments/commit/c8faa2d32d2c98456ea1e4b2231f39f85aa2ee0f))
* **helm:** maintainer updates ([6af7785](https://github.com/shinybrar/deployments/commit/6af7785e0b840d4b58224f114caa20ef255cd473))
* **helm:** updated maintainers ([67803b1](https://github.com/shinybrar/deployments/commit/67803b18ec5e2762f0942451894e4c9b8c7ee2f9))
* **maintainers:** now need atleast 15 commits in the last 12 months to be considered a maintainer ([02954e4](https://github.com/shinybrar/deployments/commit/02954e4e190774cf4756e9b3f90594eac2a80499))
* make postgres install optional ([d227cde](https://github.com/shinybrar/deployments/commit/d227cde30ae29175aac8c320ca3a7fa497503e77))
* make postgres install optional ([320865a](https://github.com/shinybrar/deployments/commit/320865ab8a93820733a32edc5c88b82b5ed81ffc))
* make postgres install optional ([c751093](https://github.com/shinybrar/deployments/commit/c75109331df4e762cf5d3fd2638e6d3b6e8e1bcf))
* memory leak in posix mapper fix ([74f3698](https://github.com/shinybrar/deployments/commit/74f3698fd2fcc46a4fa878caa880929977465781))
* move security context for readability and add notes ([bc39ae8](https://github.com/shinybrar/deployments/commit/bc39ae85ebf4e653538ad9b37c3360335cdf4e77))
* posix mapper memory leak fix with proper hibernate handling ([4235957](https://github.com/shinybrar/deployments/commit/4235957b6e540456ab286c8dc62200110c89bf90))
* **pre-commit:** added auto-generated helm-maintainers section to all helm charts ([882dfb9](https://github.com/shinybrar/deployments/commit/882dfb9f2cf2f0d1b3615d7768b92a2f39c122b8))
* **pre-commit:** end-of-file-fixer ([1d658c7](https://github.com/shinybrar/deployments/commit/1d658c75c74faedd7293d5151be51df295a1ddd9))
* **pre-commit:** removed helm-docs version footer, since its disabled by default in go install and was causing ci issues ([6d84426](https://github.com/shinybrar/deployments/commit/6d844263ef0af30047f09e47d6c0c63ae7d1c1c9))
* **pre-commit:** trailing-whitespaces ([178468c](https://github.com/shinybrar/deployments/commit/178468c8082ca69a395ebc5e185a2186afbb3335))
* **release:** helm-docs now add the release-please slug, renovate now updates AppVersion, deprecated requirement for maintainers in helm charts, updated release please config, updated release-matrix logic to properly create downstream payloads for releasing charts ([2c2b931](https://github.com/shinybrar/deployments/commit/2c2b9313c469475bd2b1f6bcfdb3b041a0f0f715))
* revert postgres version change ([4429b06](https://github.com/shinybrar/deployments/commit/4429b063213c0defff812bf3d0c3d018e04154a0))
* review rework ([740aeca](https://github.com/shinybrar/deployments/commit/740aeca0d5bc195b89708be97d2bcf9d70d71ecb))
* small syntax fix ([53f69d0](https://github.com/shinybrar/deployments/commit/53f69d01559109b43fd6d78ea8b09cb9769c2fe5))
* small syntax fix ([5a47eb0](https://github.com/shinybrar/deployments/commit/5a47eb075c0b06188ca35587c5d79be6a58f6b72))
* update chart version ([ea0eed7](https://github.com/shinybrar/deployments/commit/ea0eed7fe69129d272e27038dd6d19f1d02dfe90))
* update chart version ([758f37f](https://github.com/shinybrar/deployments/commit/758f37f08c1ad57bf35a9561ad128b6871345a2c))
* use staged images to avoid docker io repository rate limits ([48325f8](https://github.com/shinybrar/deployments/commit/48325f87198281b97372b0000c8eb277530460a6))
* use staged images to avoid docker io repository rate limits ([8a12285](https://github.com/shinybrar/deployments/commit/8a122853ed1917cc3679ce9655ea8ffbe8dba320))

## 2025.07.28 (0.5.0)
### 🚨 Breaking Changes
- 🛑 🔥 Removed default PostgreSQL database.  It is expected that deployers will run their own PostreSQL database with permanent storage.

## 2025.07.16 (0.4.4)
- Fix for default GID with new Users.  Default GID will match new User's UID.

## 2025.04.15 (0.4.1)
- Add `tolerations` feature for `posix-mapper` API and supprting PostgreSQL deployment.
  - See https://github.com/opencadc/deployments/issues/29

## 2025.02.11 (0.4.0)
- Rework fix of memory leak by properly closing the Hibernate SessionFactory
- Removed default `hostPath` in storage spec of postgresql database

## 2025.01.24 (0.3.0)
- Fix memory leak in POSIX Mapper application

## 2024.12.19 (0.2.1)
- Make postgresql configurable for external databases

## 2024.12.11 (0.2.0)
- Added support for `securityContext`
- Added support to rename application to change endpoint
- Small fixes and error reporting

## 2023.11.02 (0.1.8)
- Swagger documentation fix (Bug)
- Properly authenticate Bearer tokens (Improvement)
- Now supports setting the `gmsID` and `oidcURI` configurations (was hard-coded to SKAO)
- Code cleanup
