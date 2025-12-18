#!/bin/bash
set -e

# Find all directories that contain a Chart.yaml file
for chart_file in `find ./helm/applications -name "Chart.yaml" -print`; do
  chart_dir=$(dirname "$chart_file")
  echo "Updating dependencies for chart in: $chart_dir"
  # Run helm dependency update in the chart directory
  helm dependency update "$chart_dir"
done
