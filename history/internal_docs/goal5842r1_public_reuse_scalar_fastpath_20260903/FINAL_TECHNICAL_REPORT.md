# Goal5842R1 public reuse and scalar fast-path report

Date: 2026-09-04

## Status

Goal5842R1 is internally complete at the implementation-repair scope:

`PASS__GOAL5842R1_INTERNAL_IMPLEMENTATION_REPAIR_COMPLETE__FRESH_FAIR_BASELINE_AND_EXTERNAL_REVIEW_PENDING`

The repair preserves the public V4 admission boundary while removing three
avoidable costs identified by Goal5842: repeated formal-leaf compilation,
repeated triangle query upload, and host materialization of a per-ray vector
when the public contract asks for one checked-U64 scalar.

This is an internal engineering result. It is not a fresh Direct/PyOptiX/RTDL
baseline, public speedup claim, manuscript result, external review, or
consensus. The formal Goal5842 V12 evidence remains unchanged.

## Why this is substantive

Formal Goal5842 V12 established that public generic admission is measurable
but does not explain the dominant implementation gap. On the RTX A6000,
triangle steady execution was 23.653 ms because the public path materialized a
per-ray vector on the host and then reduced it. Merely deleting admission
checks would not fix that architecture.

Goal5842R1 changes the ownership and execution boundary instead:

1. `FormalNumbaLeafCachePolicy` gives the public toolchain an explicit,
   content-addressed formal-leaf cache. Cache hits revalidate the full key,
   artifact identity, PTX audit, and optional sealed manifest membership.
2. A prepared triangle owner retains target/GAS/pipeline state and publishes
   one exact immutable query batch only after successful native execution and
   traversal audit.
3. Re-executing the exact published tuple objects checks the native 32-byte
   digest and reuses device inputs without a second Python scan, upload, or GAS
   rebuild. Equal-but-distinct replacement tuples intentionally miss and are
   fully validated.
4. The ordinary public route defaults to `include_diagnostics=False` and calls
   the generic native v7 checked-U64 scalar operation. It performs one
   `optixLaunch`, validates a 12-byte control record, returns one 8-byte scalar,
   and does not materialize per-ray or event rows on the host.
5. `include_diagnostics=True` remains available and preserves the detailed
   per-ray route for debugging and oracle checks.

No application-specific graph, database, triangle-counting, or paper
semantics were added to the engine. The native operation is generic
triangle-hit traversal plus checked-U64 sum or product-sum reduction.

## Frozen boundaries

- Goal5842 V12 source commit:
  `04305fc820290cc183a599376f13d2fb48175233`.
- Goal5842 V12 final authority seal:
  `5c8044d9204df6b5d622142aecab8fcd25990e2ca1a19c7c5055ef4e16a31e43`.
- Goal5842R1 implementation source commit:
  `207e7afc4afd44ddef537f74d97c47ae323743b2`.
- The three Goal5838 frozen semantic-core files are byte-identical to their
  blobs at the R1 implementation commit.
- Goal5842R1 did not modify any file under the formal Goal5842 V12 evidence
  directory.

## Attempt chronology

All failures were retained rather than replaced by only the favorable result.

| Attempt | Source | Outcome | Finding |
|---|---|---|---|
| V1 | `888b953d4` | Pass, adverse | Explicit leaf-cache reuse worked, but scalar steady remained 23.249 ms. Device scalar output alone did not remove the bottleneck. |
| V2 | `0d3c2fa8f` | Fail before output | Host validation expected the older v5 receipt instead of the existing lean v7 ABI. No timing row was accepted. |
| V3 | `1e1188b72` | Fail before GPU | Remote command omitted `PYTHONPATH=src:.`. No timing row was accepted. |
| V4 | `1e1188b72` | Fail before added probe | The extra all-hit batch omitted explicit `query_metadata={}`. No result JSON was accepted. |
| V5 | `66be2dcc9` | Pass, adverse | Correct v7 scalar path and cross-family probes passed, but scalar steady remained 23.111 ms. |
| V6 | `f518fa22a` | Layer diagnostic | Public and provider layers were about 23 ms while direct native v7 was 0.069 ms, isolating overhead above the native call. |
| V7 | `207e7afc4` | Layer diagnostic | Exact-object reuse before the linear scan reduced public-layer median to 0.276 ms. |
| V8 | `207e7afc4` | Complete pass | Full workload and cross-family validation passed; scalar median was 0.289 ms. |
| V9 | `207e7afc4` | Complete repeat | Independent fresh-directory repeat passed; scalar median was 0.294 ms. |
| V10 | `207e7afc4` | Complete repeat | Third fresh-directory repeat passed through the new SSH endpoint; scalar median was 0.295 ms. |

V2, V3, and V4 did not write accepted JSON results. Their failure records are
part of this evidence packet.

## Evidence environment

V1 and V5 through V10 used one NVIDIA RTX A6000:

| Field | Value |
|---|---|
| GPU UUID | `GPU-6457d4af-a4bb-bff5-a9d2-02f251ceca27` |
| Compute capability | 8.6 |
| Driver | 550.127.08 |
| VRAM | 49,140 MiB |
| Python / Numba / NumPy | 3.12.3 / 0.65.1 / 2.4.4 |
| OptiX SDK | 7.7.0 |
| Native DSO SHA-256 | `04f319f805eaf8e420227d20b5d30cbe8a220b928112fe8915e16de0ea912a3f` |
| R1 workload | 16,384 queries and 16,384 triangles |
| Input SHA-256 | `d994f80418995342d0faa4bda84b42c2ef3604b2798de413a2813dd28dc039a7` |
| Expected weighted scalar | 65,530 |

