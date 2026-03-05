# Phase 1 Delta Report

## Integrity Summary
- Baseline rows: 78
- Post rows: 12
- Baseline duplicate rows: 66
- Post duplicate rows: 0
- Duplicate row reduction: 66

## Performance Means
- direct baseline mean total execution (s): 12.536625351224627
- direct post mean total execution (s): 13.023261109987894
- direct baseline mean avg job turnaround (s): 8.40327380952381
- direct post mean avg job turnaround (s): 7.346354166666667
- kueue baseline mean total execution (s): 10.28210304180781
- kueue post mean total execution (s): 14.838474353154501
- kueue baseline mean avg job turnaround (s): 6.82421875
- kueue post mean avg job turnaround (s): 7.776041666666667

## Eviction Tracking
- Baseline tracked workloads: 1
- Post tracked workloads: 18
- Post tuned tracked workloads: 24
- Baseline total requeues: 0
- Post total requeues: 0
- Post tuned total requeues: 0
- Baseline preemptor edges: 0
- Post preemptor edges: 0
- Post tuned preemptor edges: 0

## Notes
- Baseline eviction run contained API/webhook failures and tracked only a minimal workload set.
- Post-change run still showed webhook instability under heavy burst job creation, but tracking captured targeted workload progression.
- Tuned eviction run (lower RAM/storage) completed with full tracked workload set and stable cleanup behavior.
