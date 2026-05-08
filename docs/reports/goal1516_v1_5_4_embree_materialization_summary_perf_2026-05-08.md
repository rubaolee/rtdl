# Goal 1516: Embree Materialization Summary Performance

## Verdict

`goal1516_embree_materialization_summary_perf_recorded`

- Valid: `True`
- All parity passed: `True`
- Git commit: `ef7890b6f95240c07bdccd05b275cf111d371333`
- Host: `lx1`
- Embree version: `(4, 3, 0)`
- Repeats: `3`
- Warmups: `1`

## Cases

| App | Copies | Row median sec | Summary median sec | Summary/row speedup | Row count | Summary rows | Materialized rows avoided | Parity |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| event_hotspot_screening | 256 | 0.012275 | 0.009635 | 1.274x | 4602 | 1536 | 4602 | True |
| service_coverage_gaps | 256 | 0.006449 | 0.006260 | 1.030x | 1278 | 1024 | 1278 | True |
| event_hotspot_screening | 1024 | 0.049918 | 0.037308 | 1.338x | 18426 | 6144 | 18426 | True |
| service_coverage_gaps | 1024 | 0.024417 | 0.022034 | 1.108x | 5118 | 4096 | 5118 | True |
| event_hotspot_screening | 4096 | 0.205803 | 0.180677 | 1.139x | 73722 | 24576 | 73722 | True |
| service_coverage_gaps | 4096 | 0.090377 | 0.100071 | 0.903x | 20478 | 16384 | 20478 | True |

## Timing Scope

Python app function timing for Embree row mode versus Embree compact summary mode. This includes Python app orchestration and excludes CLI JSON printing.

## Claim Boundary

Goal1516 is CPU Embree materialization evidence for selected app modes only. It does not authorize public speedup wording, broad RTX wording, whole-app claims, true zero-copy wording, stable COLLECT_K_BOUNDED promotion, or release action.
