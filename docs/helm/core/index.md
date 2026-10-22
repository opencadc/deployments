# CADC/CANFAR Core Helm Charts

Core web and discovery services used across CADC and CANFAR. Charts such as **ac**, **cred**, and **reg** are unrelated products but may share a deployment domain; install each as its own release and apply [environment overlays](../../adr/0003-deployment-domains-via-environment-overlays.md) for hostnames, identity, and registry configuration.

## Explore the Core Services

<h4>Discover the configurable values for each Helm Chart</h4>
<div class="grid cards" markdown>
- [:material-store-settings: __Registry (`reg`)__ <small>to install an IVOA Registry service for service discovery</small>](reg.md)
</div>
