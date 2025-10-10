# CHANGELOG for POSIX Mapper (0.5.0)

## [0.6.0](https://github.com/opencadc/deployments/compare/posixmapper-0.5.0...posixmapper-0.6.0) (2025-10-10)


### Features

* add documentation for setting up postgresql first ([16afef3](https://github.com/opencadc/deployments/commit/16afef338db3f332b912f82964138649ba6f8266))
* add tolerations to apis and uis to allow fine grained node deployment ([a2ba229](https://github.com/opencadc/deployments/commit/a2ba2291ffc4cbb41cf47b0d6f1376c8ec64d3d7))
* allow setting images for those defaulting to docker io ([da0d2e7](https://github.com/opencadc/deployments/commit/da0d2e7fbcf90639adc83a47b0517de827929399))
* allow setting images for those defaulting to docker io ([97574c2](https://github.com/opencadc/deployments/commit/97574c274c1bf459951d21edbcf539a0abfe0398))
* breaking change to remove storage hostpath spec ([12a843c](https://github.com/opencadc/deployments/commit/12a843c99eab08baeb359d1531ff8452df458c0f))
* remove default postgresql database install and require provided database configuration changes ([8934276](https://github.com/opencadc/deployments/commit/89342764809e5e7e3fd1f838ed1568b1a7a35b25))
* remove default postgresql database install and require provided… ([a655f7d](https://github.com/opencadc/deployments/commit/a655f7d60a8b847301f37c852111d0423b962d97))
* use release namespace as namespace and add documentation ([ca29655](https://github.com/opencadc/deployments/commit/ca29655dd77855fa0204fff41bff55dea9bfac8f))


### Bug Fixes

* add posix mapper chart with extra security context support ([618c1f7](https://github.com/opencadc/deployments/commit/618c1f77aeb438f9fd2877c86c8cae06bd0d244f))
* add posix mapper chart with extra security context support ([86c13c7](https://github.com/opencadc/deployments/commit/86c13c7d93c0a28e4ee821ed516a94f392304c65))
* append security constraints for posix mapper postgres ([6cc8ee6](https://github.com/opencadc/deployments/commit/6cc8ee6940ee686b427dd98c4c55868a7ea7997f))
* append security constraints for posix mapper postgres ([ca1ef28](https://github.com/opencadc/deployments/commit/ca1ef28d901c44e2196003745694bd7bc22ed665))
* fix for default gid with new users ([62353ac](https://github.com/opencadc/deployments/commit/62353acc875e7606650579e3519f180192e467b7))
* fix for default gid with new users ([c8faa2d](https://github.com/opencadc/deployments/commit/c8faa2d32d2c98456ea1e4b2231f39f85aa2ee0f))
* make postgres install optional ([d227cde](https://github.com/opencadc/deployments/commit/d227cde30ae29175aac8c320ca3a7fa497503e77))
* make postgres install optional ([320865a](https://github.com/opencadc/deployments/commit/320865ab8a93820733a32edc5c88b82b5ed81ffc))
* make postgres install optional ([c751093](https://github.com/opencadc/deployments/commit/c75109331df4e762cf5d3fd2638e6d3b6e8e1bcf))
* memory leak in posix mapper fix ([74f3698](https://github.com/opencadc/deployments/commit/74f3698fd2fcc46a4fa878caa880929977465781))
* move security context for readability and add notes ([bc39ae8](https://github.com/opencadc/deployments/commit/bc39ae85ebf4e653538ad9b37c3360335cdf4e77))
* posix mapper memory leak fix with proper hibernate handling ([4235957](https://github.com/opencadc/deployments/commit/4235957b6e540456ab286c8dc62200110c89bf90))
* revert postgres version change ([4429b06](https://github.com/opencadc/deployments/commit/4429b063213c0defff812bf3d0c3d018e04154a0))
* review rework ([740aeca](https://github.com/opencadc/deployments/commit/740aeca0d5bc195b89708be97d2bcf9d70d71ecb))
* small syntax fix ([53f69d0](https://github.com/opencadc/deployments/commit/53f69d01559109b43fd6d78ea8b09cb9769c2fe5))
* small syntax fix ([5a47eb0](https://github.com/opencadc/deployments/commit/5a47eb075c0b06188ca35587c5d79be6a58f6b72))
* update chart version ([ea0eed7](https://github.com/opencadc/deployments/commit/ea0eed7fe69129d272e27038dd6d19f1d02dfe90))
* update chart version ([758f37f](https://github.com/opencadc/deployments/commit/758f37f08c1ad57bf35a9561ad128b6871345a2c))
* use staged images to avoid docker io repository rate limits ([48325f8](https://github.com/opencadc/deployments/commit/48325f87198281b97372b0000c8eb277530460a6))
* use staged images to avoid docker io repository rate limits ([8a12285](https://github.com/opencadc/deployments/commit/8a122853ed1917cc3679ce9655ea8ffbe8dba320))

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
