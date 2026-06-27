# Goal4772 - RT-BarnesHut Four-Way Fair Compare

Date: 2026-06-26

Status: **completed as evidence/protocol, pending external review debt**

## Purpose

Goal4772 answered the user's direct question: can the authors' RT-BarnesHut
program, RTDL V2.14, RTDL V3.0.2, and RTDL V4.0 be compared fairly on the same
NVIDIA RT-core POD?

The answer is:

- yes, as a four-way capability and contract matrix;
- yes, for an apples-to-apples Author-vs-V4 timing comparison under the
  author-semantics contract;
- no, for fake V2.14/V3.0.2 timing ratios against the authors' binary, because
  V2.14 and V3.0.2 do not expose the same Goal4760 author-semantics route.

This file intentionally records the absent V2.14/V3 route as an explicit
capability result rather than writing `n/a`.

## Evidence

Primary machine-readable evidence:

- `future/v4/evidence/rt_barneshut_author_reproduction_2026-06-26/v4_goal4772_four_way_fair_compare_pod_2026-06-26.json`

Inputs used by the comparison script:

- author phase output:
  `future/v4/evidence/rt_barneshut_author_reproduction_2026-06-26/v4_goal4769_author_phase_print_false_10m_stdout.txt`
- V4 benchmark JSON:
  `future/v4/evidence/rt_barneshut_author_reproduction_2026-06-26/v4_goal4768_benchmark_ready_10m_pod_2026-06-26.json`
- V4 phase profile:
  `future/v4/evidence/rt_barneshut_author_reproduction_2026-06-26/v4_goal4768_10m_phase_profile_pod_2026-06-26.jsonl`

Script:

- `scripts/v4_goal4772_rt_barneshut_four_way_fair_compare.py`

Unit test:

- `tests/v4_goal4772_rt_barneshut_four_way_fair_compare_test.py`

Local validation:

```text
py -m unittest tests.v4_goal4772_rt_barneshut_four_way_fair_compare_test

Ran 1 test in 0.245s
OK
```

POD:

- GPU: NVIDIA RTX A5000
- author root: `/root/external/RT-BarnesHut-author`
- V2.14 root: `/root/rtdl_v2_14_tag`
- V3.0.2 root: `/root/rtdl_v3_0_2_tag`
- V4 root: `/root/rtdl_v4_candidate_pod`
- dataset: `/root/external/RT-BarnesHut-author/treelogy_synthetic_10M.txt`

## Contract

The fair contract is the Goal4760 RT-BarnesHut author-semantics contract:

- 10M Treelogy-format input;
- theta `0.5`;
- bucket size `32`;
- 3D author z-order tree;
- native author RT-force checksum required;
- historical aggregate-frontier Barnes-Hut benchmark rows must not be mixed into
  this comparison.

Required native V4 ABI symbols:

- `rtdl_optix_prepare_rt_barneshut_author_3d`
- `rtdl_optix_run_rt_barneshut_author_3d`
- `rtdl_optix_destroy_rt_barneshut_author_3d`

## Four-Way Result

| Row | Route status | Same author-semantics route? | Timing ratio allowed? | Result |
| --- | --- | --- | --- | --- |
| Author program | Reference author binary with full phase accounting | Yes | Reference denominator only | Full program `10.4391s`; RT-force `1.12905s`; sort `6.87096s` |
| RTDL V2.14 | Legacy Barnes-Hut-style adapter exists, but no Goal4760 author contract and no native author ABI | No | No | Explicit capability miss for this contract; do not divide timings |
| RTDL V3.0.2 | Legacy Barnes-Hut-style adapter exists, but no Goal4760 author contract and no native author ABI | No | No | Explicit capability miss for this contract; do not divide timings |
| RTDL V4.0 | Native same-semantics RT-core route present | Yes | Yes, against author | Checksum passes; internal program `7.513309154s`; RT-force `0.886653679s`; sort `6.16351s` |

The V2.14/V3.0.2 result is not `n/a`. It is a concrete finding: those versions
do not provide the same author-semantics route, so a fair speed ratio against the
authors' program is forbidden.

## V4 Correctness

Checksum evidence:

- native force checksum: `53.746751351154444`
- author RT-force checksum: `53.7468`
- relative error: `9.051486889720442e-7`
- tolerance: pass

This is why Author-vs-V4 timing is allowed.

## Fair Author-vs-V4 Ratios

The following ratios are valid under the same input and author-semantics
contract:

| Comparison | Author seconds | V4 seconds | Ratio |
| --- | ---: | ---: | ---: |
| Full internal program | `10.4391` | `7.513309154` | `1.3894144092875964x` |
| RT-force phase | `1.12905` | `0.886653679` | `1.27338331384739x` |
| Sort phase | `6.87096` | `6.16351` | `1.1147803767658364x` |
| Author sort+tree vs V4 preprocessing | `8.58458` | `6.503060236` | `1.3200831129438122x` |

Interpretation:

- V4 is faster than the authors' binary on this same-input, same-contract
  internal program comparison.
- The largest absolute time is still sorting/preprocessing, not RT-force.
- This does not authorize paper-reproduction wording or broad V4 speedup
  wording.

## Claim Boundary

Still blocked:

- public V4 tag;
- RT-BarnesHut paper-reproduction claim;
- broad V4-over-V2/V3 speedup wording;
- public V2/V3/V4 RT-BarnesHut speed table;
- no-copy or device-resident tree-build claim.

Allowed wording:

- V4 has a same-semantics native RT-core RT-BarnesHut route that V2.14 and
  V3.0.2 do not have.
- On the same 10M Treelogy input, V4 passes the author checksum and is `1.389x`
  faster than the authors' binary on internal program time in this POD run.
- V2.14 and V3.0.2 should be reported as explicit route-absence/capability
  findings for this contract, not as timing ratios.

## Goal-Level Decision Audit

1. Was I being stupid?
   - No for this goal. The comparison was forced onto a same-semantics contract
     and did not invent ratios for absent routes.

2. What action would make this stupid?
   - Dividing historical V2.14/V3 aggregate-frontier Barnes-Hut timings by the
     authors' RT-BarnesHut program and calling that a fair result.

3. Is there another path?
   - Yes. If a true four-way timing ratio is required, implement or backport the
     Goal4760 author-semantics route into V2.14/V3.0.2, then rerun. Until then,
     the honest result is explicit route absence for those versions.

4. Can I now try the different path that actually solves the problem?
   - Yes. The immediate solved path is the current capability/timing matrix. The
     optional future engineering path is author-semantics route backporting or a
     separate legacy-contract comparison.
