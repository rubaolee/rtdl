# Goal5842 formal V12 Ada first-generation report

Date: 2026-09-03

## Status

The create-only V12 transaction completed all seven stages on one NVIDIA RTX
2000 Ada GPU. All registered causal workers, provider-baseline workers, output
identity checks, and the original independent recount passed. A second local
recount, executed from the exact frozen Git blobs, reproduced the pod recount
byte for byte.

The exact bounded status is:

`PASS__V12_ADA_FIRST_GENERATION_EVIDENCE_VERIFIED__SECOND_GENERATION_REQUIRED`

This is not Goal5842 completion. The preregistration requires two distinct GPU
architecture generations. It authorizes no public performance claim, no
hardware-independent conclusion, no external review, and no consensus.

## Frozen identity

- Source commit: `04305fc820290cc183a599376f13d2fb48175233`
- V12 preregistration internal seal:
  `9bcb9876bca6234756c9c49b0caf12956fd87a13748a62074278194446e67570`
- V12 preregistration whole-file SHA-256:
  `f90d49a1663338c729f86dd08cf3ce2b51a3845326fe349ec5b80759fd06e509`
- Formal transaction root: `goal5842-ada-04305fc82-transaction12`
- Complete archive: `pod_artifacts/goal5842_v12_ada_complete.tar.gz`
- Archive bytes: `3,790,441`
- Archive SHA-256:
  `6dff96a2c76674f56a467ae10ef8e50045792cbf2fc6908c93296e092e8bff21`
- Archive members: `2,325` (`1,773` regular files and `552` directories)
- Machine-readable first-generation authority:
  `V12_ADA_FIRST_GENERATION_AUTHORITY.json`
- First-generation authority seal:
  `588462752860276987d12ab8d6bd0e71c8d371004268ad9e47d1d0b2bbf94006`

The pod endpoint was `root@213.173.108.100:12943`, reached with the local key
path `/Users/rl2025/.ssh/id_ed25519_rtdl_codex`. The evidence authority bound
the execution to GPU UUID
`GPU-f0ab2afa-0ec0-7da9-c951-01fc713ee1e9`, NVIDIA RTX 2000 Ada Generation,
compute capability 8.9, driver 580.159.04, CUDA 12.8, OptiX SDK 9.0.0, Python
3.12.3, PyOptiX 9.1.0, and its exact native, Direct, source, header, package,
and toolchain hashes.

## Transaction integrity

All seven formal stage return codes were zero and every stage stderr file was
empty:

1. bind execution authority;
2. timer-free RTDL GPU identity witness;
3. timer-free PyOptiX package-front-door witness;
4. timer-free Direct CUDA/OptiX witness;
5. causal admission cohort;
6. three-arm provider baseline;
7. independent recount.

The transaction contains 216 causal receipts, 216 baseline subworker receipts,
and 108 baseline composites. It contains no transaction-failure marker. The
independent recount file is 30,204 bytes at
`bf5206a86009a6f9c7519dff45a92d1f527035dc0d05a609fc88f59d762b1a89`;
its internal seal is
`70305326b122e15806f9a67353b259620fcbb85932f6bbc04f002b4c899bbab3`.

The post-execution authority builder rejects archive byte drift before
extraction, rejects unsafe or non-regular tar members, reconstructs all 73
frozen source-manifest paths from Git commit `04305fc8...`, and reruns the
original independent recount. The regenerated recount equals the archived pod
recount byte for byte.

## Causal admission result

The primary estimand is the median within-block difference between cold public
generic admission and the private experiment-only unchecked construction. It
is an absolute duration, not a ratio to the unchecked arm.

| Task | Check on median | Check off median | Primary delta | Bootstrap 95% interval | Route negative control |
|---|---:|---:|---:|---:|---:|
| Custom AABB closed relation count | 60.372 ms | 22.155 ms | 38.034 ms | [37.660, 38.564] ms | -1.305 ms |
| Built-in triangle weighted all-hit | 53.858 ms | 20.076 ms | 33.827 ms | [33.027, 34.430] ms | 0.909 ms |
| Built-in sphere any-hit count | 46.381 ms | 17.575 ms | 27.699 ms | [23.260, 28.620] ms | -1.099 ms |

Each task contributes 72 fresh-process workers arranged as 18 ABBA/BAAB
blocks. The secondary full route-to-capability deltas are 37.052 ms, 34.615
ms, and 25.680 ms respectively. No check-on/off output, executable, plan,
artifact, provider projection, or provider descriptor identity mismatch was
observed. The unchecked arm remains private and unsafe; this result is not a
recommendation to remove admission checks.

## Fair-provider baseline result

The two tasks below have honest Direct CUDA/OptiX, current NVIDIA
PyOptiX-compatible, and RTDL public check-on arms. Sphere is absent because no
matched Direct and PyOptiX baseline was frozen for it.

