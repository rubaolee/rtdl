# Goal4818 — RayJoin Public-Sample Correctness Gap Diagnosis

Date: 2026-06-30

Status: `goal4818_gap_diagnosis_complete_pending_review`

This goal continues Goal4817 under review debt. It is a user-mode diagnosis
only. It does not authorize performance benchmarking, RTDL runtime/native edits,
or paper reproduction claims.

## Boundary

The executor remained an RTDL user/application author.

No files under `src/rtdsl/**`, `src/native/**`, docs, examples, tutorials, or the
release surface were edited. The POD execution used the same clean v2.14 source
checkout from Goal4817:

- `/workspace/rtdl_goal4817_user_smoke_20260630_102224`
- HEAD `293883ce12e4663ed80c2a07c166a5b22286f7ef`
- source tree stayed clean after all probes

## Artifact Index

Copied artifacts:

- `history/internal_docs/goal4818_artifacts_2026-06-30/output_structure_comparison.json`
- `history/internal_docs/goal4818_artifacts_2026-06-30/output_gap_diagnosis_stage2.json`
- `history/internal_docs/goal4818_artifacts_2026-06-30/missing_segments_source_trace.json`
- `history/internal_docs/goal4818_artifacts_2026-06-30/output_window_1678_1705.txt`
- `history/internal_docs/goal4818_artifacts_2026-06-30/author_sample_author_verbose_summary.json`
- `history/internal_docs/goal4818_artifacts_2026-06-30/author_sample_bundled_helper_embree_correctness_summary.json`

Remote raw artifacts remain under:

`/workspace/rtdl_goal4818_gap_diag_20260630`

## Inputs Compared

Author public sample:

- left: `/workspace/RayJoin_fresh/test/dataset/br_county_clean_25_odyssey_final.txt`
- right: `/workspace/RayJoin_fresh/test/dataset/br_soil_ascii_odyssey_final.txt`
- answer: `/workspace/RayJoin_fresh/test/dataset/br_countyXbr_soil_answer.txt`

RTDL output from Goal4817:

- `/workspace/rtdl_goal4817_user_smoke_artifacts_20260630/author_sample_bundled_helper_correctness/rtdl_overlay_output.txt`

## Author Binary Health

The author `polyover_exec -mode=rt -output ...` reproduced the author answer
byte-for-byte on the same public sample.

Therefore the author answer is valid for this environment, and the RTDL mismatch
is not caused by a stale or invalid answer file.

## Primary Structural Finding

The RTDL output mismatch is not a pure formatting difference.

Summary from `output_structure_comparison.json`:

| Metric | Author answer | RTDL bundled helper |
| --- | ---: | ---: |
| output chains | 64,459 | 64,453 |
| total output points | 673,371 | 673,359 |
| unique output faces | 19,399 | 19,504 |

Common chain id comparison:

- full match: 266 chains
- same geometry/span but different face ids: 1,420 chains
- geometry differs at the same chain id: 62,767 chains

The large same-id geometry difference is mostly a cascade from omitted short
chains, not a wholesale different overlay. Coordinate multiset comparison found:

- RTDL has **no extra coordinate records**.
- RTDL is missing **six** author coordinate records.
- all six missing records are 2-point output chains.

Missing author output chain ids:

- 1687
- 1693
- 5771
- 5788
- 36694
- 36733

The first omitted chain:

```text
author: 1687 2 17444 17445 0 1041
points:
-46.412457 -1.020858
-46.412193 -1.038026
```

After that omission, RTDL chain 1687 corresponds to author chain 1688 geometry,
and the sequence shifts. The same pattern repeats at the other five omissions.

## LSI Is Probably Not The Cause

The author verbose log reports:

```text
Map 0, Xsect: 20860 19916
Map 1, Xsect: 20860 17266
Total chains: 64459 Total faces: 19399
```

RTDL Goal4817 reports:

```text
lsi.intersection_count = 20860
output.chain_count = 64453
output.face_count = 19504
```

The LSI intersection count matches the author result. The six missing output
chains therefore appear downstream of LSI, most likely in point-location,
midpoint classification, or output-chain keep/flush semantics.

## PIP / SoS Contract Finding

The user-provided author-reply summary states that deterministic PIP requires
encoding the Simulation-of-Simplicity slope preference into `t_reported`:

