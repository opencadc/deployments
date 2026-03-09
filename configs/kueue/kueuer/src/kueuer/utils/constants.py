"""Application-wide constants and configuration values.

This module centralizes magic numbers and hardcoded values used throughout
the codebase, with documentation explaining why each value was chosen.
"""

# =============================================================================
# Shell Command Timeouts
# =============================================================================

# Default timeout for kubectl and other shell commands (seconds)
# Rationale: 120 seconds provides enough time for most kubectl operations
# including those that may need to wait for API server responses or
# perform multiple retries. Increased from 60s to handle slower clusters.
DEFAULT_COMMAND_TIMEOUT_SECONDS = 120

# =============================================================================
# Observation Collection
# =============================================================================

# Default interval between observation samples (seconds)
# Rationale: 5 seconds provides good granularity for observing control-plane
# metrics without overwhelming the API server with requests. This balances
# data resolution with system load.
DEFAULT_OBSERVATION_INTERVAL_SECONDS = 5.0

# Minimum observation interval to prevent API server overload (seconds)
# Rationale: 0.01 seconds (10ms) is the absolute minimum to prevent
# accidental infinite loops or excessive API calls. In practice, intervals
# should be much higher (5+ seconds).
MIN_OBSERVATION_INTERVAL_SECONDS = 0.01

# Default subdirectory name for observation artifacts
# Rationale: Consistent naming makes it easy to find observation data
# across different run directories.
DEFAULT_OBSERVATION_SUBDIR = "observe"

# =============================================================================
# Decimal Precision
# =============================================================================

# Precision for CPU resource calculations using Decimal
# Rationale: 50 decimal places ensures no loss of precision when converting
# between Kubernetes quantity formats (e.g., "100m" to "0.1") and performing
# arithmetic operations on CPU allocations.
DECIMAL_PRECISION = 50

# =============================================================================
# Kubernetes Job Tracking
# =============================================================================

# Default namespace for Kueue system components
# Rationale: This is the standard namespace where Kueue controllers run.
# Used for monitoring controller health and restart counts.
KUEUE_SYSTEM_NAMESPACE = "kueue-system"

# Default namespace for benchmark workloads
# Rationale: Matches the SKAHA project's workload namespace convention.
# This is where benchmark jobs are typically deployed.
DEFAULT_WORKLOAD_NAMESPACE = "skaha-workload"

# =============================================================================
# Artifact Directories
# =============================================================================

# Default root directory for all benchmark artifacts
# Rationale: Centralized location for all outputs makes it easy to find
# results and clean up after benchmarks. Relative path keeps artifacts
# in the project directory.
DEFAULT_ARTIFACTS_DIR = "artifacts"

# Default subdirectory for performance benchmark results
# Rationale: Separates performance data from eviction data for clarity.
PERFORMANCE_SUBDIR = "performance"

# Default subdirectory for eviction benchmark results
# Rationale: Separates eviction data from performance data for clarity.
EVICTIONS_SUBDIR = "evictions"

# Default subdirectory for plot outputs
# Rationale: Keeps generated plots separate from raw data files.
PLOTS_SUBDIR = "plots"

# Default subdirectory for comparison reports
# Rationale: Centralized location for analysis and summary reports.
COMPARISON_SUBDIR = "comparison"

# =============================================================================
# File Names
# =============================================================================

# Standard filename for performance benchmark results
PERFORMANCE_CSV_FILENAME = "performance.csv"

# Standard filename for eviction benchmark results
EVICTIONS_YAML_FILENAME = "evictions.yaml"

# Standard filename for observation timeseries data
OBSERVATION_TIMESERIES_FILENAME = "timeseries.csv"

# Standard filename for observation raw samples
OBSERVATION_SAMPLES_FILENAME = "samples.jsonl"

# Standard filename for observation analysis report
OBSERVATION_REPORT_FILENAME = "report.json"

# Standard filename for lifecycle manifest
LIFECYCLE_MANIFEST_FILENAME = "manifest.json"

# =============================================================================
# Benchmark Defaults
# =============================================================================

# Default job template file path
# Rationale: Relative path to the standard job template included in the package.
DEFAULT_JOBSPEC_FILEPATH = "src/kueuer/benchmarks/job.yaml"

# Default local queue name for benchmarks
# Rationale: Matches the SKAHA project's queue naming convention.
DEFAULT_LOCAL_QUEUE = "skaha-local-queue"

# Default cluster queue name for benchmarks
# Rationale: Matches the SKAHA project's cluster queue naming convention.
DEFAULT_CLUSTER_QUEUE = "skaha-cluster-queue"

# Default priority class for benchmark jobs
# Rationale: "high" priority ensures benchmark jobs are scheduled promptly
# for more accurate timing measurements.
DEFAULT_PRIORITY_CLASS = "high"

# =============================================================================
# Job Apply Configuration
# =============================================================================

# Default number of job manifests to apply in a single kubectl batch
# Rationale: 10 jobs per batch balances throughput with API server load.
# Too large causes timeouts, too small is inefficient.
DEFAULT_APPLY_CHUNK_SIZE = 10

# Default number of retries for failed kubectl apply operations
# Rationale: 3 retries handles transient API server issues without
# excessive delays. Most failures are permanent after 3 attempts.
DEFAULT_APPLY_RETRIES = 3

# Default backoff base for exponential retry delays (seconds)
# Rationale: 1 second base with exponential backoff (1s, 2s, 4s) provides
# reasonable retry timing without overwhelming the API server.
DEFAULT_APPLY_BACKOFF_SECONDS = 1.0
