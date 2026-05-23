# Goal2469 - RT-DBSCAN grouped-stream row vs column signature pod evidence

Date: 2026-05-20

Status: pod evidence collected for the benchmark-app no-row signature path.

## Environment

- Pod SSH: `root@213.173.110.198 -p 21453 -i ~/.ssh/id_ed25519_rtdl_codex`
- Source commit: `a9193856547bf692069955a3dbaf6c3e00c09b1b`
- GPU: NVIDIA RTX 2000 Ada Generation
- Driver: 550.127.05
- CUDA nvcc: `Build cuda_12.8.r12.8/compiler.35583870_0`
- OptiX headers: `NVIDIA/optix-dev` tag `v8.0.0`

The user-provided command used `~/.ssh/id_ed25519`, but that key is absent on
this Mac. The run used the existing RTDL key,
`~/.ssh/id_ed25519_rtdl_codex`.

The first build used OptiX 9.0 headers and failed at runtime with
`OptiX error: Unsupported ABI version` on driver 550.127.05. Rebuilding with
OptiX 8.0 headers fixed the runtime ABI mismatch.

## Inputs

Both runs used the same runner and prepared-handle repeat protocol:

```text
PYTHONPATH=src:. python scripts/goal2467_grouped_stream_baseline_pod_runner.py \
  --output-dir docs/reports/goal2469_grouped_stream_row_signature_pod \
  --point-count 32768 \
  --point-count 65536 \
  --repeat-count 5 \
  --signature-mode row

PYTHONPATH=src:. python scripts/goal2467_grouped_stream_baseline_pod_runner.py \
  --output-dir docs/reports/goal2469_grouped_stream_column_signature_pod \
  --point-count 32768 \
  --point-count 65536 \
  --repeat-count 5 \
  --signature-mode column
```

Raw artifacts:

- `docs/reports/goal2469_grouped_stream_row_signature_pod/summary.json`
- `docs/reports/goal2469_grouped_stream_row_signature_pod/clustered3d_32768_grouped_stream.json`
- `docs/reports/goal2469_grouped_stream_row_signature_pod/clustered3d_65536_grouped_stream.json`
- `docs/reports/goal2469_grouped_stream_column_signature_pod/summary.json`
- `docs/reports/goal2469_grouped_stream_column_signature_pod/clustered3d_32768_grouped_stream_column_signature.json`
- `docs/reports/goal2469_grouped_stream_column_signature_pod/clustered3d_65536_grouped_stream_column_signature.json`

## Results

Tail medians exclude the first repeat.

| Points | Row tail median | Column tail median | Row/column speedup | Time saved |
| ---: | ---: | ---: | ---: | ---: |
| 32,768 | 0.091646243 s | 0.068828613 s | 1.332x | 0.022817630 s |
| 65,536 | 0.236771312 s | 0.196566420 s | 1.205x | 0.040204892 s |

Native grouped-stream medians remained the same order. The 65,536-point case
is effectively identical; the 32,768-point case has about 4.2 ms native
run-to-run variance, smaller than the 18.6 ms host-gap reduction:

| Points | Row native median | Column native median |
| ---: | ---: | ---: |
| 32,768 | 0.062264977 s | 0.058034131 s |
| 65,536 | 0.174968306 s | 0.175098393 s |

Tail minus native grouped-stream median:

| Points | Row host/non-native gap | Column host/non-native gap | Gap reduction |
| ---: | ---: | ---: | ---: |
| 32,768 | 0.029381266 s | 0.010794481 s | 0.018586785 s |
| 65,536 | 0.061803006 s | 0.021468027 s | 0.040334979 s |

Host-side median breakdown:

| Points | Mode | Adapter run | Rows materialization | Densify labels | Row signature | Column signature |
| ---: | --- | ---: | ---: | ---: | ---: | ---: |
| 32,768 | row | 0.062634433 s | 0.013317747 s | 0.011013348 s | 0.004598679 s | n/a |
| 32,768 | column | 0.058234710 s | n/a | n/a | n/a | 0.010608394 s |
| 65,536 | row | 0.175274568 s | 0.028741293 s | 0.023725476 s | 0.009187512 s | n/a |
| 65,536 | column | 0.175254447 s | n/a | n/a | n/a | 0.021317009 s |

All repeat signatures matched within each run.

## Interpretation

The column-signature path improves the benchmark-app tail by about 20-33% on
this RTX 2000 Ada pod. The stable attribution is host-side: tail minus native
grouped-stream time drops by about 18.6 ms at 32,768 points and about 40.3 ms
at 65,536 points. This comes from removing Python row dictionaries and label
densification from the benchmark consumer path, partially offset by the new
column-signature computation.

The column signature still copies partner columns back to host and sorts by
point id to compute a deterministic benchmark signature. Further improvement
would require a partner-resident or zero-copy continuation/signature path, but
that is a separate design step and should not be claimed from this evidence.

## Claim Boundary

This evidence supports a narrow statement:

> For the RT-DBSCAN grouped-stream benchmark on this RTX 2000 Ada pod, the
> no-row column-signature consumer path reduces measured benchmark tail time
> versus the Python row-signature path while preserving the same native grouped
> RT traversal path.

It does not authorize a broad DBSCAN speedup claim, does not add a
DBSCAN-specific native ABI, and does not claim a faster native RT primitive.

## Verification

Focused pod gate passed:

```text
PYTHONPATH=src:. python -m unittest \
  tests.goal2469_rt_dbscan_column_signature_mode_test \
  tests.goal2468_rt_dbscan_overhead_breakdown_instrumentation_test \
  tests.goal2467_blocked_grouped_continuation_design_test \
  tests.goal2465_grouped_union_all_items_intersection_cull_test \
  tests.goal2463_grouped_union_all_items_path_test \
  tests.goal2461_grouped_stream_self_query_device_path_test \
  tests.goal2459_grouped_stream_threshold_capped_core_flags_test \
  tests.goal2457_generic_grouped_stream_continuation_implementation_test
```

Result: 35 tests passed on the pod.

After adding artifact-locking tests and the external review/consensus files,
the focused local and pod gates were rerun with 36 tests passing.

External review:

- `docs/reviews/goal2469_gemini_review_column_signature_pod_2026-05-20.md`
- Verdict: `ACCEPT`

Consensus:

- `docs/reviews/goal2469_codex_gemini_consensus_column_signature_pod_2026-05-20.md`
