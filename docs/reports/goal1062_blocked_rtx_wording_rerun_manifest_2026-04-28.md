# Goal1062 Blocked RTX Wording Rerun Manifest

Date: 2026-04-28

Valid: `True`

Goal1062 prepares one batched rerun plan for any remaining blocked NVIDIA RTX wording rows. It does not run cloud, create resources, authorize release, or authorize public speedup wording.

## Global Preconditions

- Run only from an already-running RTX-class NVIDIA pod checkout.
- Build the OptiX backend from the checked-out commit before commands.
- Export RTDL_SOURCE_COMMIT or keep .rtdl_source_commit populated.
- Copy the whole report directory back before stopping or terminating the pod.
- Do not use this manifest to authorize public wording without a later artifact-intake and 2+ AI review.

## Rows

| App | Path | Phase | Skip validation | Timing floor | Output | Command |
| --- | --- | --- | --- | ---: | --- | --- |

## Boundary

Goal1062 prepares one batched rerun plan for any remaining blocked NVIDIA RTX wording rows. It does not run cloud, create resources, authorize release, or authorize public speedup wording.

