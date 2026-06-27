# Goal4769 - RT-BarnesHut Author Phase Accounting

Date: 2026-06-26

Status: **completed as apples-to-apples phase accounting, pending external review debt**

## Purpose

Goal4769 followed Goal4768's 10M profile. Goal4768 showed RTDL native V4
spending about `6.16s` in z-order sort, but it was still unclear whether this
was a V4-specific bottleneck or an artifact of comparing RTDL's internal
preprocessing against the authors' artifact-mode output.

Goal4769 therefore rebuilt the authors' binary with `PRINT_ARTIFACT=false` to
expose the authors' full phase table, ran the same 10M Treelogy input, restored
the authors' source back to `PRINT_ARTIFACT=true`, and rebuilt the original
artifact-mode binary.

## Evidence

Author phase output:

- `future/v4/evidence/rt_barneshut_author_reproduction_2026-06-26/v4_goal4769_author_phase_print_false_10m_stdout.txt`
- `future/v4/evidence/rt_barneshut_author_reproduction_2026-06-26/v4_goal4769_author_phase_print_false_10m_stderr.txt`

RTDL native comparison evidence:

- `future/v4/evidence/rt_barneshut_author_reproduction_2026-06-26/v4_goal4768_benchmark_ready_10m_pod_2026-06-26.json`
- `future/v4/evidence/rt_barneshut_author_reproduction_2026-06-26/v4_goal4768_10m_phase_profile_pod_2026-06-26.jsonl`

POD:

```text
NVIDIA RTX A5000
Author source: /root/external/RT-BarnesHut-author
Author dataset: /root/external/RT-BarnesHut-author/treelogy_synthetic_10M.txt
V4 root: /root/rtdl_v4_candidate_pod
```

## Method

On the POD:

1. Backed up `samples/cmdline/s01-rtbarneshut/hostCode.cu`.
2. Changed only:

   ```cpp
   #define PRINT_ARTIFACT true
   ```

   to:

   ```cpp
   #define PRINT_ARTIFACT false
   ```

3. Rebuilt `rtbarneshut`.
4. Ran the authors' binary on the same 10M Treelogy file.
5. Restored the backed-up source file and rebuilt artifact mode.

This was a temporary author-binary instrumentation step. It is not an RTDL
source change and it was reverted after collecting the evidence.

## Author Phase Table

The authors' `PRINT_ARTIFACT=false` 10M output:

| Author phase | Seconds |
|---|---:|
| Sort Time | `6.87096` |
| Tree build time | `1.71362` |
| Tree to DFS time | `0.043701` |
| Install AutoRopes time | `0.015301` |
| Intersections setup time | `0.484204` |
| RT Cores Force Calculations time | `1.12905` |
| CPU Force Calculations time | `0` |
| Iterative Step time | `1.76213` |
| Total Program time | `10.4391` |

This proves that the authors' normal artifact-mode `Execution time` is not the
full internal program time. It starts after sort/tree build and is therefore
not a fair denominator for RTDL native `execution_seconds`.

## RTDL V4 Phase Table

From Goal4768 warm 10M run:

| RTDL native phase | Seconds |
|---|---:|
| input_download | `0.0804588` |
| point_pack | `0.123256` |
| sort | `6.16351` |
| grid | `0.0444316` |
| bucket_build | `0.122523` |
| insert | `0.030328` |
| compute_com | `0.00845067` |
| count_nodes | `0.0105522` |
| dfs_metadata | `0.0150561` |
| auto_rope | `0.0111561` |
| pipeline_init | `0.000006815` |
| device_pack | `0.144908` |
| aabb | `0.00954911` |
| upload | `0.0292855` |
| accel_build | `0.00803325` |
| launch | `0.647495` |

From Goal4768 summary:

- warm RT-force: `0.886653679s`;
- warm execution: `7.432850354s`;
- checksum relative error vs author RT checksum: `9.051486889720442e-7`;
- checksum tolerance pass: true.

## Apples-To-Apples Comparison

| Metric | RTDL V4 Native | Authors' Binary | Interpretation |
|---|---:|---:|---|
| z-order sort | `6.16351s` | `6.87096s` | RTDL is not slower; it is about `1.11x` faster by time ratio. |
| sort + tree construction basis | `6.503060236s` native preprocessing | `8.58458s` author sort+tree-build | RTDL is about `1.32x` faster on this combined basis. |
| RT-force | `0.886653679s` | `1.12905s` | RTDL is about `1.27x` faster in this phase run. |
| internal program time excluding file read | `~7.51s` including input download, `7.43285s` without it | `10.4391s` | RTDL is about `1.39x` faster with input download included. |

The exact RTDL internal-program row is reported cautiously because RTDL's
native route is called from a prepared Python route and the author program is a
standalone executable. Adding RTDL `input_download_seconds` to warm
`execution_seconds` gives the conservative `~7.51s` value.

## Interpretation

Goal4769 changes the RT-BarnesHut diagnosis:

- The 10M z-order sort is not a V4-specific performance failure. The authors'
  own sort is slower on the same data when the phase is exposed.
- The earlier comparison against author artifact-mode `Execution time` was an
  unfair denominator because it excluded sort/tree build.
- On an apples-to-apples internal-program basis excluding file read, RTDL V4's
  native author-semantics RT-core candidate is faster than the authors' binary
  on the 10M Treelogy input.

This does not authorize broad public claims by itself. The route still has
these boundaries:

- input columns are downloaded for tree build;
- the RTDL route uses custom-primitive control geometry, not literal author
  triangle geometry;
- no V2/V3/V4 public RT-BarnesHut speed table is authorized yet;
- no no-copy or device-resident tree-build claim is authorized.

Allowed internal statement:

> After exposing the authors' full phase table, the 10M Barnes-Hut result no
> longer shows a V4 full-workflow loss. The authors' sort/tree phases were
> hidden by artifact-mode reporting. RTDL V4's native author-semantics RT-core
> candidate remains checksum-valid and is faster than the authors' binary on
> the comparable internal program time, but public paper-reproduction wording
> still requires external review and claim-boundary decisions.

## Next Engineering Work

Goal4770 should update the V4 app matrix and release packet so Barnes-Hut is no
longer treated as a "full workflow author loss" row. It should be classified
as:

- RT-core native V4 candidate;
- same-input/same-semantics checksum-valid at 10M;
- apples-to-apples internal-program win over author binary on the 10M Treelogy
  dataset;
- still blocked for no-copy/device-resident tree-build and paper-facing
  reproduction wording pending external review.

## Goal-Level Decision Audit

1. Was I being stupid?
   - The earlier phase comparison was wrong; Goal4769 fixed it.

2. What action made it stupid?
   - Treating the authors' artifact-mode `Execution time` and `Preprocessing
     Time` as if they included sort/tree build.

3. Is there another path that avoids a bad premise?
   - Yes. Rebuild the author binary with full phase printing and compare
     sort/tree/total program phases directly.

4. Can I now try the different path that actually solves the problem?
   - Yes. The next path is to update the app matrix and release packet with
     the corrected Barnes-Hut classification, while keeping public claims
     blocked until external review.
