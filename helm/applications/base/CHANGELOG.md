# Changelog

## [0.5.0](https://github.com/opencadc/deployments/compare/base-0.4.1...base-0.5.0) (2026-06-15)


### Features

* remove base and update skaha ([bad25eb](https://github.com/opencadc/deployments/commit/bad25eb057d218353e4e72b4938cb1ecb4411182))


### Bug Fixes

* **helm:** added chart lock files ([e81b72d](https://github.com/opencadc/deployments/commit/e81b72d06dacf2a2c797afc5368db81f57c95bc1))
* **maintainers:** now need atleast 15 commits in the last 12 months to be considered a maintainer ([02954e4](https://github.com/opencadc/deployments/commit/02954e4e190774cf4756e9b3f90594eac2a80499))
* **merge:** conflict ([8c14f17](https://github.com/opencadc/deployments/commit/8c14f1738feba41cd6ae78812b77661e543a2617))
* **pre-commit:** removed helm-docs version footer, since its disabled by default in go install and was causing ci issues ([6d84426](https://github.com/opencadc/deployments/commit/6d844263ef0af30047f09e47d6c0c63ae7d1c1c9))
* **release:** helm-docs now add the release-please slug, renovate now updates AppVersion, deprecated requirement for maintainers in helm charts, updated release please config, updated release-matrix logic to properly create downstream payloads for releasing charts ([2c2b931](https://github.com/opencadc/deployments/commit/2c2b9313c469475bd2b1f6bcfdb3b041a0f0f715))
