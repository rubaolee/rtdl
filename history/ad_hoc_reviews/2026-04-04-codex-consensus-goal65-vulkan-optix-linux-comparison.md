# Codex Consensus: Goal 65 Vulkan OptiX Linux Comparison

Date: 2026-04-04

Consensus:

- Codex: `APPROVE`
- Gemini 3.1 Pro: `APPROVE`

Accepted result:

- Goal 65 is complete as a Linux validation/comparison round.
- Vulkan was successfully brought onto `192.168.1.20` and compared directly
  against OptiX.
- The result is intentionally negative for Vulkan acceptance:
  - Vulkan is not yet parity-clean across the accepted bounded comparison
    surface.
  - OptiX remains the accepted GPU backend.

Most important accepted conclusion:

- On the workloads where both GPU backends are parity-clean, OptiX warm runtime
  is consistently better than Vulkan warm runtime on this GTX 1070 host.
