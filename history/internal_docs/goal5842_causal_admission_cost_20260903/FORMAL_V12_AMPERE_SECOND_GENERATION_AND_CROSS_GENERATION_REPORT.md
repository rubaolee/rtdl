# Goal5842 formal V12 Ampere and cross-generation report

Date: 2026-09-03

## Status

The exact V12 transaction completed on an NVIDIA RTX A6000 (Ampere) after the
already verified RTX 2000 Ada transaction. Both use source commit
`04305fc820290cc183a599376f13d2fb48175233`, the same preregistration seal,
the same workloads, schedules, phase boundaries, statistics, and failure
rules. The GPU UUIDs and architecture generations differ.

The Ampere transaction passed all seven stages, 216 causal workers, 216
baseline subworkers, 108 baseline composites, all output-identity checks, and
the pod independent recount. A Mac recount reconstructed from the exact frozen
Git blobs reproduced the pod recount byte for byte.

The exact internal status is:

`PASS__GOAL5842_TWO_GENERATION_INTERNAL_EVIDENCE_GATE`

Goal5842 is therefore technically complete at its internal preregistered
scope. External review is still pending. This status authorizes no public or
manuscript performance claim and no cross-machine raw-time comparison.

## Evidence identity

| Field | Ada generation | Ampere generation |
|---|---|---|
| GPU | RTX 2000 Ada Generation | RTX A6000 |
| Compute capability | 8.9 | 8.6 |
| GPU UUID suffix | `...c951-01fc713ee1e9` | `...bff5-a9d2-02f251ceca27` |
| Driver | 580.159.04 | 550.127.08 |
| OptiX API | 9.0.0 | 7.7.0 |
| Transaction | `goal5842-ada-04305fc82-transaction12` | `goal5842-v12-ampere-a6000-transaction01` |
| Recount seal | `70305326...ab3` | `4590c10d...984` |

Shared immutable inputs:

- source commit: `04305fc820290cc183a599376f13d2fb48175233`;
- V12 preregistration whole-file SHA-256:
  `f90d49a1663338c729f86dd08cf3ce2b51a3845326fe349ec5b80759fd06e509`;
- V12 preregistration internal seal:
  `9bcb9876bca6234756c9c49b0caf12956fd87a13748a62074278194446e67570`.

Ampere evidence:

- complete archive:
  `pod_artifacts/goal5842_v12_ampere_a6000_complete.tar.gz`;
- archive bytes: 3,640,458;
- archive SHA-256:
  `df4e1e1062ffbb4907608ca61c0bd791d49f182889821ab4e75c382718e444a7`;
- members: 2,329 (1,776 regular files and 553 directories);
- second-generation authority:
  `V12_AMPERE_SECOND_GENERATION_AUTHORITY.json`;
- second-generation authority seal:
  `0b32261798db751b20e72776237f72c43072167e67ee4aae86784893a5d30f9c`;
- cross-generation authority: `V12_CROSS_GENERATION_AUTHORITY.json`;
- cross-generation authority seal:
  `5f755721a3c335786951e1bf091815fec609ecb4aa4498be2fddbe1da17ab3da`.

The preparation record is `V12_AMPERE_PREPARATION_NOTES.md`. It discloses two
pre-worker compatibility repairs: creating the OptiX installer prefix and
rebuilding pinned PyOptiX against OptiX 7.7 rather than accidentally selected
9.1 headers. Neither event reached worker zero or changed a registered input.

## Cross-generation causal result

The primary estimand is the within-block median duration difference between
cold public generic admission and private experiment-only unchecked
construction. Times are reported within each machine only.

| Generation | Task | Check on | Check off | Primary delta | Bootstrap 95% interval | Route negative control |
|---|---|---:|---:|---:|---:|---:|
| Ada | AABB relation | 60.372 ms | 22.155 ms | 38.034 ms | [37.660, 38.564] ms | -1.305 ms |
| Ada | Triangle weighted all-hit | 53.858 ms | 20.076 ms | 33.827 ms | [33.027, 34.430] ms | 0.909 ms |
| Ada | Sphere any-hit count | 46.381 ms | 17.575 ms | 27.699 ms | [23.260, 28.620] ms | -1.099 ms |
| Ampere | AABB relation | 83.756 ms | 28.078 ms | 55.690 ms | [55.378, 56.109] ms | -0.144 ms |
| Ampere | Triangle weighted all-hit | 74.667 ms | 24.966 ms | 49.808 ms | [49.597, 50.242] ms | -0.004 ms |
| Ampere | Sphere any-hit count | 64.341 ms | 21.808 ms | 42.776 ms | [42.194, 43.294] ms | 0.157 ms |