The V10 endpoint was `root@38.147.83.21:44968` using the project Pod key. It
resolved to the same persistent GPU UUID and workspace as V8/V9. Therefore
V8-V10 are repeatability evidence on one machine, not independent hardware
replications.

## Results

### Formal-leaf materialization

| Attempt | Uncached median | Explicit cache-hit median | Ratio |
|---|---:|---:|---:|
| V1 | 1,260.878 ms | 130.700 ms | 9.65x |
| V5 | 1,220.772 ms | 147.339 ms | 8.28x |
| V8 | 1,235.669 ms | 130.893 ms | 9.44x |
| V9 | 1,255.567 ms | 136.473 ms | 9.20x |
| V10 | 1,259.544 ms | 131.568 ms | 9.57x |

The cache removes isolated Numba recompilation, but a hit still costs roughly
131-147 ms because the current materialization path reconstructs and validates
the complete executable. R1 does not claim zero-cost materialization.

### Triangle steady execution

Each complete run used eight untimed warmups and 64 alternating timed samples
per route. Medians are descriptive and every raw sample remains in the JSON.

| Attempt | Public scalar | Diagnostic per-ray | Diagnostic / scalar |
|---|---:|---:|---:|
| V1 | 23.249 ms | 23.674 ms | 1.02x |
| V5 | 23.111 ms | 23.304 ms | 1.01x |
| V8 | 0.289 ms | 0.745 ms | 2.58x |
| V9 | 0.294 ms | 0.757 ms | 2.57x |
| V10 | 0.295 ms | 0.762 ms | 2.58x |

The three post-fix scalar medians span 0.289-0.295 ms, a 2.09% range relative
to their mean. The V6-to-V7 public-layer median changed from 23.019 ms to
0.276 ms, or 83.30x descriptively. Direct native v7 remained essentially
unchanged at 0.0689 ms before and 0.0663 ms after. This isolates the fixed
cost to repeated Python-side immutable-input scanning rather than a new OptiX
kernel.

For context only, formal V12 measured the old RTDL triangle steady route at
23.653 ms on this same GPU. Dividing that historical value by V8-V10 yields
80.14-81.84x. This is not a new preregistered three-provider comparison and is
not authorized as a paper speedup claim.

### Reused scalar execution receipt

V8, V9, and V10 each record all of the following on the final reused public
scalar execution:

- one `optixLaunch`;
- zero dynamic upload calls and zero dynamic upload bytes;
- zero dynamic acceleration builds;
- no per-ray U64 or event-row host materialization;
- one 12-byte control download before output;
- one 8-byte public scalar download;
- no auxiliary CUDA status or reduction kernels;
- exact scalar and diagnostic per-ray oracle agreement.

The separate unweighted `ALL_HIT_COUNT` probe also passed and reused the same
generic scalar path at 0.353, 0.314, and 0.318 ms in V8-V10.

### Cross-family scope

The bounded-relation public route passed its exact oracle in V5 and V8-V10,
and public formal-leaf caching applies to both admitted families. Its reused
execution remained 13.26-13.50 ms because its public contract returns, sorts,
and validates 4,096 rows. It is not the scalar-only triangle route, and R1 does
not claim to have removed that row-output cost.

## Correctness and safety

The local regression set covers:

- explicit policy precedence over environment configuration;
- create-only and sealed read-only cache behavior;
- exact cache key, manifest, PTX audit, and artifact identity validation;
- public toolchain propagation for both admitted families;
- commit-after-success input publication;
- native digest mismatch and changed-input rebuilds;
- exact-object cache hit without a second linear scan;
- equal-but-distinct metadata tuple revalidation;
- scalar route exclusion of diagnostic and host reduction helpers;
- malformed receipt and compact-device-status fail-closed behavior;
- checked-U64 sum and product-sum modes;
- non-Boolean diagnostics rejection.

The public fast path does not trust Python identity alone. Identity is a
necessary O(1) candidate check after successful immutable publication; the
native owner digest must also match before reuse is accepted.

## Remaining work

1. Preregister and run a fresh same-commit, same-input, same-output
   Direct/PyOptiX/RTDL comparison. V12 cannot be retrospectively rewritten.
2. Obtain deferred independent external review before any public or manuscript
   performance wording.
3. Decide whether complete executable materialization can itself be cached;
   formal-leaf cache hits still take about 0.13 s.
4. Optimize row-returning continuation separately. The relation route is not
   evidence that scalar reuse failed.
5. Treat human ease-of-use evidence as unavailable unless Goal5841 is later
   run with a genuinely independent external developer.

## Verification

From the repository root:

```bash
PYTHONPATH=src:. /Users/rl2025/.venvs/rtdl-goal5837-py312/bin/python \
  -m unittest tests.goal5842r1_internal_authority_test

PYTHONPATH=src:. /Users/rl2025/.venvs/rtdl-goal5837-py312/bin/python \
  scripts/goal5842r1_build_internal_authority.py --verify-stored

PYTHONPATH=src:. /Users/rl2025/.venvs/rtdl-goal5837-py312/bin/python \
  scripts/goal5842_build_final_authority.py --verify-stored
```

The controlling R1 authority is `GOAL5842R1_INTERNAL_AUTHORITY.json` in this
directory. It hash-binds this report, the hostile self-review, every accepted
and failed attempt record, the implementation files, the frozen-core files,
and the unchanged Goal5842 V12 authority.
