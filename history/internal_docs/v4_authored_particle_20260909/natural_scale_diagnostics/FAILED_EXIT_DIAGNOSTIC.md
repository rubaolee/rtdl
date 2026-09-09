# Retained Particle v1 Exit-Boundary Failure

Date: 2026-09-09 (America/New_York)

Status: `RETAINED_PRE_TIMING_INPUT_CONSTRUCTION_FAILURE`

## What Failed

The first variable-scale public-PyOptiX dry run used 1,000,000 rows from the
20,000,000-row v1 transition ensemble.  The worker failed during its untimed
warmup, before it could append any timed sample or performance result.  The
device control tuple was:

```text
(validated_row_count=999955, first_error=10028, error_code=2, status=1)
```

`error_code=2` is `RTDL_PARTICLE_ERROR_NON_STRICT_INTERIOR` in
`experiments/v4_paper_apps_pyoptix/particle_device.cu`.  The full batch had 45
rejected rows.  This was not a miss and was not an A/C performance result.

The defect was in the v1 input constructor.  It proved that each origin was
strictly inside its selected tetrahedron, but did not prove that the ray's exit
point was strictly inside the selected exit triangle.  A valid tetrahedral
origin can still generate an edge/vertex exit for a fixed ray direction.

## Bound Identities

- First observed worker source commit:
  `a8468a981948f7da40d38d0b97f34816280b3a26`
- First observed worker tree:
  `479c1aa7c21dc7ec9819153d677b113efb4400bb`
- Worker blob, unchanged in the retained exact replay:
  `1f7877b7788fa86c9d1e824c047d90561bbdf900`
- Exact replay source commit:
  `63c35f7204d5ba44d9f221398b1765f780893340`
- Exact replay source tree:
  `6d01f3f99d17f8cb82a8f863027e888914d2f172`
- v1 data manifest SHA-256:
  `4044231adc2d544c11bd534e2245a8a77cb0724c9a2495431a723bb9bccd22ba`
- Original VTU SHA-256:
  `b6be6c692256e73ea9f93d71dc81ad99478b49ec3866a9ab0109da35f72c57b8`
- Base Particle manifest SHA-256:
  `c6678099ecff9581726781a765213d5b0890f20ada70561b09dd6dd94a4009af`
- PyOptiX PTX SHA-256:
  `d563ac854f1c823a6f4471f3644b23d96f9e3500865718083fd8f5fec12011bc`

The source commit differs between first observation and exact replay because
the generator was subsequently repaired.  The worker blob is byte-identical,
the failed v1 manifest is identical, and the replay reproduced the exact
device control tuple.

## Retained Bytes

| File | SHA-256 | Meaning |
| --- | --- | --- |
| `FAILED_EXIT_DATASET_MANIFEST.json` | `4044231adc2d544c11bd534e2245a8a77cb0724c9a2495431a723bb9bccd22ba` | Complete v1 input manifest |
| `FAILED_EXIT_REPLAY.stdout` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` | Empty stdout; no result row was emitted |
| `FAILED_EXIT_REPLAY.stderr` | `7788f73ab263a6e0217c3fcaa957242b2c83572ee7f2174b33487d9eae7a1b59` | Complete replay traceback |
| `FAILED_EXIT_REPLAY.exit` | `4355a46b19d348dc2f57c046f8ef63d4538ebb936000f3c9ee954a27460dd865` | Nonzero process exit (`1`) |

## Successor Rule

The successor constructor must validate both origin-cell barycentrics and exit
triangle barycentrics, deterministically resample invalid candidates, preserve
the requested row count, and continue to use the unchanged device-side strict
check.  This failure may not be discarded, relabeled as a performance sample,
or pooled with any successor transaction.
