# deployments
deployment templates for OpenCADC software components

## Chart Inventory

<!-- CHART-INVENTORY:START -->
This section is automatically generated. Do not edit manually.

| Chart | Version | App Version | Owners | Dependencies |
| --- | --- | --- | --- | --- |
| [base](helm/applications/base) | 0.4.1 | 0.1.4 | Shiny Brar, Dustin Jenkins | traefik 26.1.0 |
| [cavern](helm/applications/cavern) | 0.7.1 | 0.9.0 | Dustin Jenkins | utils ^0.1.0 |
| [posixmapper](helm/applications/posix-mapper) | 0.5.0 | 0.3.2 | Dustin Jenkins | — |
| [scienceportal](helm/applications/science-portal) | 1.0.0 | 1.0.1 | Dustin Jenkins | redis ^18.19.0, utils ^0.1.0 |
| [skaha](helm/applications/skaha) | 1.1.0 | 1.1.0 | Dustin Jenkins, Shiny Brar | redis ^18.19.0, utils ^0.1.0 |
| [sshd](helm/applications/sshd) | 1.0.1 | 1.0.0 | Dustin Jenkins, Shiny Brar | common ^1.0.0 |
| [storageui](helm/applications/storage-ui) | 0.7.0 | 1.4.1 | Dustin Jenkins, Shiny Brar | redis ^18.4.0, utils ^0.1.0 |
| [utils](helm/applications/utils) | 0.1.0 | 1.0.0 | Shiny Brar, Dustin Jenkins | — |
| [common](helm/common) | 1.0.0 | 1.0.0 | Shiny Brar, Dustin Jenkins | — |
<!-- CHART-INVENTORY:END -->
