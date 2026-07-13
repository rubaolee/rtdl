# Goal5097 RT-DBSCAN Performance Boundary And Runner Contract

## Status

`completed_performance_regime_contract_defined`

## Purpose

After Goal5096 closed the bounded same-input RT-DBSCAN gate, this goal defines the performance regimes that later representative runs must report. The intent is to prevent a replay/warm-process number from being presented as a one-shot paper reproduction number.

## Runner Contract

The representative runner is:

```text
Paper-reproduction-apps/rt-dbscan-paper/scripts/run_authorofficial_partition_matrix.py
```

It accepts a fixture manifest, a backend, an optional patched AuthorOfficial binary, repeat count, an optional case filter, and an output summary path.

The runner records:

- RTDL wall-clock time for the selected backend.
- Author process wall time when an author binary is supplied.
- Author self-reported build/core/cluster/total phase timings when available.
- Component partition equality, core-flag equality, signature equality, and final `matched`.
- RTDL phase metadata from the generic OptiX + Numba grouped-stream route.

## Required Regimes

`cold_process_one_shot`:

- Each case is run in a fresh Python/SSH process.
- Includes RTDL process startup, CUDA/Numba/OptiX initialization, and first-use compilation/setup.
- This is the closest current proxy for a user invoking the script once.

`warm_long_lived_process`:

- Multiple cases/repeats are run in one Python process.
- First repeat can include compilation/setup; median over repeats can mostly measure steady-state.
- This is diagnostic for a service-like or notebook-like process, not a public paper performance claim.

`author_reported_phase_total`:

- Uses the patched author's own reported build/core/cluster/total fields.
- This excludes some process overhead and is the strongest author compute-phase denominator currently available.

`author_process_wall`:

- Measures process-level author invocation wall time around the binary.
- Useful for end-to-end runner context, but not identical to the author's internal compute phase.

## Non-Authorization

This contract does not authorize:

- full RT-DBSCAN paper reproduction,
- exact paper dataset performance claims,
- a public speedup claim,
- author-performance parity,
- comparing warm RTDL medians against cold author process wall as a headline.

## Evidence

The contract is implemented by `run_authorofficial_partition_matrix.py` and used by Goals5099-5100. It is reflected in all representative summary JSON files under:

```text
Paper-reproduction-apps/rt-dbscan-paper/results/representative_partition_matrix_*.json
```
