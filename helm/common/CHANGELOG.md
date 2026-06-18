# Changelog

## [1.1.0](https://github.com/opencadc/deployments/compare/common-1.0.0...common-1.1.0) (2026-06-15)


### Features

* remove carta legacy and add scripting support ([b7128f5](https://github.com/opencadc/deployments/commit/b7128f5ee08b7620dbe2c666c44d7255662da692))


### Bug Fixes

* fix pre commit ([fc24792](https://github.com/opencadc/deployments/commit/fc247922894c09d6343fa75a34fb3fb352ccf257))
* **helm:** maintainer updates ([6af7785](https://github.com/opencadc/deployments/commit/6af7785e0b840d4b58224f114caa20ef255cd473))
* **pre-commit:** removed helm-docs version footer, since its disabled by default in go install and was causing ci issues ([6d84426](https://github.com/opencadc/deployments/commit/6d844263ef0af30047f09e47d6c0c63ae7d1c1c9))
* **release:** helm-docs now add the release-please slug, renovate now updates AppVersion, deprecated requirement for maintainers in helm charts, updated release please config, updated release-matrix logic to properly create downstream payloads for releasing charts ([2c2b931](https://github.com/opencadc/deployments/commit/2c2b9313c469475bd2b1f6bcfdb3b041a0f0f715))