All six primary deltas are positive and all six registered intervals exclude
zero. The direction and diagnosis replicate across the two generations. No
Ada/Ampere raw-time ratio is computed because the machines differ in GPU,
driver, OptiX API, and host environment.

The unchecked arm remains private, unsafe, and unsupported. These results do
not recommend removing admission or weakening identity checks.

## Ampere fair-provider baseline

The baseline compares exact public inputs and outputs across Direct
CUDA/OptiX, the current NVIDIA PyOptiX-compatible API, and RTDL public
check-on. It compares current implementations, not identical hidden work.

| Task and arm | Setup | First complete execution | Steady complete execution |
|---|---:|---:|---:|
| Relation, Direct CUDA/OptiX | 411.943 ms | 1.099 ms | 1.014 ms |
| Relation, PyOptiX-compatible | 276.027 ms | 5.754 ms | 4.120 ms |
| Relation, RTDL public check-on | 2,825.146 ms | 27.990 ms | 12.882 ms |
| Triangle, Direct CUDA/OptiX | 404.634 ms | 0.159 ms | 0.081 ms |
| Triangle, PyOptiX-compatible | 335.281 ms | 0.372 ms | 0.154 ms |
| Triangle, RTDL public check-on | 2,027.688 ms | 50.264 ms | 23.653 ms |

All adverse ratios are retained. Relative to PyOptiX-compatible, RTDL is
10.21x/4.87x/3.13x on relation setup/first/steady and
6.08x/134.03x/155.21x on triangle. Relative to Direct, the corresponding
ratios are 6.85x/25.48x/12.71x and 5.03x/318.15x/295.16x.

The Ada transaction was also adverse. The magnitudes differ and are not pooled
or ratioed across machines. The replicated bounded conclusion is that current
RTDL remains materially slower than both matched alternatives for these two
routes.

## Ampere phase diagnosis

| Task | Route | Admission | Target/toolchain binding | Target materialization | Native prepare |
|---|---:|---:|---:|---:|---:|
| Relation | 59.246 ms | 83.570 ms | 14.637 ms | 2,130.353 ms | 539.628 ms |
| Triangle | 42.809 ms | 74.420 ms | 13.499 ms | 1,353.693 ms | 550.895 ms |

The primary admission delta explains descriptively about 2.18% of the
relation RTDL-minus-PyOptiX setup gap and 2.94% of the triangle gap. Against
Direct, the corresponding fractions are about 2.31% and 3.07%. These are
post-registered diagnostics formed from separately summarized medians, not
new estimands.

Target materialization plus native prepare is about 94.5% of RTDL relation
setup and 93.9% of RTDL triangle setup on Ampere. Ada reported the same
dominant phase class at about 95.1% and 96.6%. This cross-generation diagnosis
is the important engineering result: admission has a real measurable cost,
but weakening it cannot recover the multi-second current setup gap.

Triangle steady execution remains especially adverse because current public
RTDL materializes a per-ray host vector and reduces it on the host, while the
registered Direct and PyOptiX arms copy only the public weighted scalar. That
is an avoidable implementation debt, not a language lower bound.

## What Goal5842 establishes

1. Generic public admission has a measurable cold cost on all three tasks and
   both architecture generations.
2. That cost is not the dominant explanation for the current setup gap.
3. Target materialization and native prepare dominate setup on both machines.
4. The current triangle public route performs avoidable host continuation and
   is not a competitive lowering.
5. The public safety checker must remain; the next work is lifecycle reuse and
   backend/runtime optimization, not an unchecked user API.

## Claim ceiling

- V12 is disclosed post-result evidence because V11 timings were visible
  before the V12 validator-schema repair.
- V11 remains terminal and contributes no V12 row.
- No cross-machine raw-time ratio, pooled timing estimator, or
  hardware-independent magnitude claim is valid.
- Sphere has no fabricated three-provider baseline.
- The two tasks are not representative of arbitrary RT programs.
- External review and consensus are absent.
- Public and manuscript performance wording remains unauthorized.

## Verification

Run from the repository root with the project Python 3.12 environment:

```bash
PYTHONPATH=src:. /Users/rl2025/.venvs/rtdl-goal5837-py312/bin/python \
  scripts/goal5842_build_first_generation_authority.py --verify-stored

PYTHONPATH=src:. /Users/rl2025/.venvs/rtdl-goal5837-py312/bin/python \
  scripts/goal5842_build_second_generation_authority.py --verify-stored
```

The first command verifies the complete Ada archive and replays its recount.
The second does the same for Ampere and also requires the exported recount to
equal the archived and locally regenerated bytes.
