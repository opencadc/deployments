#!/bin/bash

echo "Running Renovate Entrypoint Script"

# Install uv
echo "Installing uv"
curl -LsSf https://astral.sh/uv/install.sh | sh
echo "uv Installed: $(which uv)"
# Install Helm
echo "Installing Helm"
install-tool helm 3.19.0
echo "Helm Installed: $(which helm)"
# Install Go
echo "Installing Go"
install-tool golang 1.25.3
echo "Go Installed: $(which go)"
# Install Helm Docs
echo "Installing Helm Docs"
go install github.com/norwoodj/helm-docs/cmd/helm-docs@latest
echo "Helm Docs Installed: $(which helm-docs)"
# Run renovate bot
renovate
echo "Renovate Run Complete"
