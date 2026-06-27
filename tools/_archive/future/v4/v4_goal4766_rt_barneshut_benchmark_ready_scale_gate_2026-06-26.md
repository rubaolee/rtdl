# Goal4766 - RT-BarnesHut Benchmark-Ready Scale Gate

Date: 2026-06-26

Status: **completed as benchmark-readiness evidence, pending external review debt**

## Purpose

Make the Goal4765 native RT-BarnesHut author-semantics RT-core candidate
benchmark-ready by:

1. splitting cold initialization from warm execution;
2. adding 32768 and 1M scale gates;
3. comparing against the authors' RT-core binary on the same POD and same input
   rows;
4. preserving all non-release claim boundaries.

This is still **not** a public paper-reproduction claim and **not** a release
authorization.

## What Changed

- Added `scripts/v4_rt_barneshut_native_benchmark_ready_probe.py`.
  - Runs the native candidate repeatedly in one Python process.
  - Records cold run separately from warm runs.
  - Optionally runs the authors' `rtbarneshut` binary against a trimmed
    same-input dataset.
  - Compares native warm checksum to author RT checksum without invoking the
    1M CPU oracle.
  - Keeps public speed, paper reproduction, and V2/V3/V4 speed-table claims
    unauthorized.

- Added `tests/v4_goal4766_rt_barneshut_benchmark_ready_probe_test.py`.

## Validation

Local:

```bash
py -m unittest tests.v4_goal4766_rt_barneshut_benchmark_ready_probe_test
```

Result: `Ran 2 tests ... OK`.

POD:

```bash
/root/rtdl_v4_venv/bin/python -m unittest \
  tests.v4_goal4766_rt_barneshut_benchmark_ready_probe_test
```

Result: `Ran 2 tests ... OK`.

POD hardware:

```text
NVIDIA RTX A5000
V4 root: /root/rtdl_v4_candidate_pod
Author binary: /root/external/RT-BarnesHut-author/build/rtbarneshut
Dataset: /root/external/RT-BarnesHut-author/treelogy_synthetic_1M.txt
```

## Evidence

- `future/v4/evidence/rt_barneshut_author_reproduction_2026-06-26/v4_goal4766_benchmark_ready_32768_pod_2026-06-26.json`
- `future/v4/evidence/rt_barneshut_author_reproduction_2026-06-26/v4_goal4766_benchmark_ready_1m_pod_2026-06-26.json`

## Results

### 32768 Points

Native V4 candidate:

- all native runs used `implementation_status_code=3`;
- all native runs had `rt_core_execution=true`;
- no native run used host fallback;
- warm checksum was stable.

Author-binary checksum comparison:

- author RT force checksum: `0.000576934`;
- native warm checksum: `0.0005769333559850764`;
- relative checksum error: `6.440149235295914e-10`;
- passes tolerance: true.

Timing:

| Metric | Native V4 Candidate | Authors' Binary |
|---|---:|---:|
| Cold RT-force seconds | `0.862805547` | n/a |
| Warm RT-force seconds, median | `0.006929028` | `0.05993` |
| Warm execution seconds, median | `0.0298711415` | `0.375931` |
| Author preprocessing seconds | n/a | `0.252454` |
| Author wall seconds | n/a | `3.716809246689081` |

Interpretation: 32768 is a strong candidate result. The native warm RT-force
path is much faster than the authors' reported RT-force region for the same
trimmed input on the same POD. This remains review-gated because the native
route uses custom-primitive control geometry rather than the authors' OWL
triangle module directly.

### 1M Points

Native V4 candidate:

- all native runs used `implementation_status_code=3`;
- all native runs had `rt_core_execution=true`;
- no native run used host fallback;
- warm checksum was stable.

Author-binary checksum comparison:

- author RT force checksum: `0.539531`;
- native warm checksum: `0.5395308770540055`;
- relative checksum error: `1.2294599449624855e-7`;
- passes tolerance: true.

Timing:

| Metric | Native V4 Candidate | Authors' Binary |
|---|---:|---:|
| Cold RT-force seconds | `0.901428045` | n/a |
| Warm RT-force seconds, median | `0.090850561` | `0.094797` |
| Warm RT-force seconds, min | `0.080498396` | `0.094797` |
| Warm execution seconds, median | `0.7451439795` | `1.04442` |
| Author preprocessing seconds | n/a | `0.890979` |
| Author wall seconds | n/a | `6.449731435626745` |

Interpretation: 1M is a serious-scale result. Native V4 is checksum-aligned with
the authors' RT output and is roughly comparable to slightly faster than the
authors' RT-force region on the same POD. The larger execution gain comes partly
from preprocessing differences, so it must not be reduced to a simple public
"V4 is X faster" headline without external review.

## Claim Boundary

Allowed internal statement:

> RTDL V4 now has a native, checksum-valid RT-BarnesHut author-semantics RT-core
> candidate that passes 4096, 8192, 32768, and 1M same-input checks on the RTX
> A5000 POD, with 1M warm RT-force timing in the same range as the authors'
> binary.

Still unauthorized:

- public RT-BarnesHut paper-reproduction wording;
- public speedup claims;
- V2.14/V3/V4 RT-BarnesHut speed tables;
- no-copy or device-resident tree-build claims;
- claim that the route is identical to the authors' OWL implementation;
- broad V4 high-performance release authorization.

## Remaining Technical Caveats

- The native route still downloads input columns to host to build author-style
  tree metadata.
- The route uses OptiX custom primitives approximating the authors' triangle
  control geometry. The checksum evidence is strong, but an external reviewer
  should decide whether literal triangle geometry is required for paper
  reproduction wording.
- Cold runs include OptiX/NVRTC pipeline initialization; public benchmark tables
  must explicitly distinguish cold and warm timing.
- The 1M source is serious scale, but the paper also reports larger Treelogy
  inputs such as 10M. That should be a follow-up scale gate before any paper
  comparison claim.

## Next Engineering Work

Goal4767 should prepare external-review and publication readiness:

1. Run or explicitly defer a 10M Treelogy same-input gate.
2. Ask external reviewers whether the custom-primitive geometry is acceptable
   or whether literal triangle geometry is required.
3. If accepted, create a narrowly scoped RT-BarnesHut paper-reproduction
   appendix with cold/warm timing split and no V2/V3/V4 overclaim.
4. If not accepted, implement literal triangle geometry before any paper-facing
   wording.

## Goal-Level Decision Audit

1. Was I foolish?
   - Not in the main path. The key correction was to avoid using the 1M CPU
     oracle and instead compare native checksum against the authors' patched RT
     checksum.

2. What action would have made it foolish?
   - Running the old Goal4761 wrapper at 1M would have buried the test under CPU
     oracle work and confused benchmark-readiness with oracle cost.

3. Was there another path?
   - Yes: reuse the already audited author-binary checksum emission and compare
     it directly against the native warm route at scale.

4. What different path is now active?
   - Goal4766 uses a dedicated benchmark-ready probe that separates cold/warm
     native timing and author-binary reference timing without authorizing public
     claims.
