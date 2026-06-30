# Goal1206 Live Pod Result And Embree4 Recovery

Date: 2026-05-01

Status: `EVIDENCE_READY_FOR_REVIEW`

## Pod

- Host: `103.196.86.68:29654`
- GPU: NVIDIA GeForce RTX 4090, 24564 MiB
- Driver: `550.127.05`
- Original Goal1204 artifact:
  - `docs/reports/goal1204_live_pod_2026-05-01/goal1204_repaired_rtx_pod.tgz`
  - SHA256: `4f2674d27ee3a0947e080c565da1af5330be11d8b49d76328056d8522238d7d8`
- Embree4 recovery artifact:
  - `docs/reports/goal1204_embree4_usr_recovery_live_pod_2026-05-01/goal1204_embree4_usr_recovery.tgz`
  - SHA256: `cc4778da52198efcf451101283aeb7a0dd2d8f335b9e58a1d7e364fb188aa953`

## Environment Finding

The initial Goal1204 pod installed Ubuntu `libembree-dev`, which provides Embree 3 headers/libraries. RTDL's current native Embree source requires Embree 4 (`embree4/rtcore.h`, `-lembree4`). Therefore the initial Embree control rows failed at compile time before running any app work.

Recovery action:

- Installed Embree 4.4.0 from the official RenderKit release tarball.
- Exposed the vendor layout through `/usr/include/embree4` and `/usr/lib/libembree4.so` symlinks because the current Linux runtime hardcodes `/usr` and ignores `RTDL_EMBREE_PREFIX`.
- Reran only the failed Embree controls into a separate recovery artifact.

This preserves the original failure history and avoids rerunning already-successful OptiX/Jaccard rows.

## Merged Intake

Merged report:

- `docs/reports/goal1206_repaired_rtx_recovery_merge_intake_2026-05-01.md`
- `docs/reports/goal1206_repaired_rtx_recovery_merge_intake_2026-05-01.json`

| App / Path | Embree sec | OptiX sec | Ratio Embree/OptiX | Result |
| --- | ---: | ---: | ---: | --- |
| DB compact-summary 100k | 0.338303 | 0.301344 | 1.12265 | repair passed |
| DB compact-summary 300k | 1.05533 | 0.906979 | 1.16357 | repair passed |
| Road hazard 40k | 0.814722 | 0.230652 | 3.53225 | same-scale floor-safe positive candidate |
| Jaccard 8192 chunk 512 | n/a | 1.19001 | n/a | public-safe chunk parity passed |
| Jaccard 8192 chunk 64 | n/a | 1.2714 | n/a | diagnostic-only, parity false |

## Boundary

This report is evidence intake only. It does not authorize public docs, release, or public RTX speedup wording. The merged evidence requires external review and a separate public wording decision before promotion.

## Follow-Up Code Fix

The Linux Embree runtime should respect `RTDL_EMBREE_PREFIX` the same way Windows does. Today, Linux defaults to `/usr`, which caused an avoidable pod setup failure even after Embree 4 was installed under `/opt/embree-4.4.0`.
