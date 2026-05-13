# Goal1904 - Gemini Review of Goal1903 Batch Packet

**Date:** 2026-05-13
**Reviewer:** Gemini CLI

## Review Questions and Answers

### 1. Does Goal1903 correctly avoid claiming release evidence from the local GTX-only dry-run?
Yes, Goal1903 explicitly prevents claiming release evidence from local GTX-only dry runs. The `docs/reports/goal1903_v2_partner_pod_batch_packet_2026-05-13.md` states that `REQUIRE_RTX=0` is for local mechanics-only and not for accepted RTX evidence. The `scripts/goal1903_v2_partner_pod_batch_runner.sh` script includes a check for `REQUIRE_RTX=1` and the GPU name to ensure an RTX card is present for accepted pod batch runs. Furthermore, the embedded Python script validates `claim_boundaries` to ensure specific release-related flags are `False`.

### 2. Is the RTX pod command clear enough to run without extra interpretation?
Yes, the RTX pod command provided in `docs/reports/goal1903_v2_partner_pod_batch_packet_2026-05-13.md` is clear and straightforward. It includes all necessary environment variables (`OUT_DIR`, `OPTIX_PREFIX`) directly in the bash command, making it easy to execute.

### 3. Does the batch runner collect the right heads for the current v2.0 gate: fixed-radius, segment/polygon, and road-hazard?
Yes, the batch runner is designed to collect data for all three specified heads. The `docs/reports/goal1903_v2_partner_pod_batch_packet_2026-05-13.md` explicitly lists fixed-radius, segment/polygon, and road-hazard as the rows it can run. The `scripts/goal1903_v2_partner_pod_batch_runner.sh` confirms this by including `RUN_FIXED_RADIUS`, `RUN_SEGMENT_POLYGON`, and `RUN_ROAD_HAZARD` flags, and calling the respective performance scripts for each.

### 4. Does Goal1899 now correctly direct the next hardware step to Goal1903 rather than the narrower Goal1897-only packet?
Yes, `docs/reports/goal1899_v2_strict_birth_gate_current_board_2026-05-13.md` explicitly directs the next hardware step to Goal1903. Under the "Broad RT-core speedup" section and the "Immediate Next Hardware Step" section, the document clearly instructs to "Run Goal1903 on RTX pod, including the road-hazard head, and review results," and provides the specific command for Goal1903.

### 5. Are any public claims still too broad, especially around broad RT-core speedup, whole-app acceleration, true zero-copy, arbitrary PyTorch/CuPy acceleration, or package-install support?
No, the public claims are appropriately constrained. Both `docs/reports/goal1903_v2_partner_pod_batch_packet_2026-05-13.md` (in its "Boundary" section and Python script validation) and `docs/reports/goal1899_v2_strict_birth_gate_current_board_2026-05-13.md` explicitly state that these broader claims are not yet authorized, are still blocked, or require further review. The system is designed to prevent premature authorization of these claims.

## Verdict

`accept`
