# Goal3595 - RayJoin Public-CDB Long-Repeat Stability Packet

Date: 2026-06-06

Status: internal evidence only

## Purpose

Goal3595 reruns the Goal3593 bounded public-CDB same-contract probe with a longer repeat count so that at least one partner baseline row accumulates near ten seconds of measured hot-loop time. This is still a bounded diagnostic packet, not a RayJoin reproduction or release claim.

The runner is unchanged:

- `scripts/goal3593_rayjoin_public_cdb_cupy_same_contract_probe.py`

Artifact:

- `docs/reports/goal3595_rayjoin_public_cdb_repeat200_a5000/summary.json`

## Pod Configuration

GPU:

- NVIDIA RTX A5000

Pod commit:

- `ca5ae21260e28a0a011e242aa7cbe97d35d8690c`

Command shape:

```bash
cd /root/rtdl_goal3556_current
export PYTHONPATH=src:.
export RTDL_OPTIX_LIBRARY=/root/rtdl_goal3556_current/build/librtdl_optix.so
export RTDL_OPTIX_LIB=/root/rtdl_goal3556_current/build/librtdl_optix.so
export RTDL_EMBREE_LIBRARY=/root/rtdl_goal3556_current/build/librtdl_embree.so
python3 scripts/goal3593_rayjoin_public_cdb_cupy_same_contract_probe.py \
  --data-dir /root/rtdl_goal3293/data/rayjoin_public_cdb \
  --cases all \
  --repeat 200 \
  --warmup 5 \
  --output /tmp/goal3595_public_cdb_repeat200_summary.json
```

## Results

| Case | CuPy CUDA-Core Median Sec | CuPy Total Sec | RTDL/OptiX Median Sec | RTDL/OptiX Total Sec | RTDL/OptiX vs CuPy | Count |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `pip_county512` | 0.000437917 | 0.087361970 | 0.002150856 | 0.438148404 | 0.204x | 1417 |
| `lsi_county512_soil512` | 0.021059401 | 4.220671882 | 0.000185231 | 0.037593882 | 113.693x | 269 |
| `overlay_county512_soil512` | 0.049443172 | 9.937864013 | 0.000538940 | 0.275021487 | 91.742x | 174 |

Summary:

- All counts matched.
- Minimum RTDL/OptiX-vs-CuPy ratio: `0.2036x`.
- Geomean RTDL/OptiX-vs-CuPy ratio: `12.8536x`.
- The overlay CuPy baseline accumulated `9.9379` seconds of measured hot-loop time, satisfying the intended longer-row stability purpose for this packet.
- The artifact was regenerated from a fresh clean pod checkout; its recorded `git_status_short` is empty.

## Interpretation

Goal3595 confirms the Goal3593 direction under a much longer repeat count:

- PIP remains CuPy-favorable at this bounded public-CDB size.
- LSI remains strongly RTDL/OptiX-favorable.
- Overlay active-pair dependency count remains strongly RTDL/OptiX-favorable.

The stronger LSI/overlay medians are expected because the longer run reduces one-off jitter and shows the prepared RTDL/OptiX hot routes staying stable while dense CuPy all-pairs segment/polygon work remains comparatively heavy.

## Boundary

Goal3595 does not authorize:

- a RayJoin paper reproduction claim,
- a broad RT-core speedup claim,
- a whole-app speedup claim,
- a release claim,
- a true zero-copy claim,
- automatic partner/backend selection.

The useful conclusion is narrower: for bounded public CDB RayJoin-style contracts, users should make the route choice visible. Current v2.8 evidence recommends CuPy for this PIP count and RTDL/OptiX for this LSI count and overlay active-pair dependency count.