```text
t_reported = t_edge + max(t_edge, 1.0) * (1.0 - tie_breaker) * 1e-14
```

with map-specific slope preference:

- `query_map_id == 0`: prefer larger slope
- `query_map_id == 1`: prefer smaller slope

The author HEAD source confirms the same direction in
`src/algo/rt_pip_custom.cu`:

```text
/* If im==0 we want the bigger slope, if im==1, the smaller. */
if ((query_map_id && !flag) || (flag && !query_map_id)) {
    continue;
}
```

The released RTDL native OptiX source currently uses the opposite slope
preference inside the equal-height comparison:

```text
const bool current_slope_gt = exact_slope > best_slope;
better = query_map_id == 0u ? !current_slope_gt : current_slope_gt;
```

and the existing `RTDL_RAYJOIN_CDB_ALLOW_EQUAL_TIES=1` knob only applies:

```text
nextafterf(report_t, +inf)
```

It does not implement the author-reply slope-dependent `t_reported` perturbation.

Goal4817 empirically confirmed that setting
`RTDL_RAYJOIN_CDB_ALLOW_EQUAL_TIES=1` did not change the RTDL output hash and did
not repair byte equality.

## Embree Cross-Check

An RTDL bundled-helper `backend="embree"` cross-check was attempted to separate
OptiX-specific tie behavior from Python output assembly. It did not run because
the clean POD environment did not have Embree installed/configured:

```text
RuntimeError: Embree is not installed at the configured prefix.
```

This is an environment gap for this diagnostic branch. It is not evidence that
Embree would or would not match the author answer.

## Diagnosis

The best current diagnosis is:

`blocked_by_released_rtdl_pip_sos_contract_gap`

More specifically:

1. RTDL's bundled helper reaches the right LSI intersection count.
2. RTDL misses six 2-point output chains on the author public sample.
3. Those omissions cascade into many face-id and chain-id differences.
4. The released RTDL OptiX PIP tie policy is inconsistent with the author source
   and author-reply deterministic `t_reported` rule.
5. The existing released equal-ties environment knob does not resolve it.

This diagnosis is strong enough to block exact RayJoin paper reproduction using
released RTDL v2.14 on this public sample.

It is not a request to modify RTDL inside this goal.

## What This Does And Does Not Prove

Proves:

- Author public sample answer is reproducible by author binary in the current POD.
- RTDL bundled-helper output is close but not byte-equivalent.
- The mismatch is narrow in geometry terms: six 2-point output chains are missing.
- The released RTDL PIP/SoS contract differs from the author-reply/source
  contract.

Does not prove:

- full Section 5.7 reproduction;
- generic RTDL+Numba reproduction;
- any performance result;
- that all mismatch comes only from slope tie policy;
- that RTDL should be patched in this line of work.

## Recommended Next Goal

**Goal4819 — RTDL user-mode reproduction closure decision.**

Purpose:

Decide the honest final label for this reproduction line before any larger run.

Recommended decision:

- For exact author-byte reproduction with released RTDL v2.14:
  `blocked_by_released_rtdl_pip_sos_contract_gap`.
- For bounded helper capability:
  `bundled_helper_runs_but_not_exact_author_reproduction`.
- For generic RTDL+Numba:
  still blocked/unproven because no full public overlay assembly route has been
  demonstrated and the clean environment lacked Numba.

Allowed next work:

- package Goal4816-A through Goal4818 into a final review packet;
- ask Claude/Antigravity to confirm whether this is a legitimate closure;
- optionally create a separate future product-gap proposal that says what RTDL
  would need to expose/fix later.

Forbidden:

- performance runs;
- runtime/native edits;
- calling current output exact reproduction;
- silently using private bundled helpers as generic-language evidence.

## Goal-Level Decision Audit

1. **Am I being foolish?**
   No. I stopped at correctness and found the real gap without editing RTDL.

2. **What would make this foolish?**
   Treating a near-match as success, running performance despite failed
   correctness, or patching RTDL while pretending to be a user.

3. **Is there another path that avoids being stuck?**
   Yes. Close this line honestly as a released-capability/SoS contract gap and
   propose future product work separately.

4. **Can I start a different path that truly solves the problem?**
   Yes, but not inside the current user-mode reproduction. The product path
   would require RTDL to expose/implement the author-compatible PIP SoS contract
   and a non-bundled overlay assembly API. That is future RTDL development, not
   this reproduction proof.

