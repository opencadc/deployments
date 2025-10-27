# base Helm Chart for the Science Platform (0.4.1)

## [0.5.0](https://github.com/opencadc/deployments/compare/base-0.4.1...base-0.5.0) (2025-10-27)


### Features

* add ability to set hostname to deploy user sessions on separate… ([8ff451a](https://github.com/opencadc/deployments/commit/8ff451ae2ae44c1d66c6938cfec373ed19b0692a))
* add hostname for sessions and base chart ([4e58f21](https://github.com/opencadc/deployments/commit/4e58f21a26965cd6847da8c06caa258049715f72))
* **helm-docs:** migrated existing readme to docs, and auto-generated new chart readme, based on values.yml files ([fc2311f](https://github.com/opencadc/deployments/commit/fc2311f11767056b3cc612f45af6e1e87e470ea3))


### Bug Fixes

* do not make assumptions about different namespaces ([95b9053](https://github.com/opencadc/deployments/commit/95b90537eb31b5b69e3fc332f29d19735b4b5e33))
* do not make assumptions about different namespaces ([31db35d](https://github.com/opencadc/deployments/commit/31db35d359365d024562264c707ef60934d2971d))
* **maintainers:** now need atleast 15 commits in the last 12 months to be considered a maintainer ([02954e4](https://github.com/opencadc/deployments/commit/02954e4e190774cf4756e9b3f90594eac2a80499))
* **pre-commit:** added auto-generated helm-maintainers section to all helm charts ([882dfb9](https://github.com/opencadc/deployments/commit/882dfb9f2cf2f0d1b3615d7768b92a2f39c122b8))
* **pre-commit:** end-of-file-fixer ([1d658c7](https://github.com/opencadc/deployments/commit/1d658c75c74faedd7293d5151be51df295a1ddd9))
* **pre-commit:** trailing-whitespaces ([178468c](https://github.com/opencadc/deployments/commit/178468c8082ca69a395ebc5e185a2186afbb3335))

## 2025.06.05 (0.4.1)
- Fix Namespace creation to allow for same Namespace between system and workloads.

## 2024.12.13 (0.4.0)
- Update Traefik to use the 26.1.0 Helm Chart (Traefik Version 2.11.0)
