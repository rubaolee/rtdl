# Goal 1571: carry pointer diagnostic negative result

## Verdict

The opt-in carry pointer diagnostic preserves parity, but it is slower for the
odd-tile target case. Do not promote `RTDL_OPTIX_COLLECT_K_CARRY_POINTER_DIAGNOSTIC`
into the production `COLLECT_K_BOUNDED` path.

## Scope

- Pod: `root@157.157.221.29 -p 22942`
- Commit base while testing: `9f3ad77c` plus local Goal 1571 diagnostic edits
- Library: `build/librtdl_optix.so`
- Profile artifact:
  `docs/reports/goal1571_v1_5_4_optix_collect_k_carry_pointer_diagnostic_profile_2026-05-08.json`
- Counts: `65537`, `131072`
- Repeats: `3`
- Diagnostic flag: `RTDL_OPTIX_COLLECT_K_CARRY_POINTER_DIAGNOSTIC=1`

## Result

| candidates | parity | total ms | merge launch ms | merge sync ms | carry copy ms | metadata fields |
|---:|---|---:|---:|---:|---:|---:|
| 65537 | pass | 0.469720 | 0.314466 | 0.038906 | 0.033193 | 132 |
| 131072 | pass | 0.310408 | 0.090691 | 0.119977 | 0.000000 | 65 |

The `65537` profile is classified as diagnostic smoke rather than accepted
Goal1506 evidence because the topology/metadata accounting intentionally differs
from the expected fastest path. The parity gates passed.

## Interpretation

The diagnostic removes row-data carry copies by aliasing the carried segment,
but the existing pointer-descriptor path requires count downloads plus
descriptor/count uploads on every odd carry level. That overhead overwhelms the
saved row-copy work:

- prior post-fusion `65537` total: `0.281784 ms`;
- carry-pointer diagnostic `65537` total: `0.469720 ms`;
- prior post-fusion `65537` merge launch: `0.082206 ms`;
- carry-pointer diagnostic `65537` merge launch: `0.314466 ms`.

The no-carry `131072` case stays near the prior profile, which confirms that
the diagnostic flag is scoped to odd carry levels and does not perturb the
normal no-carry path materially.

## Next Direction

Do not continue with the existing host-count pointer descriptor carry alias
path. The only carry-copy direction still worth considering is a counts-aware
device descriptor design that avoids per-level count downloads/uploads, but it
should be attempted only if we want a larger kernel/API change.

For now, the measured evidence says carry-copy elimination through the existing
pointer path is not the next production optimization.

This result is diagnostic only and does not authorize public speedup wording.
