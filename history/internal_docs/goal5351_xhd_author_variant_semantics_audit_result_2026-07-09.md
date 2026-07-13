# Goal5351 X-HD Author Variant Semantics Audit Result

Status: `implemented_review_pending`

## Purpose

Goal5349 closed a narrow user-facing gap: the RTDL `hd_exec`-compatible runner
now accepts the author variant names `eb`, `nn`, `itk`, `clover`, and `rt`.
That does **not** mean RTDL reproduces the author algorithms or performance
denominators for those variants.

Goal5351 audits the author source and Figure-5 scripts so the project has a
durable, machine-checkable matrix for:

- what each author variant flag maps to in C++/CUDA;
- what Figure-5 label it corresponds to;
- what RTDL currently supports;
- which claims remain forbidden.

## Artifact

```text
Paper-reproduction-apps/x-hd-paper/results/xhd_goal5351_author_variant_semantics_audit.json
```

Generation command:

```text
py Paper-reproduction-apps/x-hd-paper/scripts/build_xhd_goal5351_variant_semantics_audit.py \
  --author-source-root .codex_tmp/xhd_author_src \
  --output Paper-reproduction-apps/x-hd-paper/results/xhd_goal5351_author_variant_semantics_audit.json
```

The script verified the expected source snippets against the pinned author
commit checkout:

```text
source_verification_status = source_expectations_matched
author main commit = 7bf41c8442d059c94f4178355c6d5a10571d9658
paper branch commit = 8c3846866052e1e8755210021f23fac2cbe8c3d6
```

## Findings

Author `hd_exec` variant mapping:

```text
eb      -> Variant::kEarlyBreak             -> HausdorffDistanceEarlyBreak
nn      -> Variant::kNearestNeighborSearch  -> HausdorffDistanceNearestNeighborSearch
clover  -> Variant::kClover                 -> HausdorffDistanceClover
itk     -> Variant::kITK                    -> HausdorffDistanceITK
rt      -> Variant::kRT                     -> HausdorffDistanceRT / XHD
```

Figure-5 script labels:

```text
EB        = eb_gpu
NN-KD     = nn_gpu
NN-Clover = clover_gpu
ITK       = itk_cpu, MRI/image baseline only
X-HD      = rt_gpu
RT-HDIST  = external script baseline, not an hd_exec variant
```

Important CLI note:

```text
main.cpp parses compare-methods into Variant::kCompareMethods, but
RunHausdorffDistanceImpl has no switch case for it. Goal5351 therefore does not
treat compare-methods as a supported paper variant surface.
```

## Current RTDL Status

RTDL currently has:

```text
value surface:
  all author variant names accepted for directed HDResult output

algorithm surface:
  full author variant algorithm parity = false
  partial: rt value route on Level-B representative artifacts
  not closed: eb, nn, clover, itk, RT-HDIST external baseline

performance surface:
  author variant performance parity = false
```

For non-`rt` variants, the current RTDL behavior is explicitly:

```text
author_variant_value_compatible_route_only
```

For `rt`, the current RTDL behavior is stronger but still bounded:

```text
partial_level_b_value_route
```

RTDL has generic cell-MBR / native OptiX routes that match Level-B directed
HD values and an `hd_exec`-compatible exact-witness route on reviewed
representative artifacts. It still does **not** claim author RT-core algorithm
identity.

## Claim Boundary

The artifact sets all of the following to `false`:

```text
full_xhd_paper_reproduction_claimed
figure5_reproduction_claimed
author_variant_algorithm_equivalence_claimed
author_variant_performance_parity_claimed
rtdl_accepts_all_author_variant_names_as_algorithm_equivalent
rt_hdist_reproduced
```

## Validation

Commands run:

```text
py -m json.tool Paper-reproduction-apps/x-hd-paper/results/xhd_goal5351_author_variant_semantics_audit.json

py -m unittest \
  tests.goal5351_xhd_author_variant_semantics_audit_test \
  tests.goal5349_xhd_hd_exec_variant_value_surface_test \
  tests.goal5350_xhd_functional_parity_matrix_amendment_test
```

Result:

```text
Ran 11 tests in 1.614s
OK
```

The local Windows `py` launcher printed the known noisy environment warning:

```text
Could not find platform independent libraries <prefix>
```

The tests passed.

## Interpretation

Goal5351 closes an ambiguity in the functional-parity matrix. It confirms that:

- Goal5349 improved the user-facing option surface;
- accepting `eb/nn/itk/clover/rt` names is not algorithm reproduction;
- Figure 5 still cannot be called reproduced from variant-name support;
- future work must either implement algorithm-equivalent baselines or classify
  those baselines as external author baselines.

Recommended next actions:

```text
1. Decide external baseline policy for ITK, NN-KD, NN-Clover, EB, and RT-HDIST.
2. For the main X-HD algorithm, target RT-specific gaps:
   radius growth, LB/heavy-cell offload, Figure 7/11 counters.
3. Do not claim Figure 5 completion from Goal5349/5351.
```

Exit label:

```text
author_variant_semantics_audit_ready__non_rt_algorithm_parity_not_closed
```
