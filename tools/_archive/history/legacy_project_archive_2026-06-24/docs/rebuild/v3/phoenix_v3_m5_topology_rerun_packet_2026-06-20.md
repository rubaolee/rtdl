# Phoenix V3 M5 Topology Rerun Packet

Status: ready for external review, not executed, 2026-06-20.

This packet targets Goal4392 M5: generic point-location/topology streams for
RayJoin-style workloads. It is not release evidence and does not authorize
public speedup wording.

In short: this packet does not authorize public speedup wording.

```text
release_authorized: false
public_speedup_claim_authorized: false
Phoenix M7-qualified release rows: 0
```

Machine-readable packet:

```text
docs/rebuild/v3/phoenix_v3_m5_topology_rerun_packet_2026-06-20.json
```

## Why M5

M4 proved grouped/fused continuation can produce internal serious-scale
evidence across DBSCAN and RayDB. M5 asks a different V3 language question:

```text
Can RTDL express RayJoin-style point-location and topology rows as generic
topology streams, with OptiX and Embree under the same contract?
```

M5 is not allowed to become a loose RayJoin speedup story. It must keep author
code, RTDL OptiX, RTDL Embree, same-contract output, topology scope, and public
claim boundaries separate.

## Known Blocker

Current pod preflight did not find the RayJoin author `query_exec` binary. Full
M5 author-code completion therefore remains blocked unless that binary appears
on the pod before execution.

If `query_exec` is missing, this packet still runs RTDL same-contract internal
evidence, but it must classify M5 author-code completion as blocked. Missing
`query_exec` is not a V3 topology-code failure.

## Remote Target

```text
ssh root@213.173.108.14 -p 11592 -i C:\Users\Lestat\.ssh\id_ed25519_rtdl_codex_current_pod
cd /root/rtdl_v3_rebuild_20260620/current
export ART=/root/rtdl_v3_rebuild_20260620/artifacts/phoenix_v3_m5_topology_20260620
export PY=/root/rtdl_v3_rebuild_20260620/.venv/bin/python
```

## Command Batch