| Task and arm | Setup | First complete execution | Steady complete execution |
|---|---:|---:|---:|
| Relation, Direct CUDA/OptiX | 416.043 ms | 0.897 ms | 0.834 ms |
| Relation, PyOptiX-compatible | 317.506 ms | 3.879 ms | 2.823 ms |
| Relation, RTDL public check-on | 5,172.556 ms | 17.326 ms | 8.388 ms |
| Triangle, Direct CUDA/OptiX | 422.424 ms | 0.135 ms | 0.074 ms |
| Triangle, PyOptiX-compatible | 352.036 ms | 0.225 ms | 0.128 ms |
| Triangle, RTDL public check-on | 4,499.898 ms | 29.640 ms | 13.931 ms |

All ratios are adverse and are retained. Relative to PyOptiX-compatible, RTDL
is 16.08x/4.47x/3.00x on relation setup/first/steady and
12.56x/134.47x/108.75x on triangle. Relative to Direct, the corresponding
ratios are 12.29x/19.28x/10.06x and 10.47x/223.79x/188.95x. These are
one-machine implementation measurements, not intrinsic language-overhead
theorems.

The baseline compares the same frozen public inputs and exact public outputs.
It does not claim identical internal work. In particular, the registered
Direct and PyOptiX triangle intervals copy only the public weighted scalar,
while current RTDL also materializes an internal per-ray vector and reduces it
on the host. That extra work is a real cost of the current implementation, but
it must not be described as unavoidable RTDL language cost.

## Phase diagnosis

| Task | RTDL route | Admission | Target/toolchain binding | Target materialization | Native prepare |
|---|---:|---:|---:|---:|---:|
| Relation | 62.400 ms | 60.783 ms | 50.066 ms | 4,203.053 ms | 718.615 ms |
| Triangle | 47.974 ms | 54.516 ms | 41.512 ms | 3,643.482 ms | 703.679 ms |

The causal admission delta accounts descriptively for only 0.78% of the
observed relation RTDL-minus-PyOptiX setup gap and 0.82% of the triangle gap.
The analogous fractions against Direct are 0.80% and 0.83%. These percentages
combine separately estimated medians and are diagnostic, not additional
registered estimands.

Target materialization plus native prepare accounts for about 95.1% of the
relation RTDL setup median and 96.6% of the triangle RTDL setup median when the
independently reported phase medians are divided by setup median. This supports
one bounded engineering conclusion: weakening generic admission cannot recover
the current multi-second setup gap. The next optimization target is prepared
target reuse and removal of redundant materialization/host continuation, while
preserving admission and identity checks.

## Scientific interpretation

Goal5842 has produced valuable negative diagnosis rather than a favorable
performance result. The generic admission contract has a measurable cold cost
of about 28--38 ms on this Ada environment, but it is not the dominant source
of the observed RTDL overhead. The current implementation's target
materialization and native preparation dominate setup, and the triangle route
also exposes a severe internal-materialization execution debt.

This result narrows the CGO response to the performance concern. It allows the
paper to distinguish language safety-check cost from current backend/runtime
construction cost, but only after cross-generation replication and review. It
does not yet support a submission sentence with these timings.

## Claim ceiling and remaining gate

- V12 is not result-blind because V11's registered rows were visible before
  the arm-schema repair and V12 freeze.
- V11 remains a terminal failed transaction. No V11 row is pooled into V12.
- There was no preregistered success threshold, and every adverse V12 row is
  retained.
- One Ada GPU is one architecture generation, regardless of repeated runs or
  additional Ada UUIDs.
- No check-off ratio, cross-machine raw-time ratio, public performance claim,
  external review, consensus, or Goal5842 completion is authorized.
- The exact next action is the distinct-generation replay in
  `SECOND_GENERATION_REPLAY_PLAN_V12.md`.

## Local verification

Run from the repository root with the Python 3.12 environment:

```bash
PYTHONPATH=src:. /Users/rl2025/.venvs/rtdl-goal5837-py312/bin/python \
  scripts/goal5842_build_first_generation_authority.py --verify-stored
```

The command rehashes and safely extracts the complete archive, reconstructs
the exact source commit from Git, reruns the independent recount, and requires
the stored authority to equal the deterministic rebuild.

The focused Goal5842, prepared-cache, immutable-input, selected-sphere, and new
evidence-custody suites pass `78/78`. The combined Goal5840/Goal5842 run passes
`116/118`. Its two errors are the already disclosed historical Goal5840
repair-builder custody comparisons
`test_repair_authority_is_append_only_and_preserves_scientific_inputs` and
`test_attempt02_repair_authority_preserves_both_failures_and_inputs`; each
compares a later legitimate current tree to old attempt-local frozen inputs.
They are neither hidden nor repaired by rewriting historical evidence, and no
Goal5842 test fails.
