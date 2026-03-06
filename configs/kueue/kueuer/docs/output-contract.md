# Kueuer output contract

This page defines where `kueuer` writes artifacts and how to predict the path
for a given command. Use it when you are scripting runs or linking results from
tickets and documents.

## Default root

The default artifact root is `artifacts/`.

Artifact-producing commands create `artifacts/<run_id>/...` unless you override
their output directory. The default `run_id` is a UTC timestamp such as
`20260306-153000`.

## Standalone benchmark layout

Standalone benchmark commands write one data file per command under the run
directory:

1. `kr benchmark performance` writes `artifacts/<run_id>/performance.csv`.
2. `kr benchmark evictions` writes `artifacts/<run_id>/evictions.yaml`.

When you pass `--output-dir /path/to/custom-dir`, the command writes directly
into that directory instead:

1. `performance.csv`
2. `evictions.yaml`

## Plot layout

Plot commands never choose an output directory for you. You must pass
`--output-dir`.

Typical plot directories are:

1. `artifacts/<run_id>/plots/performance/`
2. `artifacts/<run_id>/plots/evictions/`
3. `artifacts/<run_id>/plots/observe/`

## Lifecycle layout

Lifecycle commands operate on one run directory:

1. `artifacts/<run_id>/manifest.json`
2. `artifacts/<run_id>/suite/performance.csv`
3. `artifacts/<run_id>/suite/evictions.yaml`
4. `artifacts/<run_id>/plots/performance/*.png`
5. `artifacts/<run_id>/plots/evictions/*.png`
6. `artifacts/<run_id>/plots/observe/*.png` when observation data exists
7. `artifacts/<run_id>/observe/raw_samples.jsonl` when `--observe` is enabled
8. `artifacts/<run_id>/observe/timeseries.csv` when `--observe` is enabled
9. `artifacts/<run_id>/observe/capabilities.json` when `--observe` is enabled
10. `artifacts/<run_id>/observe/summary.json` after `observe analyze`
11. `artifacts/<run_id>/observe/policy.json` after `observe analyze`
12. `artifacts/<run_id>/observe/report.md` after `observe report`

## Compatibility reads

The current implementation still reads a small set of legacy filenames so older
run directories remain usable during migration.

1. `manifest.json` falls back to `run_manifest.json`.
2. `suite/performance.csv` falls back to `suite/performance_results.csv`.