```bash
mkdir -p "$ART"
nvidia-smi > "$ART/nvidia-smi.txt"
cat VERSION > "$ART/source_version.txt"
sha256sum \
  VERSION \
  src/rtdsl/v3_0_m5_topology_pilots.py \
  scripts/goal4373_rayjoin_cdb_point_location_compare.py \
  scripts/v3_0_m33_rayjoin_overlay_active_count_same_contract.py \
  scripts/v3_optix_hardware_gate.py \
  scripts/v3_phoenix_m5_topology_intake.py \
  > "$ART/source_manifest.sha256"
PYTHONPATH=src:. "$PY" scripts/v3_gpu_python_env_gate.py --json-out "$ART/gpu_env_gate.json"
PYTHONPATH=src:. "$PY" scripts/v3_optix_hardware_gate.py \
  --require-rt-hardware \
  --json-out "$ART/optix_hardware_gate.json"

make build-embree build-optix OPTIX_PREFIX=/workspace/vendor/optix-dev-8.0.0

PYTHONPATH=src:. "$PY" -c \
  "import json, rtdsl as rt; print(json.dumps(rt.validate_m5_topology_pilots(), sort_keys=True))" \
  > "$ART/m5_local_graph_gate.json"

: > "$ART/rayjoin_query_exec_path.txt"
for candidate in \
  /workspace/rayjoin/build/query_exec \
  /workspace/RayJoin/build/query_exec \
  /workspace/rayjoin/build/src/query_exec \
  /workspace/RayJoin/build/src/query_exec \
  /root/rayjoin/build/query_exec \
  /root/RayJoin/build/query_exec; do
  if test -x "$candidate"; then
    printf "%s\n" "$candidate" > "$ART/rayjoin_query_exec_path.txt"
    break
  fi
done
if ! test -s "$ART/rayjoin_query_exec_path.txt" && test -d /workspace; then
  timeout 20s find /workspace -maxdepth 6 -type f -name query_exec -print -quit \
    > "$ART/rayjoin_query_exec_path.txt" 2>/dev/null || true
fi
if ! test -s "$ART/rayjoin_query_exec_path.txt" && test -d /root; then
  timeout 20s find /root -maxdepth 5 \
    -path /root/rtdl_v3_rebuild_20260620/artifacts -prune \
    -o -type f -name query_exec -print -quit \
    > "$ART/rayjoin_query_exec_path.txt" 2>/dev/null || true
fi
if test -s "$ART/rayjoin_query_exec_path.txt"; then
  echo present > "$ART/rayjoin_query_exec_status.txt"
else
  echo missing > "$ART/rayjoin_query_exec_status.txt"
fi

PYTHONPATH=src:. "$PY" scripts/goal4373_rayjoin_cdb_point_location_compare.py \
  --base-cdb data/rayjoin_public_cdb/br_county.cdb \
  --query-cdb "$ART/goal4373_query_points_parity_filtered_100k.cdb" \
  --generate-query-cdb \
  --filter-backend-parity \
  --parity-filter-oversample 2048 \
  --point-count 100000 \
  --seed 4373 \
  --rtdl-warmups 3 \
  --rtdl-repeats 1000 \
  --optix-repeats 1000 \
  --embree-repeats 1000 \
  --correctness-sample 100000 \
  --output-dir "$ART/m5_pip_point_location_parity_filtered_100k"

PYTHONPATH=src:. "$PY" scripts/v3_0_m33_rayjoin_overlay_active_count_same_contract.py \
  --left-cdb data/rayjoin_public_cdb/br_county_start256_count512.cdb \
  --right-cdb data/rayjoin_public_cdb/br_soil_start256_count512.cdb \
  --warmup 2 \
  --repeat 25 \
  --output "$ART/m5_overlay_active_count_same_contract.json"

PYTHONPATH=src:. "$PY" scripts/v3_phoenix_m5_topology_intake.py \
  --artifact-dir "$ART" \
  --json-out "$ART/m5_topology_intake_summary.json" \
  --md-out "$ART/m5_topology_intake_summary.md" \
  --pretty
```

## Acceptance

This packet is successful only if:

- `source_manifest.sha256` records hashes for `VERSION` and the critical M5
  scripts;
- the OptiX/RT hardware gate passes before benchmark rows run;
- the Goal4397 M5 local graph gate passes;
- `query_exec` preflight status is recorded as either `present` or `missing`;
- RTDL PIP point-location parity-filtered 100k evidence records OptiX and
  Embree under the same point-location contract;
- RTDL PIP query generation records a backend-parity filter that rejects
  exact-row tie points before timing;
- RTDL PIP OptiX and Embree repeat counts are equal at 1000;
- RTDL overlay active-count evidence records OptiX and Embree under
  `overlay_active_pair_dependency_count`;
- `m5_topology_intake_summary.json` records a top-level M5 author-code
  comparison status;
- if `query_exec` is missing, M5 author-code completion is marked blocked;
- full polygon overlay, RayJoin paper reproduction, public speedup, and release
  authorization remain false.

## Goal-Level Decision Audit

Decision: make M5 topology the next Phoenix P0 packet after M4.

1. Was I foolish?

   No. This follows Goal4392 order and targets the next generic language gap.

2. What action would make it foolish?

   Treating existing RayJoin ratios as full M5, or ignoring the missing author
   binary, would be foolish.

3. Was there another path?

   Yes. Phoenix could jump to Barnes-Hut/M6 or package repair. M5 is chosen
   because topology streams are the next formal gate and RayJoin is a central
   user-facing benchmark family.

4. Can I now try a different path that actually solves the problem?

   Yes. This packet either produces internal M5 topology evidence or cleanly
   records the author-code blocker, without inventing release success.
