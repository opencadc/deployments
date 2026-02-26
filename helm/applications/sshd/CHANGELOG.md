# Changelog

## [1.1.0](https://github.com/opencadc/deployments/compare/sshd-1.0.1...sshd-1.1.0) (2026-02-26)


### Features

* **helm-docs:** migrated existing readme to docs, and auto-generated new chart readme, based on values.yml files ([fc2311f](https://github.com/opencadc/deployments/commit/fc2311f11767056b3cc612f45af6e1e87e470ea3))
* remove carta legacy and add scripting support ([b7128f5](https://github.com/opencadc/deployments/commit/b7128f5ee08b7620dbe2c666c44d7255662da692))


### Bug Fixes

* fix pre commit ([fc24792](https://github.com/opencadc/deployments/commit/fc247922894c09d6343fa75a34fb3fb352ccf257))
* **helm:** added chart lock files ([e81b72d](https://github.com/opencadc/deployments/commit/e81b72d06dacf2a2c797afc5368db81f57c95bc1))
* **helm:** sshd chart ([b7857ff](https://github.com/opencadc/deployments/commit/b7857ff3fadd3dd856b539de0e4fa1cd3bab56c4))
* **maintainers:** now need atleast 15 commits in the last 12 months to be considered a maintainer ([02954e4](https://github.com/opencadc/deployments/commit/02954e4e190774cf4756e9b3f90594eac2a80499))
* **pre-commit:** added auto-generated helm-maintainers section to all helm charts ([882dfb9](https://github.com/opencadc/deployments/commit/882dfb9f2cf2f0d1b3615d7768b92a2f39c122b8))
* **pre-commit:** removed helm-docs version footer, since its disabled by default in go install and was causing ci issues ([6d84426](https://github.com/opencadc/deployments/commit/6d844263ef0af30047f09e47d6c0c63ae7d1c1c9))
* **pre-commit:** trailing-whitespaces ([178468c](https://github.com/opencadc/deployments/commit/178468c8082ca69a395ebc5e185a2186afbb3335))
* **release:** helm-docs now add the release-please slug, renovate now updates AppVersion, deprecated requirement for maintainers in helm charts, updated release please config, updated release-matrix logic to properly create downstream payloads for releasing charts ([2c2b931](https://github.com/opencadc/deployments/commit/2c2b9313c469475bd2b1f6bcfdb3b041a0f0f715))

## [1.1.0](https://github.com/shinybrar/deployments/compare/sshd-1.0.1...sshd-1.1.0) (2025-10-30)


### Features

* **helm-docs:** migrated existing readme to docs, and auto-generated new chart readme, based on values.yml files ([fc2311f](https://github.com/shinybrar/deployments/commit/fc2311f11767056b3cc612f45af6e1e87e470ea3))
* initial commit for sshd with common utility library ([16abaa2](https://github.com/shinybrar/deployments/commit/16abaa2ce713269414e492eed12b9504a70d4713))
* initial commit for sshd with common utility library ([7d25a80](https://github.com/shinybrar/deployments/commit/7d25a80c32e122ce0dfcdccaae2c11d36ae12436))


### Bug Fixes

* **helm:** added chart lock files ([e81b72d](https://github.com/shinybrar/deployments/commit/e81b72d06dacf2a2c797afc5368db81f57c95bc1))
* **helm:** sshd chart ([b7857ff](https://github.com/shinybrar/deployments/commit/b7857ff3fadd3dd856b539de0e4fa1cd3bab56c4))
* **maintainers:** now need atleast 15 commits in the last 12 months to be considered a maintainer ([02954e4](https://github.com/shinybrar/deployments/commit/02954e4e190774cf4756e9b3f90594eac2a80499))
* **pre-commit:** added auto-generated helm-maintainers section to all helm charts ([882dfb9](https://github.com/shinybrar/deployments/commit/882dfb9f2cf2f0d1b3615d7768b92a2f39c122b8))
* **pre-commit:** removed helm-docs version footer, since its disabled by default in go install and was causing ci issues ([6d84426](https://github.com/shinybrar/deployments/commit/6d844263ef0af30047f09e47d6c0c63ae7d1c1c9))
* **pre-commit:** trailing-whitespaces ([178468c](https://github.com/shinybrar/deployments/commit/178468c8082ca69a395ebc5e185a2186afbb3335))
* **release:** helm-docs now add the release-please slug, renovate now updates AppVersion, deprecated requirement for maintainers in helm charts, updated release please config, updated release-matrix logic to properly create downstream payloads for releasing charts ([2c2b931](https://github.com/shinybrar/deployments/commit/2c2b9313c469475bd2b1f6bcfdb3b041a0f0f715))
* remove debug for now ([bf2c03d](https://github.com/shinybrar/deployments/commit/bf2c03debbc7f6feedd94637e576a2a65d1088f6))
* remove tests fo rnow ([1e815cb](https://github.com/shinybrar/deployments/commit/1e815cbd5afd8e26a71e9ed99ee7f2d7737a66d3))
* use latest traefik api group ([a776214](https://github.com/shinybrar/deployments/commit/a776214ae68a91a3dab99d67608972558a21b247))
* use latest traefik api group ([84debe4](https://github.com/shinybrar/deployments/commit/84debe45777162ae258acb51ab05c60c8d8617e5))
