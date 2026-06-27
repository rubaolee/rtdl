# Phoenix V3 M12 Local Runner-Overhead Reduction

Status: `m12_local_runner_overhead_reduction_not_pod_not_release`

M11 showed that the Spatial LSI productized route had clean runtime-trunk
metadata but was slower than the old route. Jason's review required local
generic runner-overhead reduction before more POD.

```text
release_authorized: false
public_speedup_claim_authorized: false
broad_v3_faster_than_v2_claim_authorized: false
focused_pod_spend_authorized: false
full_all_app_pod_spend_authorized: false
```

## What Changed

The prepared-execution runner now supports two optional generic hooks:

- `measured_run_prepared`: a lightweight callable for measured repeats.
- `finalize_output`: a callable that builds the full output exactly once after
  measured repeats.

Default behavior is unchanged. Existing callers that do not pass these hooks
still use `run_prepared` for every repeat.

The Spatial LSI productized route now uses:

- `run_hot()` for the measured dense-count hot path.
- `finalize_run()` once after timing to build M3 table, prepared-handle
  metadata, claim boundaries, and the full payload.

No native algorithm changed. No POD was used for M12.

## Local Evidence

Microbench:
`docs/rebuild/v3/evidence/phoenix_v3_runner_overhead_m12_local_microbench_20260622.json`

| Local microbench metric | Value |
| --- | ---: |
| Heavy full runner call | `0.0009929465000168421s` |
| Heavy finalize-once runner call | `0.0008233700499986298s` |
| Finalize-once speedup vs full | `1.2059541150646593x` |
| Saved fraction | `0.17078105418100165` |

This is local overhead evidence, not POD performance evidence.

## Gates

Passed:

```text
py -3 -m unittest tests.v3_phoenix_runner_overhead_microbench_test tests.v3_phoenix_spatial_segment_intersection_runner_wiring_test tests.v3_phoenix_prepared_execution_session_runner_test
```

Result: `Ran 36 tests ... OK`

## Interpretation

M12 addresses the specific runner-inclusive overhead exposed by M11: repeated
rich payload construction inside the measured loop. The fix is generic and
available to any prepared-session caller whose steady-state output can be
measured separately from final payload construction.

It does not prove the Spatial LSI route is now faster on POD. It only creates a
local, testable overhead reduction that may justify a bounded rerun if reviewed.

## Goal-Level Decision Audit

Decision: Reduce generic prepared-execution runner overhead locally using
hot-repeat/finalize-once hooks.

1. Was I foolish?
   No.
2. If yes, what actions made the decision foolish?
   The foolish action would be to rerun POD before reducing the visible generic
   runner overhead.
3. Was there another path?
   Yes: retarget another Set-A family, but M11 review warned that this could
   hide a real runtime cost behind heavier work.
4. Can I now try a different path?
   Yes: document the local reduction and request 2-AI review before any focused
   rerun.
