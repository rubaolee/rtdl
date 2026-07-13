# Goal4971 Exact LSI Device Columns Large Representative Status

Date: 2026-07-04

## Status

`blocked_by_pod_port_unavailable_after_goal_defined`

## What Was Done

1. Goal4971 was defined in:

   ```text
   history/internal_docs/goal4971_exact_lsi_device_columns_large_representative_gate_2026-07-04.md
   ```

2. The existing Goal4964 fact pattern was checked:

   - exact LSI pair-id device columns already exist
   - public sample result was correctness pass but performance no-go
   - the valid next step is a large representative top4 gate, not a duplicate ABI implementation

3. The top4 matrix runner was extended so future matrix runs include:

   ```text
   rtdl_binary_exact_lsi_device_columns
   ```

   using:

   ```bash
   --device-columnar \
   --validate-device-order \
   --compiled-group \
   --exact-lsi-device-columns
   ```

4. Local syntax check passed:

   ```bash
   py -m py_compile \
     scripts/goal4970_stage_top4_arcgis_cdb.py \
     scripts/goal4970_run_section57_top4_matrix.py
   ```

## Intended POD Command

The direct command to run on the prepared POD workspace is:

```bash
cd /root/rtdl_goal4955
. .venv/bin/activate
export PYTHONPATH=src:.
export RTDL_OPTIX_LIB=/root/rtdl_goal4955/build/librtdl_optix.so
export RTDL_OPTIX_LIBRARY=/root/rtdl_goal4955/build/librtdl_optix.so
export PATH=/usr/local/cuda/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin

python Paper-reproduction-apps/rayjoin-paper/section57_overlay_columnar_binary.py \
  --left /root/rtdl_goal4955/Paper-reproduction-apps/rayjoin-paper/_data/goal4970_top4_arcgis/top4_county.cdb \
  --right /root/rtdl_goal4955/Paper-reproduction-apps/rayjoin-paper/_data/goal4970_top4_arcgis/top4_zipcode.cdb \
  --summary /root/rtdl_goal4955/Paper-reproduction-apps/rayjoin-paper/_runs/goal4970_top4_matrix/rtdl_binary_exact_lsi_device_columns_section57_overlay.json \
  --pair-name top4_county_zipcode_arcgis_same_source \
  --cache-dir /root/rtdl_goal4955/Paper-reproduction-apps/rayjoin-paper/_runs/goal4970_top4_matrix/rtdl_packed_cache \
  --device-columnar \
  --validate-device-order \
  --compiled-group \
  --exact-lsi-device-columns
```

Expected comparison baseline from Goal4970:

```text
normal fresh binary writer_free_hot_sec = 7.757310301065445
normal fresh binary lsi_public_rows_sec = 4.066678975708783
```

Goal4971 must compare the exact-LSI device-column route against those two
numbers on the same top4 input.

## Blocker

The POD endpoint became unavailable while starting the run:

```text
ssh root@213.173.108.15 -p 10689 -i ~/.ssh/id_ed25519_rtdl_codex_current_pod
banner exchange: Connection to UNKNOWN port -1: Connection refused
```

Network probe:

```text
PingSucceeded: true
TcpTestSucceeded: false
```

So the host responds to ICMP but the SSH/TCP service on port `10689` is closed.
This is an environment blocker, not an RTDL code failure.

## Exit Criteria When POD Returns

Goal4971 closes only after:

1. The exact-LSI device-column route runs on the top4 input.
2. It reports the same semantic gates as Goal4970:

   ```text
   lsi_row_count = 428322
   xsect_sorted_counts = {side0: 428322, side1: 428322}
   vertex positive counts = {side0_in_side1: 812721, side1_in_side0: 4527305}
   device sort validation = true for both maps
   ```

3. It compares:

   ```text
   exact_lsi_device_columns writer_free_hot_sec
   exact_lsi_device_columns LSI phase
   exact_lsi_device_columns device-to-NumPy copy phase
   ```

   against the normal fresh binary baseline.

4. Exit label is one of:

   - `exact_lsi_device_columns_large_input_speedup_confirmed`
   - `exact_lsi_device_columns_large_input_no_go_confirmed`
   - `blocked_by_runtime_or_correctness_failure`

If no-go is confirmed again, the next attack is exact LSI compute/predicate/traversal,
not resident row wrappers.
