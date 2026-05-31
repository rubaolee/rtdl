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
  --compact-child-output \
  --output-dir /tmp/goal2855_current_packet
```

The runner writes `goal2855_summary.json` into the output directory. It streams
`[goal2855]` progress before and after each harness, while Goal2803 continues to
stream its own per-repeat Barnes-Hut progress.

With `--compact-child-output`, each child harness writes its full stdout to
`_stdout/<goal>_<app>.stdout`, while the terminal echoes only progress and error
lines. This keeps long pod runs readable without discarding diagnostic JSON.

For the first clean pod validation, the summary artifact is preserved at:

`docs/reports/goal2855_current_canonical_harness_runner_pod/goal2855_summary.json`

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

## Pod Validation

Clean pod validation was run on the RTX A5000 pod from pushed `main`:

| Field | Value |
| --- | --- |
| Source commit | `e8b95e9e4cbdc0893747be949d5c7b587e8dbe35` |
| Output directory | `/tmp/goal2855_packet_e8b95e9e_1780261491` |
| Summary artifact | `docs/reports/goal2855_current_canonical_harness_runner_pod/goal2855_summary.json` |
| GPU | `NVIDIA RTX A5000, 570.211.01` |
| Runner elapsed | `434.92` seconds |
| Artifact count | `7 / 7` |
| Summary status | `pass` |
| `source_dirty` | `[]` |
| Claim-boundary violations | `{}` |

Readback:

```text
pass True e8b95e9e4cbdc0893747be949d5c7b587e8dbe35 7 7 434.92
{}
{}
```

The full packet runner printed progress for all seven harnesses. The long
Barnes-Hut 8,192-body case printed per-repeat substeps, including the three
large Embree repeats at `99.562`, `102.794`, and `94.667` seconds and the three
OptiX repeats at `21.184`, `19.607`, and `20.488` seconds. That validates the
Goal2851 observability requirement inside the packet-level runner.

## Conclusion

Goal2855 is accepted as an operational hardening step. It reduces future pod
validation risk by making the current canonical v2.5 benchmark packet
reproducible, observable, and fail-closed. The boundary remains strict: this
runner supports readiness tracking, not release consensus or public performance
claims.
