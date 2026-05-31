# Goal2855 v2.5 Current Canonical Harness Packet Runner

Date: 2026-05-31

Verdict: **accept-with-boundary**

Goal2855 adds a reusable seven-harness packet runner for the current v2.5
canonical pod checks:

`scripts/goal2855_v2_5_current_canonical_harness_packet_runner.py`

This goal does not change any benchmark implementation and does not change the
native RTDL engine. It operationalizes the manual Goal2847 packet run so future
pod validation can execute the same seven canonical harnesses with one command,
live progress, fail-closed artifact checks, and a machine-readable summary.

This is **not a v2.5 release authorization**. It is also not a public speedup,
paper reproduction, whole-app speedup, broad RT-core speedup, or true-zero-copy
claim.

## Runner Scope

The runner executes these existing harnesses in order:

| Goal | App / surface | Artifact | Boundary |
| --- | --- | --- | --- |
| Goal2797 | triangle counting | `goal2797_triangle_counting.json` | canonical app harness only |
| Goal2798 | LibRTS spatial index | `goal2798_librts.json` | Tier C no-regression harness |
| Goal2799 | spatial RayJoin | `goal2799_spatial_rayjoin.json` | prepared OptiX count/parity route, not full RayJoin reproduction |
| Goal2800 | RTNN | `goal2800_rtnn.json` | exact ranked-summary opponent, distribution-dependent |
| Goal2801 | Hausdorff/X-HD | `goal2801_hausdorff_xhd.json` | exact RTDL/OptiX path, no claim to beat optimized CuPy grid |
| Goal2802 | RT-DBSCAN | `goal2802_rt_dbscan.json` | grouped stream continuation evidence, no paper reproduction claim |
| Goal2803 | Barnes-Hut | `goal2803_barnes_hut.json` | membership/vector-sum harness; Triton vector path not promoted |

## Command Shape

Plan-only mode:

```bash
PYTHONPATH=src:. python3 scripts/goal2855_v2_5_current_canonical_harness_packet_runner.py \
  --list \
  --fail-fast \
  --output-dir /tmp/goal2855_current_packet
```

Full pod run:

```bash
PYTHONPATH=src:. timeout 2400s python3 -u \
  scripts/goal2855_v2_5_current_canonical_harness_packet_runner.py \
  --fail-fast \
  --output-dir /tmp/goal2855_current_packet
```

The runner writes `goal2855_summary.json` into the output directory. It streams
`[goal2855]` progress before and after each harness, while Goal2803 continues to
stream its own per-repeat Barnes-Hut progress.

## Fail-Closed Summary Checks

The packet summary is `pass` only when all of the following hold:

- all seven artifacts exist,
- each artifact has `status: pass`,
- every harness command exits with return code `0`,
- every artifact reports the same `source_commit`,
- every artifact reports `source_dirty: []`,
- no known claim-boundary key is accidentally set true, including public
  speedup, whole-app speedup, paper reproduction, true zero-copy, and native
  engine customization keys.

The summary itself also carries:

```json
{
  "v2_5_release_authorized": false,
  "public_speedup_claim_authorized": false,
  "whole_app_speedup_claim_authorized": false,
  "paper_reproduction_claim_authorized": false,
  "true_zero_copy_claim_authorized": false
}
```

## Validation

Local static validation:

```text
py -3 -m py_compile scripts/goal2855_v2_5_current_canonical_harness_packet_runner.py
py -3 -m unittest tests.goal2855_v2_5_current_canonical_harness_packet_runner_test
```

Expected focused result:

```text
Ran 4 tests
OK
```

Pod validation is the next step: run the full packet from a clean pushed commit,
confirm `goal2855_summary.json` is `pass`, and record the exact commit, GPU,
dirty state, and elapsed time.

## Conclusion

Goal2855 is accepted as an operational hardening step. It reduces future pod
validation risk by making the current canonical v2.5 benchmark packet
reproducible, observable, and fail-closed. The boundary remains strict: this
runner supports readiness tracking, not release consensus or public performance
claims.
