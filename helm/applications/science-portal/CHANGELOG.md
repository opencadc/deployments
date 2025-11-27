# CHANGELOG for Science Portal UI (Chart 1.1.1)

## [1.1.0](https://github.com/opencadc/deployments/compare/scienceportal-1.0.2...scienceportal-1.1.0) (2025-11-27)


### Features

* add configuration with skaha default for default project in pul… ([e56e0e5](https://github.com/opencadc/deployments/commit/e56e0e55dd8ba6e54f4864d191369b1961134cf6))
* add configuration with skaha default for default project in pull down ([0a1d5a9](https://github.com/opencadc/deployments/commit/0a1d5a983a86bc59762dae2d61e5eda49ce53ad1))
* add limit range configuration and update docs ([4eaf993](https://github.com/opencadc/deployments/commit/4eaf993b33da03033d6fa83638791fea61d3b088))
* add tolerations to apis and uis to allow fine grained node deployment ([a2ba229](https://github.com/opencadc/deployments/commit/a2ba2291ffc4cbb41cf47b0d6f1376c8ec64d3d7))
* first pass for skaha and science portal ([857a94e](https://github.com/opencadc/deployments/commit/857a94ebb433bbf93749c046880d1b9a7fff196c))
* **helm-docs:** migrated existing readme to docs, and auto-generated new chart readme, based on values.yml files ([fc2311f](https://github.com/opencadc/deployments/commit/fc2311f11767056b3cc612f45af6e1e87e470ea3))
* new portal update for storage info ([386a4b7](https://github.com/opencadc/deployments/commit/386a4b738bf8e87bccdf5d52e458bd679520f87c))
* new portal update for storage info ([9a5f081](https://github.com/opencadc/deployments/commit/9a5f08103aaa6821f18e718536880c26cbb1d10a))
* support pod security context ([0b1cb74](https://github.com/opencadc/deployments/commit/0b1cb7490c93bc66f7df37dd7a82ff1ae2c9b4a3))
* use release namespace ([16cc82a](https://github.com/opencadc/deployments/commit/16cc82aff143a13e5913d27e53d9d33195b5caec))


### Bug Fixes

* add redis updates for cve fix and skaha limit range object ([e8c02c0](https://github.com/opencadc/deployments/commit/e8c02c0e780d7eeebceed6c237e409d5fc84dba5))
* add timeouts to kill warnings ([9658a11](https://github.com/opencadc/deployments/commit/9658a117bafefcb41f56e3f5ed2c97515e3339be))
* chart version updates ([106330d](https://github.com/opencadc/deployments/commit/106330d3da2b72395fefd5243b44968bb70c2987))
* chart versions ([ad90b90](https://github.com/opencadc/deployments/commit/ad90b9058136bcf79bbbc60e0d129414f724f6c7))
* chart versions ([d9c8052](https://github.com/opencadc/deployments/commit/d9c8052f00fc408442d506407c8c6c3d1fe96939))
* disable specific experimental features ([33586a6](https://github.com/opencadc/deployments/commit/33586a676b80696dcd89c75cd09b1e002e3b8c82))
* **docs:** fixed deployment docs ([4ce4c9d](https://github.com/opencadc/deployments/commit/4ce4c9d6dcba36b7e5fae47b073f2f75f26529ff))
* documentation link updates ([70411d8](https://github.com/opencadc/deployments/commit/70411d8afdc2382bbf81663da3f65465417f7873))
* documentation link updates ([7264452](https://github.com/opencadc/deployments/commit/72644529e631bdb97efd86926f99812b2eaa477c))
* Enable multiple registry entries for the helm chart (--registry client) ([9c5ead6](https://github.com/opencadc/deployments/commit/9c5ead6aa8955bd7537dbbc186abedb0eb8db415))
* fix chart version for science portal ([515fe51](https://github.com/opencadc/deployments/commit/515fe515203417b67aa1a6a242cf96b3cd891065))
* fix for default project when none specified ([62d5271](https://github.com/opencadc/deployments/commit/62d52714b2073b5586c8c655e02478b718cf8504))
* fix for default project when none specified ([a51806a](https://github.com/opencadc/deployments/commit/a51806ac60e5c5b47e61cce3520bd60ad83fbe4f))
* fix for gpu field input ([d840036](https://github.com/opencadc/deployments/commit/d840036c70cc8bf7f4e1f3a3e46e84deeacbd318))
* fix for helm versions ([543bd8e](https://github.com/opencadc/deployments/commit/543bd8ee065b4ed07c37108c2efdc0faf54babbb))
* **helm:** added chart lock files ([e81b72d](https://github.com/opencadc/deployments/commit/e81b72d06dacf2a2c797afc5368db81f57c95bc1))
* **helm:** maintainer updates ([6af7785](https://github.com/opencadc/deployments/commit/6af7785e0b840d4b58224f114caa20ef255cd473))
* **helm:** updated maintainers ([67803b1](https://github.com/opencadc/deployments/commit/67803b18ec5e2762f0942451894e4c9b8c7ee2f9))
* **maintainers:** now need atleast 15 commits in the last 12 months to be considered a maintainer ([02954e4](https://github.com/opencadc/deployments/commit/02954e4e190774cf4756e9b3f90594eac2a80499))
* merge ([4b4b3ae](https://github.com/opencadc/deployments/commit/4b4b3aed5202dba6eb0215ebcddcf4d26b59c135))
* **merge:** conflict ([8c14f17](https://github.com/opencadc/deployments/commit/8c14f1738feba41cd6ae78812b77661e543a2617))
* new helm deployments to include new redis image ([23b300d](https://github.com/opencadc/deployments/commit/23b300d58a1de07ad5ff7c21155b0976fd338518))
* new helm deployments to include new redis image ([efd4424](https://github.com/opencadc/deployments/commit/efd442462b42bcc56b199c2813e5347fcf105e60))
* **pre-commit:** added auto-generated helm-maintainers section to all helm charts ([882dfb9](https://github.com/opencadc/deployments/commit/882dfb9f2cf2f0d1b3615d7768b92a2f39c122b8))
* **pre-commit:** end-of-file-fixer ([1d658c7](https://github.com/opencadc/deployments/commit/1d658c75c74faedd7293d5151be51df295a1ddd9))
* **pre-commit:** fixes ([e750d75](https://github.com/opencadc/deployments/commit/e750d75083368e66196265cd3414e8608d21d6c4))
* **pre-commit:** linting ([783fbdb](https://github.com/opencadc/deployments/commit/783fbdb3cbc9a64f6ec0c0f28635c4600320b326))
* **pre-commit:** removed helm-docs version footer, since its disabled by default in go install and was causing ci issues ([6d84426](https://github.com/opencadc/deployments/commit/6d844263ef0af30047f09e47d6c0c63ae7d1c1c9))
* **pre-commit:** trailing-whitespaces ([178468c](https://github.com/opencadc/deployments/commit/178468c8082ca69a395ebc5e185a2186afbb3335))
* properly set the experimental feature if configured ([f9843a2](https://github.com/opencadc/deployments/commit/f9843a22c6f7d69e1f9c001643ccd9834aad8f5b))
* **release:** helm-docs now add the release-please slug, renovate now updates AppVersion, deprecated requirement for maintainers in helm charts, updated release please config, updated release-matrix logic to properly create downstream payloads for releasing charts ([2c2b931](https://github.com/opencadc/deployments/commit/2c2b9313c469475bd2b1f6bcfdb3b041a0f0f715))
* remove duplicate entry ([216b0ec](https://github.com/opencadc/deployments/commit/216b0ec7fa53f549c0b2a24ab86357afa1d623ae))
* specific experimental feature settings ([223f48b](https://github.com/opencadc/deployments/commit/223f48b771732c3f0147a493b92f294be3035d69))
* updated all the cadc-registry properties to enable a list of registries. ([bc6c474](https://github.com/opencadc/deployments/commit/bc6c474311ab548164b280a0ab86477e3e86c5ec))
* updated readmes with the schema for registryURL ([bf7ea95](https://github.com/opencadc/deployments/commit/bf7ea95b02d1a52af4471e5e53e309a624c969b4))
* updated readmes with the schema for registryURL ([5c717a5](https://github.com/opencadc/deployments/commit/5c717a5e2d0e29b30983bfe3f87ae63f9870a050))
* Updated to enable list of registries or a single value for registryURL ([f5eb435](https://github.com/opencadc/deployments/commit/f5eb435ad9d6b7d02638f9e9343c1c03c84d10f3))
* use proper indent ([86fe85a](https://github.com/opencadc/deployments/commit/86fe85a95eab9615085104d9ae16c4882d79e6af))
* version bump ([7a67925](https://github.com/opencadc/deployments/commit/7a67925b8b29b1d743b96b3a1f552ff8cabf8003))
* version bump ([c2dccf4](https://github.com/opencadc/deployments/commit/c2dccf4445b306007c9abebac0b79a912dac6342))
* version revert to remove accidentally released portal change and fix client secret setting ([73f9639](https://github.com/opencadc/deployments/commit/73f96398de23d1f3363f462b71f1d7399a8b33a6))
* version revert to remove accidentally released portal change and… ([ce78285](https://github.com/opencadc/deployments/commit/ce782855d1e1100a73fc1d116e5b867d7f78e737))
* version updates ([e04748f](https://github.com/opencadc/deployments/commit/e04748f68f6909e38ad4581fd7b5d004dd659dbe))
* version updates ([2896c2b](https://github.com/opencadc/deployments/commit/2896c2b44a5ad6cf0dd2d1d506dad81027108176))

## 2025.11.25 (1.1.1)
- Use `Release.Namespace` for installation rather than separate `namespace` value.

## 2025.11.17 (1.0.4)
- Fix: Remove running instances counts due to severe ineffieciency.
- Fix: Use `view=interactive` to only query inteactive sessions for the UI.

## 2025.10.31 (1.0.3)
- Feature: Add experimental slider feature gate
  - Add `experimentalFeatures.slider` section to `values.yaml` to enable/disable the slider feature.

## 2025.10.27 (1.0.2)
- Add configuration for default project to pre-select in the pull-down menu.

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
