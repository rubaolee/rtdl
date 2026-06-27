# Goal2335 RayJoin Current-v2.0 Basis Completion

Date: 2026-05-18

Status: `current-v2-correctness-complete-performance-gap-characterized`

## Purpose

This goal finishes the current-v2.0-only RayJoin work that can be done without
adding a new native primitive or a v3.0-style user shader extension. The target
was not to beat RayJoin yet. The target was to close the immediate evidence
holes, use the pod while it was available, and decide which remaining work is
ordinary v2.0 app/runtime tuning versus a larger primitive/runtime extension.

## What Changed

### RayJoin PIP Result Export

Added a diagnostic RayJoin patch:

`docs/research/rayjoin_pip_result_export_debug_patch.diff`

It adds an environment variable:

```bash
RAYJOIN_EXPORT_PIP_RESULTS=/path/to/pip_results.json
```

The export writes RayJoin's final `closest_eids` vector from `query_exec
-query=pip` as positive point ids plus closest boundary edge ids. This patch is
diagnostic only; it is not part of RTDL and does not add an app-specific RTDL
engine path.

### RTDL Current-v2.0 Same-Contract PIP Probe

Added:

`scripts/goal2335_rayjoin_pip_vertical_probe_comparison.py`

RayJoin's `query=pip` path is not the same contract as RTDL's faster
`closed_shape_membership_2d_optix` path. RayJoin exposes a vertical ray support
contract: for each generated point, find the nearest upward boundary edge, or
`DONTKNOW` if no such edge exists. RTDL's closed-shape membership contract
answers a higher-level shape-membership predicate.

The current-v2.0 same-contract route therefore uses existing generic primitives:

1. Convert each RayJoin PIP query point into a vertical probe segment.
2. Run generic prepared segment-pair intersection against the base map edges.
3. Reduce emitted intersection rows by `left_id` using app/partner-side logic.
4. Compare the resulting positive point set against RayJoin's exported positive
   point set.

This preserves the RTDL engine boundary. The native engine still sees only
generic segment-pair intersection.

## Pod Evidence

| Item | Value |
| --- | --- |
| Pod | `root@69.30.85.175 -p 22114` |
| Key actually used | `C:\Users\Lestat\.ssh\id_ed25519_rtdl_codex_current_pod` |
| GPU | `NVIDIA RTX A5000, 570.211.01` |
| RTDL clean checkout | `/root/rtdl_goal2333_clean` |
| RTDL commit for clean validation | `07bee69ce2c31cfe225dcd96bca005b6e376e3a1` |
| RayJoin checkout | `/root/RayJoin_goal2331` |
| RayJoin upstream | `02bf622` plus query-stream, LSI-result, and PIP-result diagnostic patches |
| Dataset | `br_county_clean_25_odyssey_final.txt` |

Artifacts:

`docs/reports/goal2335_rayjoin_current_v2_basis_pod/`

## RayJoin PIP Same-Contract Results

| Scale | RayJoin positive points | RTDL positive points | Missing | Extra | Same positive point set |
| --- | ---: | ---: | ---: | ---: | --- |
| 4,096 | 3,374 | 3,374 | 0 | 0 | yes |
| 65,536 | 53,372 | 53,372 | 0 | 0 | yes |

This closes the PIP semantic evidence hole: RTDL can express RayJoin's PIP
support contract on the current v2.0 basis.

## Timing Snapshot

### LSI

Goal2333 already fixed LSI same-contract identity:

| Workload | RayJoin query time | RTDL v2.0 prepared OptiX time | Result |
| --- | ---: | ---: | --- |
| LSI, 65,536 queries | `0.460211 ms` | `4.929 ms` scalar / `4.948 ms` rows | same identity set, about `10.7x` slower |

### PIP, Same RayJoin Support Contract

| Scale | RayJoin query time | RTDL vertical-probe query | RTDL reduction | Raw RTDL rows | Result |
| --- | ---: | ---: | ---: | ---: | --- |
| 4,096 | `0.236209 ms` | `25.086 ms` | `1.308 ms` | 145,295 | same positive point set, much slower |
| 65,536 | `1.490470 ms` | `711.948 ms` | `22.649 ms` | 2,320,729 | same positive point set, much slower |

The faster RTDL closed-shape route is not the same contract:

| Scale | RTDL closed-shape membership count | RayJoin support-contract positives | Interpretation |
| --- | ---: | ---: | --- |
| 65,536 | 5,783 | 53,372 | different contracts, not a valid same-contract comparison |

## What We Finished On Current v2.0

| Work item | Status | Evidence |
| --- | --- | --- |
| RayJoin PIP result export | done | `rayjoin_pip_results_4096.json`, `rayjoin_pip_results_65536.json` |
| PIP same-contract comparison | done | missing/extra zero at 4,096 and 65,536 |
| LSI same-contract comparison | done by Goal2333 | missing/extra zero at 4,096 and 65,536 |
| Warm query timing with prepared handles | done | Goal2332/2333 plus Goal2335 artifacts |
| Phase-separated timing | done | pack/build/query/reduction separated in Goal2335 artifacts |
| App/runtime reuse on current primitives | done as far as current v2.0 allows | prepared handles reused within repeats; no rows requested when scalar count is valid |

## What Current v2.0 Cannot Solve Cleanly

The main remaining RayJoin performance gap is not a missing Python trick. It is
that the current same-contract PIP route must materialize a generic
vertical-probe/edge intersection row stream, then reduce it outside the native
query. At 65,536 points this means 2.32 million emitted rows before reduction.
RayJoin's implementation fuses this around its specialized layout and reports a
tighter GPU query metric.

This is why the next leap should be a generic RTDL primitive/runtime extension,
not RayJoin-specific native code:

- generic first-hit / nearest-boundary support for ray-or-segment probes;
- generic device-resident grouped count/parity/reduction over prepared-scene
  row streams;
- optional device-side exact refine plus reduction before host-visible rows.

This does not have to wait for v3.0 custom shader injection. It fits a v2.x
runtime/primitive roadmap as long as the contracts stay generic. v3.0 becomes
relevant only if we want users to inject their own traversal shaders or custom
device predicates.

## Claim Boundary

This goal authorizes:

- RTDL v2.0 can express RayJoin LSI and PIP evidence contracts using generic,
  app-agnostic primitives.
- RTDL's current same-contract PIP route matches RayJoin's exported positive
  point set at 4,096 and 65,536 queries on the tested pod.
- The remaining RayJoin performance gap is precisely characterized.

This goal does not authorize:

- RTDL beats RayJoin;
- full RayJoin paper reproduction;
- broad RT-core speedup;
- whole-application speedup;
- true zero-copy;
- v2.0 release authorization.

## Verdict

Current-v2.0 RayJoin correctness/evidence work is complete enough to close this
round. Performance parity with RayJoin needs larger generic v2.x
primitive/runtime work. It should not be solved by putting RayJoin-specific code
inside the RTDL engine.
